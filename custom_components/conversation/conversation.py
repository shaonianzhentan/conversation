import logging, aiohttp, re
from homeassistant.helpers import template, intent
from .semantic import Semantic

_LOGGER = logging.getLogger(__name__)
VERSION = "2022.6.12"

class Conversation():

    def __init__(self, hass):
        self.hass = hass
        local = hass.config.path("custom_components/conversation/www")
        LOCAL_PATH = '/www-conversation'
        hass.http.register_static_path(LOCAL_PATH, local, False)
        hass.components.frontend.add_extra_js_url(hass, f'{LOCAL_PATH}/wake-up.js?v={VERSION}')
        self.update(VERSION, '')
        self.semantic = Semantic(hass)

    # Voice service processing
    async def async_process(self, text):
        self.fire_text(text)
        # update cache data
        await self.semantic.update(text)
        print(self.semantic.entities)
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
                    # customze reply
                    reply = result.get('reply')
                    if reply is not None:
                        for key in slots:
                            set_var = '{% set ' + key + '="' + slots[key] + '" %}'
                            reply = set_var + reply
                        return self.intent_result(self.template(reply))
                    # default reply
                    return self.intent_result(f'执行脚本：{entity_id}')
            elif isinstance(result, list):
                result_message = []
                for item in result:
                    entity_id = item.get('entity_id')
                    entity_name = item.get('entity_name')
                    domain = item.get('domain')
                    entity_state = item.get('state', '')
                    result_message.append(f'{domain}{entity_name}：{entity_state}')
                return self.intent_result('\n'.join(result_message))
        
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
            "icon": "mdi:account-voice",
            "friendly_name": "语音助手",
            "reply": reply
        })

    # Parsing template
    def template(self, message):
        tpl = template.Template(message, self.hass)
        return tpl.async_render(None)

    # 返回意图结果
    def intent_result(self, message, extra_data = None):
        intent_result = intent.IntentResponse()
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