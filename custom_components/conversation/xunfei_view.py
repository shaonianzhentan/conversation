import os
import json
import logging
from homeassistant.components.http import HomeAssistantView
_LOGGER = logging.getLogger(__name__)

from .util import DOMAIN, XUNFEI_API

class XunfeiView(HomeAssistantView):

    url = XUNFEI_API
    name = DOMAIN
    requires_auth = False

    async def put(self, request):
        hass = request.app["hass"]
        xunfei_pi_path = hass.config.path(f"./custom_components/conversation/xunfei_pi/bin")
        try:
            
            # 判断程序文件是否存在
            iat_sample = f'{xunfei_pi_path}/iat_sample'
            if os.path.exists(iat_sample) == False:
                return self.json({ 'code': 1, 'msg': '文件不存在'})

            # 读取文件
            reader = await request.multipart()
            file = await reader.next()
            filename = f"{xunfei_pi_path}/voice.wav"
            with open(filename, 'wb') as f:
                while True:
                    chunk = await file.read_chunk()  # 默认是8192个字节。
                    if not chunk:
                        break
                    size += len(chunk)
                    f.write(chunk)

            # 语音转文本
            rs = os.popen(iat_sample)
            text = rs.read()
            print(text)
            arr = text.split('=============================================================')
            if len(arr) == 0:
                return None
            result = arr[1].strip('\n')
            return self.json({ 'code': 0, 'msg': '识别成功', 'data': result})
        except Exception as e:
            return self.json({ 'code': 1, 'msg': '出现异常', 'data': e})