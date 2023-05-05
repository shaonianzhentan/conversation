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

from .conversation import Conversation
DATA_VOICE = "conversation_voice"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    assistant = ConversationAssistant(hass, entry)
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
    hass.data[DATA_VOICE] = Conversation(hass, recognize)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    conversation.async_unset_agent(hass, entry)
    return True


class ConversationAssistant(conversation.AbstractConversationAgent):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[dict]] = {}
        # 预定义实体
        self.calendar_id = self.entry.options.get("calendar_id")
        self.music_id = self.entry.options.get("music_id")

    @property
    def attribution(self):
        """Return the attribution."""
        return {"name": "Powered by shaonianzhentan", "url": "https://github.com/shaonianzhentan/conversation"}

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        raw_prompt = "系统提示"

        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            prompt = self._async_generate_prompt(raw_prompt)
            messages = [{"role": "system", "content": prompt}]

        messages.append({"role": "user", "content": user_input.text})

        # 处理意图
        conversation_voice = self.hass.data[DATA_VOICE]
        text = conversation_voice.trim_char(text)

        # 调用内置服务
        intent_response = await conversation.async_converse(
                hass=self.hass,
                text=text,
                conversation_id=conversation_id,
                context=user_input.context
            )
        response = intent_response.response
        if response.error_code is not None:
            # 插件意图
            intent_response = await conversation_voice.async_process(text)

        speech = intent_response.speech.get('plain')
        if speech is not None:
            result = speech.get('speech')
            conversation_voice.update(text, result)

        _LOGGER.debug("Response %s", result)

        messages.append({"role": "system", "content": result})
        self.history[conversation_id] = messages

        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    def _async_generate_prompt(self, raw_prompt: str) -> str:
        """Generate a prompt for the user."""
        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
            },
            parse_result=False,
        )