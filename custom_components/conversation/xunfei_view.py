import os, subprocess
import json
import logging
from homeassistant.components.http import HomeAssistantView
_LOGGER = logging.getLogger(__name__)

from .util import DOMAIN, XUNFEI_API

class XunfeiView(HomeAssistantView):

    url = XUNFEI_API
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        query = request.query
        type = query.get('type', '')
        root_path = hass.config.path(r"custom_components/conversation/xunfei_pi/")
        iat_sample = f'{root_path}iat_sample'
        try:
            # 判断程序文件是否存在
            if os.path.exists(iat_sample) == False:
                return self.json({ 'code': 1, 'msg': '文件不存在'})

            # 读取文件
            reader = await request.multipart()
            file = await reader.next()
            filename = f"{root_path}voice.wav"
            size = 0
            with open(filename, 'wb') as f:
                while True:
                    chunk = await file.read_chunk()  # 默认是8192个字节。
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)

            # 语音转文本
            pi = os.popen(f'{root_path}iat_sample.sh')
            text = pi.read()
            _LOGGER.debug(text)
            arr = text.split('=============================================================')
            if len(arr) > 0:
                result = arr[1].strip('\n')
                # 调用语音识别服务
                if(type == 'conversation'):
                    hass.async_create_task(hass.services.async_call('conversation', 'process', {'source': 'XunFei','text': result}))
                return self.json({ 'code': 0, 'msg': '识别成功', 'data': result})
            else:
                return self.json({ 'code': 1, 'msg': '识别失败', 'data': text})            
        except Exception as e:
            _LOGGER.debug(e)
            return self.json({ 'code': 1, 'msg': '出现异常'})