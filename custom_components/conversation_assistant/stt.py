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
        return ["zh-cn", "zh-hk", "zh-tw"]
    
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

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stream) -> stt.SpeechResult:
        try:
            translation_config = speechsdk.translation.SpeechTranslationConfig(
                subscription=self.speech_key, region="eastasia",
                speech_recognition_language='zh-CN')
            
            audio_config = speechsdk.audio.FromStreamInput(stream)

            recognizer = speechsdk.translation.TranslationRecognizer(
                translation_config=translation_config, audio_config=audio_config)
            
            result = recognizer.recognize_once()

            # Check the result
            if result.reason == speechsdk.ResultReason.TranslatedSpeech:                
                text = result.text
                print("""Recognized: {}
                German translation: {}
                French translation: {}
                Chinese translation: {}""".format(
                    result.text, result.translations['de'],
                    result.translations['fr'],
                    result.translations['zh-Hans'],))
            elif result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print("Recognized: {}".format(result.text))
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized: {}".format(result.no_match_details))
            elif result.reason == speechsdk.ResultReason.Canceled:
                print("Translation canceled: {}".format(result.cancellation_details.reason))
                if result.cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(result.cancellation_details.error_details))

        except Exception as err:
            _LOGGER.exception("Error processing audio stream: %s", err)
            return stt.SpeechResult(None, stt.SpeechResultState.ERROR)

        return stt.SpeechResult(
            text,
            stt.SpeechResultState.SUCCESS,
        )