import logging, aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import tts
from urllib.parse import quote

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
        return ["zh-cn"]

    @property
    def supported_options(self):
        """Return list of supported options like voice, emotion."""
        return [tts.ATTR_AUDIO_OUTPUT, tts.ATTR_VOICE, ATTR_SPEAKER]

    @property
    def default_options(self):
        """Return a dict include default options."""
        return {tts.ATTR_AUDIO_OUTPUT: "mp3"}

    @callback
    def async_get_supported_voices(self, language: str) -> list[str] | None:
        return [ 
            tts.Voice(voice_id='默认', name='默认')
        ]

    async def async_get_tts_audio(self, message, language, options):
        voice_name: str | None = options.get(tts.ATTR_VOICE)
        voice_speaker: str | None = options.get(ATTR_SPEAKER)

        url = f'https://fanyi.baidu.com/gettts?lan=zh&text={quote(message)}&spd=5&source=web'
        _LOGGER.debug(url)
        buffer = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                buffer = await response.read()
        return 'mp3', buffer