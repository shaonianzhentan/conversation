'''
https://github.com/home-assistant/core/tree/dev/homeassistant/components/conversation
'''
from __future__ import annotations

import logging, asyncio

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Context
from home_assistant_intents import get_languages
from homeassistant.const import Platform
from .http import HttpView
from .entity_assistant import EntityAssistant
from .conversation_assistant import ConversationAssistant
from .manifest import manifest

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.STT,  Platform.TTS]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 安装集成 '''
    hass.http.register_view(HttpView)

    assistant = ConversationAssistantAgent(hass, entry)
    conversation.async_set_agent(hass, entry, assistant)

    async def recognize(text, conversation_id=None):
        result = await assistant.async_process(
            conversation.ConversationInput(
                text=text,
                context=Context(),
                conversation_id=conversation_id,
                device_id=None,
                language=None
            )
        )
        return result
    hass.data[manifest.domain] = ConversationAssistant(hass, recognize, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def update_listener(hass, entry):
    ''' 更新配置 '''
    await async_unload_entry(hass, entry)
    await asyncio.sleep(1)
    await async_setup_entry(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 删除集成 '''
    conversation.async_unset_agent(hass, entry)
    del hass.data[manifest.domain]

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class ConversationAssistantAgent(conversation.AbstractConversationAgent):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry

        self.entity_assistant = EntityAssistant(hass, entry.options)

    @property
    def attribution(self):
        """Return the attribution."""
        return {"name": "由 shaonianzhentan 提供技术支持", "url": "https://github.com/shaonianzhentan/conversation"}

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return get_languages()

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        conversation_id = user_input.conversation_id
        # 兼容中文语句
        language = user_input.language or self.hass.config.language
        country = self.hass.config.country
        if language == "zh-Hans":
            language = "zh-cn"
        elif language == "zh-Hant":
            if country == "HK":
                language = "zh-hk"
            elif country == "TW":
                language = "zh-tw"

        # 处理意图
        conversation_assistant = self.hass.data[manifest.domain]
        text = conversation_assistant.trim_char(user_input.text)
        if text == '':
            return conversation.ConversationResult(
                response=conversation_assistant.intent_result('没有接收到控制命令'),
                conversation_id=conversation_id
            )

        # 调用Hass意图
        conversation_result = await conversation.async_converse(
            hass=self.hass,
            text=text,
            conversation_id=conversation_id,
            context=user_input.context,
            language=language,
            agent_id='homeassistant',
            device_id=user_input.device_id
        )
        intent_response = conversation_result.response
        if intent_response.error_code is not None:
            # 插件意图
            result = await self.entity_assistant.async_process(text)
            if result is not None:
                message, entity_id = result
                state = self.hass.states.get(entity_id)
                entities = [
                    {
                        'id': entity_id,
                        'name': state.attributes.get('friendly_name'),
                        'state': state.state
                    }
                ]
                intent_response = conversation_assistant.intent_result(message, {
                    'entities': entities
                })
            else:
                intent_response = await conversation_assistant.async_process(text)

        speech = intent_response.speech.get('plain')
        if speech is not None:
            result = speech.get('speech')
            conversation_assistant.update(text, result)

        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )