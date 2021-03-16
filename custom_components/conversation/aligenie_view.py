import logging, json
from homeassistant.components.http import HomeAssistantView

from .util import DOMAIN, ALIGENIE_API, matcher_query_state, find_entity

_LOGGER = logging.getLogger(__name__)

def build_text_message(message, is_session_end, open_mic):
    #固定响应格式
    RETURN_DATA = {
        "returnCode": "0",
        "returnErrorSolution": "",
        "returnMessage": "",
        "returnValue": {
            "resultType": "RESULT",
            "executeCode": "SUCCESS",
            "msgInfo": "",
            "gwCommands": [
                {
                    "commandDomain": "AliGenie.Speaker",
                    "commandName": "Speak",
                    "payload": {
                        "type": "text",
                        "text": message,
                        "expectSpeech": open_mic,
                        "needLight": True,
                        "needVoice": True,
                        "wakeupType": "continuity"
                    }
                }
            ]
        }
    }
    return RETURN_DATA

# 消息处理
async def conversation_process(hass, text, cfg):
    open_mic = cfg.get('open_mic', True)
    is_session_end = (open_mic == False)
    hass.async_create_task(hass.services.async_call('conversation', 'process', {'source': 'AliGenie','text': text}))
    # 如果配置到了查询，则不进入系统意图
    result = matcher_query_state(text)
    if result is not None:
        friendly_name = result
        state = await find_entity(hass, friendly_name)
        if state is not None:
            message = f'{friendly_name}的状态是{state.state}'
            if open_mic:
                message += '，请问还有什么事吗？'
            return build_text_message(message, is_session_end, open_mic)
    message = '收到'
    if open_mic:
        message += '，还有什么事吗？'
    return build_text_message(message, is_session_end, open_mic)

# 格式转换
async def parse_input(aligenie, data, hass):
    # 原始语音内容（这里先写死测试）
    text = data['utterance'].replace(aligenie, '')
    # 判断当前用户是否是自己
    cfg = hass.data['conversation_voice'].api_config.get_config()
    if text != '':
        return await conversation_process(hass, text, cfg)
            
    return build_text_message('我没听懂欸', is_session_end=True, open_mic=False)

class AliGenieView(HomeAssistantView):

    url = ALIGENIE_API
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        _LOGGER.debug("======= 天猫精灵API接口信息")
        _LOGGER.debug(data)
        # 读取配置文件
        cfg = hass.data['conversation_voice'].api_config.get_config()
        userOpenId = cfg.get('userOpenId', '')
        aligenie = cfg.get('aligenie', '请帮我')
        # 验证权限
        if userOpenId != '' and userOpenId != data['requestData']['userOpenId']:
            response =  build_text_message('抱歉，您没有权限', is_session_end=True, open_mic=False)
        else:
            response = await parse_input(aligenie, data, hass)
        return self.json(response)