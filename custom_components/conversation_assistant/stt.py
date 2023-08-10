import logging, requests, json
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import stt

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
            async def get_chunk():
                async for audio_bytes in stt_stream:
                    yield audio_bytes

            result = await self.hass.async_add_executor_job(self.post_audio, get_chunk)
            text = "".join(result["DisplayText"])

        except Exception as err:
            _LOGGER.exception("Error processing audio stream: %s", err)
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

        return stt.SpeechResult(
            text,
            stt.SpeechResultState.SUCCESS,
        )

    def post_audio(self, get_chunk):
        ''' 微软语音识别 '''
        region = 'eastasia'
        url = "https://%s.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN" % region

        headers = { 'Accept': 'application/json;text/xml',
            'Connection': 'Keep-Alive',
            'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000',
            'Ocp-Apim-Subscription-Key': self.speech_key,
            'Transfer-Encoding': 'chunked',
            'Expect': '100-continue' }

        response = requests.post(url=url, data=get_chunk(), headers=headers)
        resultJson = json.loads(response.text)
        print(json.dumps(resultJson, indent=4))
        return resultJson