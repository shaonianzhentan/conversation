import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import stt
from .speech_recognition import async_speech_recognition

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            ConversationSttEntity(config_entry),
        ]
    )

class ConversationSttEntity(stt.SpeechToTextEntity):

    def __init__(self, config_entry: ConfigEntry):
        self._attr_name = '语音助手STT'
        self._attr_unique_id = f"{config_entry.entry_id}-stt"
        self.speech_key = config_entry.options.get('speech_key', '')

    @property
    def supported_languages(self):
        return ["zh-cn"]

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        """Return a list of supported formats."""
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[stt.AudioCodecs]:
        """Return a list of supported codecs."""
        return [stt.AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[stt.AudioBitRates]:
        """Return a list of supported bitrates."""
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[stt.AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[stt.AudioChannels]:
        """Return a list of supported channels."""
        return [stt.AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stt_stream) -> stt.SpeechResult:

        if self.speech_key == '':
            return stt.SpeechResult('未配置Azure语音服务密钥', stt.SpeechResultState.SUCCESS)

        try:

            text = await self.async_post_audio(stt_stream)
            if text is not None and text != '':
                return stt.SpeechResult(text, stt.SpeechResultState.SUCCESS)

        except Exception as err:
            _LOGGER.exception("Error processing audio stream: %s", err)
            return stt.SpeechResult('识别出现异常，请检查Azure语音服务密钥是否正确，或者联系插件作者寻求帮助', stt.SpeechResultState.SUCCESS)

        return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

    async def async_post_audio(self, stt_stream):
        async def file_sender():
            async for audio_bytes in stt_stream:
                yield audio_bytes
            _LOGGER.debug('识别结束')
        return await async_speech_recognition(self.speech_key, file_sender)