import json
import logging
from homeassistant.components.http import HomeAssistantView

from ..util import DOMAIN, XIAODU_API
from .xiaodu import discoveryDevice, controlDevice, queryDevice

_LOGGER = logging.getLogger(__name__)

class XiaoduGateView(HomeAssistantView):

    url = XIAODU_API
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        _LOGGER.debug("======= 小度API接口信息：%s", data)
        header = data['header']
        payload = data['payload']
        name = header['name']
        accessToken = payload['accessToken']
        # 正常授权验证
        token = await hass.auth.async_validate_access_token(accessToken)
        # 进行自定义服务验证
        if token is None:
            voice = hass.data["conversation_voice"]
            config_data = voice.api_config.get_config()
            apiKey = config_data.get('apiKey', '')
            # 判断是否定义apiKey
            if apiKey != '' and accessToken == f'apiKey{apiKey}':
                token = accessToken
        # 走正常流程
        result = {}
        if token is not None:
            namespace = header['namespace']
            if namespace == 'DuerOS.ConnectedHome.Discovery':
                # 发现设备
                result = await discoveryDevice(hass)
                name = 'DiscoverAppliancesResponse'
            elif namespace == 'DuerOS.ConnectedHome.Control':
                # 控制设备
                result = await controlDevice(hass, name, payload)
                if result is None:
                    name = 'UnsupportedOperationError'
                else:
                    name = name.replace('Request', 'Confirmation')
            elif namespace == 'DuerOS.ConnectedHome.Query':
                # 查询设备
                result = queryDevice(hass, name, payload)
                name = name.replace('Request', 'Response')
        else:
            name = 'InvalidAccessTokenError'

        header['name'] = name
        # 如果包含Uid则返回用户ID
        if 'openUid' in payload:
            result['openUid'] = payload['openUid']
        response = {'header': header, 'payload': result}

        _LOGGER.debug("Respnose: %s", response)    
        return self.json(response)