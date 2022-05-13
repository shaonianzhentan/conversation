import logging, aiohttp, re
from homeassistant.helpers import template, intent
from .semantic import Semantic

_LOGGER = logging.getLogger(__name__)
VERSION = "1.7"

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
        # Exact match
        result = await self.semantic.find_entity_name(text)
        if result is not None:
            entity_id = result.get('entity_id')
            entity_name = result.get('entity_name')
            domain = result.get('domain')
            if domain == 'script':
                self.call_service(entity_id)
                return self.intent_result(f'执行脚本：{entity_id}')
            else:
                state = self.hass.states.get(entity_id)
                return self.intent_result(f'{entity_name}的状态：{state.state}')

        # Query entity first
        entity = await self.semantic.find_entity(text)
        print(entity)
        
        # trigger match
        service = await self.semantic.trigger_match(text, entity)
        if service is not None:
            domain = entity['domain']
            entity_id = entity['entity_id']
            entity_name = entity['entity_name']
            self.call_service_entity(service, entity_id)
            return self.intent_result(f'正在激活{domain}{entity_name}')

        # activate match
        service = await self.semantic.activate_match(text, entity)
        if service is not None:
            domain = entity['domain']
            entity_id = entity['entity_id']
            entity_name = entity['entity_name']
            self.call_service_entity(service, entity_id)
            return self.intent_result(f'正在触发{domain}{entity_name}')

        # light
        result = await self.light_match(text, entity)
        if result is not None:
            return self.intent_result(result)

        # media_player
        result = await self.media_player_match(text, entity)
        if result is not None:
            return self.intent_result(result)

        # climate
        result = await self.climate_match(text, entity)
        if result is not None:
            return self.intent_result(result)
        
        # Semantic analysis
        result = await self.semantic.turn_match(text, entity)
        slots = result['slots']
        if len(slots) > 0:
            cmd_arr = []
            for slot in slots:
                entity_id = slot.get('entity_id')
                cmd_text = slot.get('cmd_text')
                service =  slot["cmd"]
                if entity_id is None:
                    for entity in result.get('entities'):
                        domain = entity["domain"]
                        entity_id = entity['entity_id']
                        entity_name = entity['entity_name']

                        service_name = f'{domain}.{service}'
                        if self.hass.services.has_service(domain, service):
                            self.call_service_entity(service_name, entity_id)
                            cmd_arr.append(f'{cmd_text}{entity_name}')
                else:
                    domain = slot["domain"]
                    entity_name = slot.get('entity_name')

                    service_name = f'{domain}.{service}'
                    if self.hass.services.has_service(domain, service):
                        self.call_service_entity(service_name, entity_id)
                        cmd_arr.append(f'{cmd_text}{entity_name}')

            if len(slots) > 0 and len(cmd_arr) > 0:
                return self.intent_result(f"正在{'、'.join(cmd_arr)}")

        # Call chat robot
        message = await self.chat_robot(text)
        return self.intent_result(message)
    
    async def light_match(self, text, entity):
        if entity is not None:            
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
                    return f'{entity_name}的亮度正在设为{brightness}%'

    async def media_player_match(self, text, entity):
        if entity is not None:
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
                        return f'{entity_name}音量正在调整为{volume_level}%'
    
    async def climate_match(self, text, entity):
        if entity is not None:
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
                    return f'{entity_name}运行模式设为{hvac_mode}'

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
                        return f'{entity_name}温度调整为{value}摄氏度'

    # Remove the front and back punctuation marks
    def trim_char(self, text):
        return text.strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')

    # Chat robot
    async def chat_robot(self, text):
        message = "对不起，我不明白"
        try:
            async with aiohttp.request('GET','https://api.ownthink.com/bot?appid=xiaosi&spoken=' + text) as r:
                res = await r.json(content_type=None)
                _LOGGER.debug(res)
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