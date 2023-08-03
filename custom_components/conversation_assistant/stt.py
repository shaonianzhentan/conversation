import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import stt

import azure.cognitiveservices.speech as speechsdk

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
        self.speech_key = config_entry.options.get('speech_key')
        self._attr_name = '语音助手STT'
        self._attr_unique_id = f"{config_entry.entry_id}-stt"

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
        text = None
        try:
            speech_key, service_region = self.speech_key, "eastasia"
            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

            stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=stream)

            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language="zh-CN", audio_config=audio_config)
            
            # Connect callbacks to the events fired by the speech recognizer
            speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
            speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
            speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
            speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
            speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

            speech_recognizer.start_continuous_recognition()
            print('开始识别')

            async for audio_bytes in stt_stream:
                stream.write(audio_bytes)

            print('结束啦')
            stream.close()
            speech_recognizer.stop_continuous_recognition()
            
        except Exception as err:
            print(err)
            _LOGGER.exception("Error processing audio stream: %s", err)
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)        

        if text is None:
            print('没听到声音')
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

        return stt.SpeechResult(
            text,
            stt.SpeechResultState.SUCCESS,
        )