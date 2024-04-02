import aiohttp, logging
import opuslib.api.decoder as decoder

_LOGGER = logging.getLogger(__name__)

async def async_speech_recognition(speech_key, buffer_data, content_type='wav'):
    ''' 微软语音识别 '''
    region = 'eastasia'
    url = "https://%s.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=zh-CN" % region

    headers = {
        'Accept': 'application/json;text/xml',
        'Connection': 'Keep-Alive',
        'Content-Type': 'audio/wav; codecs=audio/pcm; samplerate=16000' if content_type == 'wav' else 'audio/pcm; samplerate=16000',
        'Ocp-Apim-Subscription-Key': speech_key,
        'Expect': '100-continue'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=buffer_data if isinstance(buffer_data, bytearray) else buffer_data()) as response:
            if response.status == 200:
                result = await response.json()
                _LOGGER.debug(result)
                return result['DisplayText']

async def async_ops_recognition(speech_key, file_path):
    ''' 小爱同学语音数据 '''
    with open(file_path, 'rb') as file:
        data = bytearray(file.read())
    # 音频数据解码
    dec = decoder.create_state(16000, 1)
    chunk_len = 640
    index = 0
    output = bytearray()
    encodeLength = 0
    while (index < len(data)-encodeLength):
        encodeLength = data[index]
        encodeData = data[index+1:index+encodeLength+1]
        decodeData = decoder.decode(dec, bytes(
            encodeData), len(encodeData), chunk_len, 0)
        output.extend(decodeData[:chunk_len])
        del data[index]
        index += encodeLength
    # 文件识别
    return await async_speech_recognition(speech_key, output, 'pcm')