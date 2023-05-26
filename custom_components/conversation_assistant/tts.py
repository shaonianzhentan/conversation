from homeassistant.core import callback
from homeassistant.components.tts import TextToSpeechEntity

class ConversationTextToSpeechEntity(TextToSpeechEntity):

    def __init__(self, hass, entry):
        self.name = '文本转语音'

    @property
    def default_language(self):
        return "zh-cn"

    @property
    def supported_languages(self):
        return ["zh-cn", "zh-hk", "zh-tw"]

    @callback
    def async_get_supported_voices(self, language: str) -> list[str] | None:
        return ["zh-cn", "zh-hk", "zh-tw"]

    async def async_get_tts_audio(self, message: str, language: str, options):
        buffer = None
        return 'mp3', buffer