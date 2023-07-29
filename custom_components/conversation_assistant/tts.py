import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import tts

import azure.cognitiveservices.speech as speechsdk

_LOGGER = logging.getLogger(__name__)
ATTR_SPEAKER = 'speaker'

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            ConversationTtsEntity(config_entry),
        ]
    )

class ConversationTtsEntity(tts.TextToSpeechEntity):

    def __init__(self, config_entry):
        self.speech_key = config_entry.options.get('speech_key')
        self._attr_name = '语音助手TTS'
        self._attr_unique_id = f"{config_entry.entry_id}-tts"

    @property
    def default_language(self):
        return "zh-cn"

    @property
    def supported_languages(self):
        return ["zh-cn", "zh-hk", "zh-tw"]

    @property
    def supported_options(self):
        """Return list of supported options like voice, emotion."""
        return [tts.ATTR_AUDIO_OUTPUT, tts.ATTR_VOICE, ATTR_SPEAKER]

    @property
    def default_options(self):
        """Return a dict include default options."""
        return {tts.ATTR_AUDIO_OUTPUT: "wav"}

    @callback
    def async_get_supported_voices(self, language: str) -> list[str] | None:
        return ["zh-cn", "zh-hk", "zh-tw"]

    async def async_get_tts_audio(self, message, language, options):
        voice_name: str | None = options.get(tts.ATTR_VOICE)
        voice_speaker: str | None = options.get(ATTR_SPEAKER)
        buffer = []
        return 'mp3', buffer