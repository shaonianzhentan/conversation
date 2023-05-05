from __future__ import annotations

from functools import partial
import logging
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, MATCH_ALL
from homeassistant.core import HomeAssistant, Context
from homeassistant.exceptions import ConfigEntryNotReady, TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid
from home_assistant_intents import get_domains_and_languages, get_intents

from .conversation_assistant import ConversationAssistant
DATA_VOICE = "conversation_voice"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    assistant = ConversationAssistantAgent(hass, entry)
    conversation.async_set_agent(hass, entry, assistant)

    async def recognize(text, conversation_id=None):
        result = await assistant.async_process(
            conversation.ConversationInput(
                text=text,
                context=Context(),
                conversation_id=conversation_id,
            )
        )
        return result
    hass.data[DATA_VOICE] = ConversationAssistant(hass, recognize)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    conversation.async_unset_agent(hass, entry)
    return True


class ConversationAssistantAgent(conversation.AbstractConversationAgent):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        # 预定义实体
        self.calendar_id = self.entry.options.get("calendar_id")
        self.music_id = self.entry.options.get("music_id")

    @property
    def attribution(self):
        """Return the attribution."""
        return {"name": "由 shaonianzhentan 提供技术支持", "url": "https://github.com/shaonianzhentan/conversation"}

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return get_domains_and_languages()["homeassistant"]

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
        conversation_voice = self.hass.data[DATA_VOICE]
        text = conversation_voice.trim_char(user_input.text)

        # 调用内置服务
        conversation_result = await conversation.async_converse(
                hass=self.hass,
                text=text,
                conversation_id=conversation_id,
                context=user_input.context,
                language=language,
                agent_id='homeassistant'
            )
        intent_response = conversation_result.response
        if intent_response.error_code is not None:
            # 插件意图
            intent_response = await conversation_voice.async_process(text)

        speech = intent_response.speech.get('plain')
        if speech is not None:
            result = speech.get('speech')
            conversation_voice.update(text, result)

        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )