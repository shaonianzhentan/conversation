"""Support for functionality to have conversations with Home Assistant."""
import logging
import re, aiohttp

import voluptuous as vol

from homeassistant import core
from homeassistant.components import http, websocket_api
from homeassistant.components.http.data_validator import RequestDataValidator
from homeassistant.const import HTTP_INTERNAL_SERVER_ERROR
from homeassistant.helpers import config_validation as cv, intent
from homeassistant.loader import bind_hass

from .agent import AbstractConversationAgent
from .default_agent import DefaultAgent, async_register

_LOGGER = logging.getLogger(__name__)

ATTR_TEXT = "text"

DOMAIN = "conversation"

REGEX_TYPE = type(re.compile(""))
DATA_AGENT = "conversation_agent"
DATA_CONFIG = "conversation_config"

SERVICE_PROCESS = "process"

SERVICE_PROCESS_SCHEMA = vol.Schema({vol.Required(ATTR_TEXT): cv.string})

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("intents"): vol.Schema(
                    {cv.string: vol.All(cv.ensure_list, [cv.string])}
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async_register = bind_hass(async_register)  # pylint: disable=invalid-name


@core.callback
@bind_hass
def async_set_agent(hass: core.HomeAssistant, agent: AbstractConversationAgent):
    """Set the agent to handle the conversations."""
    hass.data[DATA_AGENT] = agent


async def async_setup(hass, config):
    """Register the process service."""
    hass.data[DATA_CONFIG] = config

    async def handle_service(service):
        """Parse text into commands."""
        text = service.data[ATTR_TEXT]
        _LOGGER.debug("Processing: <%s>", text)
        agent = await _get_agent(hass)
        try:
            await agent.async_process(text, service.context)
        except intent.IntentHandleError as err:
            _LOGGER.error("Error processing %s: %s", text, err)

    hass.services.async_register(
        DOMAIN, SERVICE_PROCESS, handle_service, schema=SERVICE_PROCESS_SCHEMA
    )
    hass.http.register_view(ConversationProcessView())
    hass.components.websocket_api.async_register_command(websocket_process)
    hass.components.websocket_api.async_register_command(websocket_get_agent_info)
    hass.components.websocket_api.async_register_command(websocket_set_onboarding)

    return True


@websocket_api.async_response
@websocket_api.websocket_command(
    {"type": "conversation/process", "text": str, vol.Optional("conversation_id"): str}
)
async def websocket_process(hass, connection, msg):
    """Process text."""
    connection.send_result(
        msg["id"],
        await _async_converse(
            hass, msg["text"], msg.get("conversation_id"), connection.context(msg)
        ),
    )


@websocket_api.async_response
@websocket_api.websocket_command({"type": "conversation/agent/info"})
async def websocket_get_agent_info(hass, connection, msg):
    """Do we need onboarding."""
    agent = await _get_agent(hass)

    connection.send_result(
        msg["id"],
        {
            "onboarding": await agent.async_get_onboarding(),
            "attribution": agent.attribution,
        },
    )


@websocket_api.async_response
@websocket_api.websocket_command({"type": "conversation/onboarding/set", "shown": bool})
async def websocket_set_onboarding(hass, connection, msg):
    """Set onboarding status."""
    agent = await _get_agent(hass)

    success = await agent.async_set_onboarding(msg["shown"])

    if success:
        connection.send_result(msg["id"])
    else:
        connection.send_error(msg["id"])


class ConversationProcessView(http.HomeAssistantView):
    """View to process text."""

    url = "/api/conversation/process"
    name = "api:conversation:process"

    @RequestDataValidator(
        vol.Schema({vol.Required("text"): str, vol.Optional("conversation_id"): str})
    )
    async def post(self, request, data):
        """Send a request for processing."""
        hass = request.app["hass"]

        try:
            intent_result = await _async_converse(
                hass, data["text"], data.get("conversation_id"), self.context(request)
            )
        except intent.IntentError as err:
            _LOGGER.error("Error handling intent: %s", err)
            return self.json(
                {
                    "success": False,
                    "error": {
                        "code": str(err.__class__.__name__).lower(),
                        "message": str(err),
                    },
                },
                status_code=HTTP_INTERNAL_SERVER_ERROR,
            )

        return self.json(intent_result)


async def _get_agent(hass: core.HomeAssistant) -> AbstractConversationAgent:
    """Get the active conversation agent."""
    agent = hass.data.get(DATA_AGENT)
    if agent is None:
        agent = hass.data[DATA_AGENT] = DefaultAgent(hass)
        await agent.async_initialize(hass.data.get(DATA_CONFIG))
    return agent

def text_start(findText, text):
    return text.find(findText,0,len(findText)) >= 0

async def _async_converse(
    hass: core.HomeAssistant, text: str, conversation_id: str, context: core.Context
) -> intent.IntentResponse:
    """Process text and get intent."""
    agent = await _get_agent(hass)
    try:
        # 去掉前后标点符号
        _text = text.strip('。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')    
        # 发送事件，共享给其他组件
        hass.bus.fire('ha_voice_text_event', {
            'text': _text
        })
        # 执行自定义脚本
        states = hass.states.async_all()
        for state in states:
            entity_id = state.entity_id
            if entity_id.find('script.') == 0:
                attributes = state.attributes
                friendly_name = attributes.get('friendly_name')
                cmd = friendly_name.split('=')
                if cmd.count(_text) > 0:
                    arr = entity_id.split('.')
                    _LOGGER.info('执行脚本：' + entity_id)
                    await hass.services.async_call(arr[0], arr[1])
                    intent_result = intent.IntentResponse()
                    intent_result.async_set_speech("正在执行自定义脚本：" + entity_id)
                    return intent_result
        
        # 开关控制
        intent_type = ''
        if text_start('打开',_text) or text_start('开启',_text) or text_start('启动',_text):
            intent_type = 'HassTurnOn'
            if '打开' in _text:
                _name = _text.split('打开')[1]
            elif '开启' in _text:
                _name = _text.split('开启')[1]
            elif '启动' in _text:
                _name = _text.split('启动')[1]
        elif text_start('关闭',_text) or text_start('关掉',_text) or text_start('关上',_text):
            intent_type = 'HassTurnOff'
            if '关闭' in _text:
                _name = _text.split('关闭')[1]
            elif '关掉' in _text:
                _name = _text.split('关掉')[1]
            elif '关上' in _text:
                _name = _text.split('关上')[1]            
        elif text_start('切换', _text):
            intent_type = 'HassToggle'
            _name = _text.split('切换')[1]
        # 默认的开关操作
        if intent_type != '':
            # 操作所有灯和开关
            if _name == '所有灯' or _name == '所有的灯' or _name == '全部灯' or _name == '全部的灯':
                _name = 'all lights'
            elif _name == '所有开关' or _name == '所有的开关' or _name == '全部开关' or _name == '全部的开关':
                _name = 'all switchs'
            await intent.async_handle(hass, DOMAIN, intent_type, {'name': {'value': _name}})
            intent_result = intent.IntentResponse()
            intent_result.async_set_speech("正在" + text)
            return intent_result
        else:
            intent_result = await agent.async_process(text, context, conversation_id)
    except intent.IntentHandleError as err:
        err_msg = str(err)
        if 'Unable to find an entity called' in err_msg:
            err_msg = err_msg.replace('Unable to find an entity called', '没有找到这个设备：')

        intent_result = intent.IntentResponse()
        intent_result.async_set_speech(err_msg)

    if intent_result is None:
        # 调用聊天机器人
        message = "对不起，我不明白"
        try:
            async with aiohttp.request('GET','https://api.ownthink.com/bot?appid=xiaosi&spoken=' + text) as r:
                res = await r.json(content_type=None)
                _LOGGER.info(res)
                message = res['data']['info']['text']
        except Exception as e:
            _LOGGER.info(e)
        intent_result = intent.IntentResponse()
        intent_result.async_set_speech(message)

    return intent_result
