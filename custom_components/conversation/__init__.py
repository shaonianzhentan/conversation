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

from .voice import Voice

_LOGGER = logging.getLogger(__name__)

ATTR_TEXT = "text"

DOMAIN = "conversation"

REGEX_TYPE = type(re.compile(""))
DATA_AGENT = "conversation_agent"
DATA_CONFIG = "conversation_config"
DATA_VOICE = "conversation_voice"

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

    # 显示插件信息
    hass.data[DATA_VOICE] = Voice(hass)
    _LOGGER.info('''
-------------------------------------------------------------------
    语音小助手【作者QQ：635147515】
    
    版本：1.2
    
    介绍：官方语音助手修改增强版
    
    项目地址：https://github.com/shaonianzhentan/conversation

-------------------------------------------------------------------''')
    local = hass.config.path("custom_components/ha_cloud_music/local")
    hass.http.register_static_path('/conversation', local, False)

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


async def _async_converse(
    hass: core.HomeAssistant, text: str, conversation_id: str, context: core.Context
) -> intent.IntentResponse:
    """Process text and get intent."""
    agent = await _get_agent(hass)
    voice = hass.data[DATA_VOICE]
    try:
        # 去掉前后标点符号
        _text = voice.fire_text(text)
        # 执行自定义脚本
        result = await voice.execute_script(_text)
        if result is not None:
            return result
        
        # 开关控制
        result = await voice.execute_switch(_text)
        if result is not None:
            return result

        # 内置处理指令
        intent_result = await agent.async_process(_text, context, conversation_id)
    except intent.IntentHandleError as err:
        # 错误信息处理
        err_msg = voice.error_msg(str(err))

        intent_result = intent.IntentResponse()
        intent_result.async_set_speech(err_msg)

    if intent_result is None:
        # 调用聊天机器人
        message = await voice.chat_robot(text)
        intent_result = intent.IntentResponse()
        intent_result.async_set_speech(message)

    return intent_result
