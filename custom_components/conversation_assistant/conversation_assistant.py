import logging, aiohttp, re
from homeassistant.helpers import template, intent
from .semantic import Semantic
from .manifest import manifest

_LOGGER = logging.getLogger(__name__)

# 天气状态翻译
WEATHER_STATE = {
    'clear-night': '晴朗的夜晚',
    'cloudy': '多云',
    'exceptional': '异常',
    'fog': '雾',
    'hail': '冰雹',
    'lightning': '打雷闪电',
    'lightning-rainy': '雷阵雨',
    'partlycloudy': '局部多云',
    'pouring': '倾盆大雨',
    'rainy': '雨',
    'snowy': '雪',
    'snowy-rainy': '雨夹雪',
    'sunny': '晴',
    'windy': '有风',
    'windy-variant': '很大风'
}

class ConversationAssistant():

    def __init__(self, hass, recognize, entry_id):
        self.id = entry_id
        self.hass = hass
        local = hass.config.path("custom_components/conversation_assistant/www")
        LOCAL_PATH = '/www-conversation'
        hass.http.register_static_path(LOCAL_PATH, local, False)
        hass.components.frontend.add_extra_js_url(hass, f'{LOCAL_PATH}/wake-up.js?v={manifest.version}')
        self.update(manifest.version, '')
        self.semantic = Semantic(hass)
        self.recognize = recognize

    # Voice service processing
    async def async_process(self, text):
        # update cache data
        result = await self.semantic.update(text)
        if result is not None:
            if result[0] == 0:
                return self.intent_result(self.template('{% for state in states.' + result[1]+ ''' -%}【{{ state.name }} - {{ state.state }}】
{% endfor %} '''))
        # Exact match
        result = await self.semantic.find_entity_name(text)
        if result is not None:
            if isinstance(result, dict):
                entity_id = result.get('entity_id')
                entity_name = result.get('entity_name')
                domain = result.get('domain')
                if domain == 'script':
                    # reg match
                    slots = result.get('slots', {})
                    self.call_service(entity_id, slots)
                    vars = []
                    for key in slots:
                        vars.append('{% set ' + key + '="' + slots[key] + '" %}')
                    var_str = ''.join(vars)

                    # 额外数据
                    extra_data = result.get('extra_data')
                    if extra_data is not None:
                        if isinstance(extra_data, dict):

                            url = extra_data.get('url')
                            if url is not None:
                                extra_data['url'] = self.template(var_str + url).strip()

                            picurl = extra_data.get('picurl')
                            if picurl is not None:
                                extra_data['picurl'] = self.template(var_str + picurl).strip()

                    # customze reply
                    reply = result.get('reply')
                    if reply is not None:
                        return self.intent_result(self.template(var_str + reply).strip(), extra_data)
                    # default reply
                    return self.intent_result(f'执行脚本：{entity_id}', extra_data)
            elif isinstance(result, list):
                result_message = []
                for item in result:
                    entity_id = item.get('entity_id')
                    entity_name = item.get('entity_name')
                    domain = item.get('domain')
                    entity_state = item.get('state', '')

                    if domain == 'weather' and entity_state != 'unavailable':
                        ''' 天气 '''
                        state = self.hass.states.get(entity_id)
                        attributes = state.attributes
                        unit = attributes.get('temperature_unit')
                        result_message.append(f'今天天气{WEATHER_STATE.get(state.state, state.state)}，温度{attributes.get("temperature")} {unit}，湿度{attributes.get("humidity")} %')
                        forecast = attributes.get('forecast', [])
                        for index, item in enumerate(forecast):
                            date = item['datetime']
                            if index == 0:
                                date = '明天'
                            elif index == 1:
                                date = '后天'
                            else:
                                date = date[:10]

                            condition = item['condition']
                            temperature = item['temperature']
                            templow = item['templow']
                            result_message.append(f'{date}天气{WEATHER_STATE.get(condition, condition)}，最高温度{temperature} {unit}，最低温度{templow} {unit}')
                    elif ['input_button', 'button'].count(domain) > 0 and entity_name == text:
                        # 完全匹配时点击按钮
                        self.call_service_entity(f'{domain}.press', entity_id)
                        return self.intent_result(f'点击{entity_name}按钮')
                    elif domain == 'calendar' and entity_name == text:
                        ''' 日历 '''
                        state = self.hass.states.get(entity_id)
                        attributes = state.attributes
                        message = attributes.get('message')
                        if message is not None:
                            description = attributes.get('description')
                            start_time = attributes.get('start_time')
                            end_time = attributes.get('end_time')
                            result_message.append(f'事件：{message}；')
                            result_message.append(f'开始时间：{start_time}；')
                            result_message.append(f'结束时间：{end_time}；')
                            result_message.append(f'描述：{description}；')
                        else:
                            result_message.append('近期没有需要提醒的事件')
                        break
                    else:
                        result_message.append(f'{domain}{entity_name}：{entity_state} {item.get("unit")}')

                return self.intent_result('\r\n'.join(result_message))

        # trigger match
        result = await self.trigger_match(text)
        if result is not None:
            return self.intent_result(result)

        # activate match
        result = await self.activate_match(text)
        if result is not None:
            return self.intent_result(result)

        # light
        result = await self.light_match(text)
        if result is not None:
            return self.intent_result(result)

        # media_player
        result = await self.media_player_match(text)
        if result is not None:
            return self.intent_result(result)

        # climate
        result = await self.climate_match(text)
        if result is not None:
            return self.intent_result(result)
        
        result = await self.turn_match(text)
        if result is not None:
            return self.intent_result(result)

        # 微信位置匹配
        result = await self.wechat_match(text)
        if result is not None:
            return self.intent_result(result)

        # Call chat robot
        message = await self.chat_robot(text)
        return self.intent_result(message)

    async def activate_match(self, text):
        entities = self.semantic.entities
        if len(entities) > 0:
            result = []
            for entity in entities:
                domain = entity.get('domain')
                if ['scene'].count(domain) > 0 and ('激活' in text or '启用' in text or '启动' in text):
                    entity_name = entity['entity_name']
                    self.call_service_entity('scene.turn_on', entity['entity_id'])
                    result.append(f'{domain}{entity_name}')
            if len(result) > 0:
                return f"正在激活{'、'.join(result)}"

    async def trigger_match(self, text):
        entities = self.semantic.entities
        if len(entities) > 0:
            result = []
            for entity in entities:
                domain = entity.get('domain')
                if ['automation', 'input_button', 'button', 'script', 'alarm_control_panel'].count(domain) > 0 and '触发' in text:
                    service = ''
                    if domain == 'automation':
                        service = 'trigger'
                    elif domain == 'script':
                        service = 'turn_on'
                    elif domain == 'alarm_control_panel':
                        service = 'alarm_trigger'
                    else:
                        service = 'press'

                    if service != '':
                        entity_id = entity['entity_id']
                        entity_name = entity['entity_name']
                        self.call_service_entity(f'{domain}.{service}', entity_id)
                        result.append(f'{domain}{entity_name}')
            if len(result) > 0:
                return f"正在触发{'、'.join(result)}"

    async def light_match(self, text):
        entities = self.semantic.entities
        if len(entities) > 0:
            result = []
            for entity in entities:
                domain = entity.get('domain')
                if domain == 'light':
                    entity_id = entity.get('entity_id')
                    entity_name = entity.get('entity_name')
                    brightness = 0
                    if '亮度' in text:
                        # check numbers
                        compileX = re.compile("\d+")
                        findX = compileX.findall(text)
                        if len(findX) > 0:
                            value = int(findX[0])
                            brightness = 100 if value > 100 else value
                    if '最亮' in text:
                        brightness = 100
                    if '最暗' in text:
                        brightness = 1

                    if brightness > 0:
                        self.call_service('light.turn_on', { 'entity_id': entity_id, 'brightness_pct': brightness })
                        result.append(f'{entity_name}的亮度正在设为{brightness}%')
                    else:
                        color_obj = {
                            '主题色': 'homeassistant',
                            '爱丽丝蓝': 'aliceblue',
                            '古董白': 'antiquewhite',
                            '浅绿色': 'aqua',
                            '碧绿': 'aquamarine',
                            '青白色': 'azure',
                            '米色': 'beige',
                            '陶坯黄': 'bisque',
                            '杏仁白': 'blanchedalmond',
                            '蓝色': 'blue',
                            '蓝紫色': 'blueviolet',
                            '棕色': 'brown',
                            '硬木褐': 'burlywood',
                            '军服蓝': 'cadetblue',
                            '查特酒绿': 'chartreuse',
                            '巧克力色': 'chocolate',
                            '珊瑚红': 'coral',
                            '矢车菊蓝': 'cornflowerblue',
                            '玉米穗黄': 'cornsilk',
                            '绯红': 'crimson',
                            '青色': 'cyan',
                            '深蓝色': 'darkblue',
                            '深青色': 'darkcyan',
                            '深金菊黄': 'darkgoldenrod',
                            '深灰色': 'darkgray',
                            '墨绿色': 'darkgreen',
                            '黑灰色': 'darkgrey',
                            '深卡其色': 'darkkhaki',
                            '深品红': 'darkmagenta',
                            '深橄榄绿': 'darkolivegreen',
                            '深橙': 'darkorange',
                            '深洋兰紫': 'darkorchid',
                            '深红色': 'darkred',
                            '深鲑红': 'darksalmon',
                            '深海藻绿': 'darkseagreen',
                            '深岩蓝': 'darkslateblue',
                            '深岩灰': 'darkslategray',
                            '暗岩灰': 'darkslategrey',
                            '深松石绿': 'darkturquoise',
                            '深紫罗兰': 'darkviolet',
                            '深粉色': 'deeppink',
                            '深天蓝': 'deepskyblue',
                            '昏灰': 'dimgray',
                            '浅灰': 'dimgrey',
                            '湖蓝': 'dodgerblue',
                            '火砖红': 'firebrick',
                            '花卉白': 'floralwhite',
                            '森林绿': 'forestgreen',
                            '紫红色': 'fuchsia',
                            '庚氏灰': 'gainsboro',
                            '幽灵白': 'ghostwhite',
                            '金色': 'gold',
                            '金菊黄': 'goldenrod',
                            '灰色': 'gray',
                            '绿色': 'green',
                            '黄绿色': 'greenyellow',
                            '灰白色': 'grey',
                            '蜜瓜绿': 'honeydew',
                            '艳粉': 'hotpink',
                            '印度红': 'indianred',
                            '靛蓝': 'indigo',
                            '象牙白': 'ivory',
                            '卡其色': 'khaki',
                            '薰衣草紫': 'lavender',
                            '薰衣草红': 'lavenderblush',
                            '草坪绿': 'lawngreen',
                            '柠檬绸黄': 'lemonchiffon',
                            '浅蓝': 'lightblue',
                            '浅珊瑚红': 'lightcoral',
                            '浅青': 'lightcyan',
                            '浅金菊黄': 'lightgoldenrodyellow',
                            '亮灰': 'lightgray',
                            '浅绿': 'lightgreen',
                            '浅灰': 'lightgrey',
                            '浅粉': 'lightpink',
                            '浅肉色': 'lightsalmon',
                            '浅海藻绿': 'lightseagreen',
                            '浅天蓝': 'lightskyblue',
                            '浅板岩灰色': 'lightslategray',
                            '浅板岩灰白色': 'lightslategrey',
                            '亮钢蓝': 'lightsteelblue',
                            '浅黄色': 'lightyellow',
                            '石灰': 'lime',
                            '石灰绿': 'limegreen',
                            '亚麻布': 'linen',
                            '洋红': 'magenta',
                            '褐红色': 'maroon',
                            #'颜色': 'mediumaquamarine',
                            #'颜色': 'mediumblue',
                            #'颜色': 'mediumorchid',
                            #'颜色': 'mediumpurple',
                            #'颜色': 'mediumseagreen',
                            #'颜色': 'mediumslateblue',
                            #'颜色': 'mediumspringgreen',
                            #'颜色': 'mediumturquoise',
                            #'颜色': 'mediumvioletred',
                            #'颜色': 'midnightblue',
                            #'颜色': 'mintcream',
                            #'颜色': 'mistyrose',
                            #'颜色': 'moccasin',
                            #'颜色': 'navajowhite',
                            #'颜色': 'navy',
                            #'颜色': 'navyblue',
                            #'颜色': 'oldlace',
                            '橄榄色': 'olive',
                            #'颜色': 'olivedrab',
                            '橙色': 'orange',
                            #'颜色': 'orangered',
                            #'颜色': 'orchid',
                            #'颜色': 'palegoldenrod',
                            #'颜色': 'palegreen',
                            #'颜色': 'paleturquoise',
                            #'颜色': 'palevioletred',
                            #'颜色': 'papayawhip',
                            #'颜色': 'peachpuff',
                            #'颜色': 'peru',
                            '粉色': 'pink',
                            #'颜色': 'plum',
                            #'颜色': 'powderblue',
                            '紫色': 'purple',
                            '红色': 'red',
                            #'颜色': 'rosybrown',
                            #'颜色': 'royalblue',
                            #'颜色': 'saddlebrown',
                            #'颜色': 'salmon',
                            #'颜色': 'sandybrown',
                            #'颜色': 'seagreen',
                            #'颜色': 'seashell',
                            #'颜色': 'sienna',
                            '银色': 'silver',
                            '天蓝色': 'skyblue',
                            #'颜色': 'slateblue',
                            #'颜色': 'slategray',
                            #'颜色': 'slategrey',
                            #'颜色': 'snow',
                            #'颜色': 'springgreen',
                            #'颜色': 'steelblue',
                            #'颜色': 'tan',
                            #'颜色': 'teal',
                            #'颜色': 'thistle',
                            #'颜色': 'tomato',
                            #'颜色': 'turquoise',
                            #'颜色': 'violet',
                            #'颜色': 'wheat',
                            '白色': 'white',
                            #'颜色': 'whitesmoke',
                            '黄色': 'yellow',
                            #'颜色': 'yellowgreen'
                        }
                        # 颜色
                        compileX = re.compile('|'.join(color_obj.keys()))
                        findX = compileX.findall(text)
                        if len(findX) > 0:
                            name = findX[0]
                            color_name = color_obj[name]
                            self.call_service('light.turn_on', { 'entity_id': entity_id, 'color_name': color_name })
                            result.append(f'{entity_name}的颜色调整为{color_name}{name}')

            if len(result) > 0:
                return '、'.join(result)

    async def media_player_match(self, text):
        entities = self.semantic.entities
        if len(entities) > 0:
            result = []
            for entity in entities:
                domain = entity.get('domain')
                if domain == 'media_player':
                    entity_id = entity.get('entity_id')
                    entity_name = entity.get('entity_name')
                    # prev or next
                    compileX = re.compile("(上|下)[一|1][曲|首|个]")
                    findX = compileX.findall(text)
                    if len(findX) > 0:
                        if findX[0] == '上':
                            self.call_service_entity('media_player.media_previous_track', entity_id)
                        else:
                            self.call_service_entity('media_player.media_next_track', entity_id)
                        return f'{entity_name}{findX[0]}一首'
                    # play or pause
                    if '播放' in text:
                        self.call_service_entity('media_player.media_play', entity_id)
                        return f'{entity_name}播放'
                    if '暂停' in text:
                        self.call_service_entity('media_player.media_pause', entity_id)
                        return f'{entity_name}暂停'

                    if ['声音小点', '小点声音', '小一点声音', '声音小一点', '音量减少', '减少音量', '音量调低', '调低音量'].count(text) == 1:
                        self.call_service_entity('media_player.volume_down', entity_id)
                        return f'{entity_name}音量减少'

                    if ['声音大点', '大点声音', '大一点声音', '声音大一点', '音量增加', '增加音量', '音量调高', '调高音量'].count(text) == 1:
                        self.call_service_entity('media_player.volume_up', entity_id)
                        return f'{entity_name}音量增加'

                    if '声音' in text or '音量' in text:
                        # check numbers
                        compileX = re.compile("\d+")
                        findX = compileX.findall(text)
                        if len(findX) > 0:
                            volume_level = int(findX[0])
                            if volume_level > 100:
                                volume_level = 100
                            self.call_service('media_player.volume_set', {
                                'entity_id': entity_id,
                                'volume_level': volume_level / 100.0
                            })
                            result.append(f'{entity_name}音量正在调整为{volume_level}%')
            if len(result) > 0:
                return '、'.join(result)

    async def climate_match(self, text):
        entities = self.semantic.entities
        if len(entities) > 0:
            result = []
            for entity in entities:
                domain = entity.get('domain')
                if domain == 'climate':
                    entity_id = entity.get('entity_id')
                    entity_name = entity.get('entity_name')
                    
                    hvac_mode = ''
                    if '自动模式' in text:
                        hvac_mode = 'auto'
                    if '制热模式' in text:
                        hvac_mode = 'heat'
                    if '制冷模式' in text:
                        hvac_mode = 'cool'
                    if '除湿模式' in text:
                        hvac_mode = 'dry'
                    if '仅送风模式' in text:
                        hvac_mode = 'fan_only'
                    
                    if hvac_mode != '':
                        self.call_service('climate.set_hvac_mode', {
                            'entity_id': entity_id,
                            'hvac_mode': hvac_mode
                        })
                        result.append(f'{entity_name}运行模式设为{hvac_mode}')
                        continue

                    # set temperature 
                    if '度' in text and ('设' in text or '调' in text):
                        compileX = re.compile("\d+")
                        findX = compileX.findall(text)
                        if len(findX) > 0:
                            value = int(findX[0])
                            # humidity
                            if '湿度' in text:
                                self.call_service('climate.set_humidity', {
                                    'entity_id': entity_id,
                                    'humidity': 100 if value > 100 else value
                                })
                                return f'{entity_name}湿度调整为{value}%'
                            # temperature
                            self.call_service('climate.set_temperature', {
                                'entity_id': entity_id,
                                'temperature': value
                            })
                            result.append(f'{entity_name}温度调整为{value}摄氏度')
                            continue
            if len(result) > 0:
                return '、'.join(result)


    async def turn_match(self, text):
        result = []
        turnOn_text = ''
        turnOff_text = ''
        matchTurnOn = self.semantic.parser_match(text, '打开|开启|开一下|开下')
        matchTurnOff = self.semantic.parser_match(text, '关闭|关掉|关上|关一下|关下')
        if matchTurnOn is not None and matchTurnOff is not None:
            if matchTurnOn[0] != '':
                turnOn_text = matchTurnOn[2]
            if matchTurnOff[0] != '':
                turnOff_text = matchTurnOff[2]

            if matchTurnOn[0] == '':
                turnOn_text = matchTurnOn[2].split(matchTurnOff[1])[0]
            if matchTurnOff[0] == '':
                turnOff_text = matchTurnOff[2].split(matchTurnOn[1])[0]
        elif matchTurnOn is not None:
            if matchTurnOn[0] != '':
                turnOn_text = matchTurnOn[0]
            if matchTurnOn[2] != '':
                turnOn_text = matchTurnOn[2]
        elif matchTurnOff is not None:
            if matchTurnOff[0] != '':
                turnOff_text = matchTurnOff[0]
            if matchTurnOff[2] != '':
                turnOff_text = matchTurnOff[2]
        # single device
        turnOn_entities = await self.semantic.find_entity_multiple(turnOn_text)
        if len(turnOn_entities) > 0:
            for entity in turnOn_entities:
                domain = entity.get('domain')
                entity_id = entity.get('entity_id')
                entity_name = entity.get('entity_name')
                service = 'turn_on'
                if domain == 'cover':
                    service = 'open_cover'
                elif domain == 'lock':
                    service = 'unlock'
                if self.hass.services.has_service(domain, service):
                    self.call_service_entity(f'{domain}.{service}', entity_id)
                    result.append(f'打开{domain}{entity_name}')
        
        turnOff_entities = await self.semantic.find_entity_multiple(turnOff_text)
        if len(turnOff_entities) > 0:
            for entity in turnOff_entities:
                domain = entity.get('domain')
                entity_id = entity.get('entity_id')
                entity_name = entity.get('entity_name')
                service = 'turn_off'
                if domain == 'cover':
                    service = 'close_cover'
                elif domain == 'lock':
                    service = 'lock'
                if self.hass.services.has_service(domain, service):
                    self.call_service_entity(f'{domain}.{service}', entity_id)
                    result.append(f'关闭{domain}{entity_name}')

        # in area
        area = await self.semantic.find_area(turnOn_text)
        if area is not None:
            entities = await self.semantic.findAll_entity(area)
            for entity in entities:
                domain = entity.get('domain')
                entity_id = entity.get('entity_id')
                entity_name = entity.get('entity_name')
                service = 'turn_on'
                if domain == 'cover':
                    service = 'open_cover'
                elif domain == 'lock':
                    service = 'unlock'
                if self.hass.services.has_service(domain, service):
                    self.call_service_entity(f'{domain}.{service}', entity_id)
                    result.append(f'打开{domain}{entity_name}')

        area = await self.semantic.find_area(turnOff_text)
        if area is not None:
            entities = await self.semantic.findAll_entity(area)
            for entity in entities:
                domain = entity.get('domain')
                entity_id = entity.get('entity_id')
                entity_name = entity.get('entity_name')
                service = 'turn_off'
                if domain == 'cover':
                    service = 'close_cover'
                elif domain == 'lock':
                    service = 'lock'
                if self.hass.services.has_service(domain, service):
                    self.call_service_entity(f'{domain}.{service}', entity_id)
                    result.append(f'关闭{domain}{entity_name}')

        if len(result) > 0:
            return '、'.join(result)

    async def wechat_match(self, text):
        compileX = re.compile("微信定位(\d+\.\d+),(\d+\.\d+)")
        findX = compileX.findall(text)
        if len(findX) > 0:
            location = findX[0]
            latitude = location[0]
            longitude = location[1]
            vars = '{% set location = { "latitude": ' + latitude + ', "longitude": ' + longitude + ' } %}'
            return self.template(vars + '''{% set state = closest(location.latitude,location.longitude, states) %}
距离最近的实体【{{ state.name }}】
距离【{{ state.name }}】{{ distance(location.latitude,location.longitude, state) | round(2) }}公里
距离【{{states.zone.home.name}}】{{ distance(location.latitude,location.longitude) | round(2) }}公里
【{{ state.name }}】距离【{{states.zone.home.name}}】{{ distance(state) | round(2) }}公里''')

    # Remove the front and back punctuation marks
    def trim_char(self, text):
        return text.strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')

    # Chat robot
    async def chat_robot(self, text):
        message = "对不起，我不明白"
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.request('GET','https://api.ownthink.com/bot?appid=xiaosi&spoken=' + text, timeout=timeout) as r:
                res = await r.json(content_type=None)
                message = res['data']['info']['text']
        except Exception as e:
            _LOGGER.debug(e)
        return message

    def update(self, text, reply):
        self.hass.states.async_set('conversation.voice', text, {
            'id': self.id,
            "icon": "mdi:account-voice",
            "friendly_name": "语音小助手",
            "reply": reply
        })

    # Parsing template
    def template(self, message):
        tpl = template.Template(message, self.hass)
        return tpl.async_render(None)

    # 返回意图结果
    def intent_result(self, message, extra_data = None):
        intent_result = intent.IntentResponse(self.hass.config.language)
        intent_result.async_set_speech(message, 'plain', extra_data)
        return intent_result

    # 异步调用服务
    def call_service(self, service, data={}):
        arr = service.split('.')
        self.hass.async_create_task(self.hass.services.async_call(arr[0], arr[1], data))

    def call_service_entity(self, service, entity_id):
        self.call_service(service, { 'entity_id': entity_id })

    def fire_text(self, text):
        hass = self.hass
        data = { 'text': text }
        hass.bus.fire('conversation', data)
        if hass.services.has_service('python_script', 'conversation'):
            self.call_service('python_script.conversation', data)