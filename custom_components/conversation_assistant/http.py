import tempfile
from homeassistant.components.http import HomeAssistantView
from .manifest import manifest
from .speech_recognition import async_ops_recognition
class HttpView(HomeAssistantView):

    url = "/api/conversation_assistant"
    name = "api:conversation_assistant"
    requires_auth = True

    async def post(self, request):
        hass = request.app["hass"]
        body = await request.json()
        text = body.get('text')
        conversation_assistant = hass.data[manifest.domain]
        result = await conversation_assistant.recognize(text)
        return self.json(result.as_dict())

    async def put(self, request):
        hass = request.app["hass"]
        # 读取文件
        reader = await request.multipart()
        formData = {}
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.filename is None:
                value = await part.text()
            else:
                value = await self.async_write_file(hass, part)
            formData[part.name] = value

        # 语音识别
        ops_file = formData.get('file')
        conversation_assistant = hass.data[manifest.domain]
        text = await async_ops_recognition(conversation_assistant.speech_key, ops_file)
        result = await conversation_assistant.recognize(text)
        return self.json(result.as_dict())

    async def async_write_file(self, hass, file):
        temp = tempfile.NamedTemporaryFile(delete=False)
        size = 0
        while True:
            chunk = await file.read_chunk()  # 默认是8192个字节。
            if not chunk:
                break
            size += len(chunk)
            temp.write(chunk)
        return temp.name