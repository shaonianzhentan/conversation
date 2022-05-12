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
        self.update(VERSION)
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
        # Semantic analysis
        result = await self.semantic.parser(text)
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
                return self.intent_result('、'.join(cmd_arr))

        # Call chat robot
        message = await self.chat_robot(text)
        return self.intent_result(message)

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

    def update(self, text):
        self.hass.states.async_set('conversation.voice', text, {
            "icon": "mdi:account-voice",
            "friendly_name": "语音助手"
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