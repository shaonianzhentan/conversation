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
        _LOGGER.debug("======= 小度API接口信息")
        _LOGGER.debug(data)
        header = data['header']
        payload = data['payload']
        properties = None
        name = header['name']

        token = await hass.auth.async_validate_access_token(payload['accessToken'])
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
                    result = errorResult('DEVICE_NOT_SUPPORT_FUNCTION')
                name = name.replace('Request', 'Confirmation')
            elif namespace == 'DuerOS.ConnectedHome.Query':
                # 查询设备
                result = queryDevice(hass, name, payload)
                name = name.replace('Request', 'Response')
            else:
                result = errorResult('SERVICE_ERROR')
        else:
            result = errorResult('ACCESS_TOKEN_INVALIDATE')

        header['name'] = name
        # Fill response deviceId
        if 'deviceId' in payload:
            result['deviceId'] = payload['deviceId']

        response = {'header': header, 'payload': result}
        if properties:
            response['properties'] = properties
        _LOGGER.info("Respnose: %s", response)
    
        return self.json(response)


# 错误结果
def errorResult(errorCode, messsage=None):
    """Generate error result"""
    messages = {
        'INVALIDATE_CONTROL_ORDER':    'invalidate control order',
        'SERVICE_ERROR': 'service error',
        'DEVICE_NOT_SUPPORT_FUNCTION': 'device not support',
        'INVALIDATE_PARAMS': 'invalidate params',
        'DEVICE_IS_NOT_EXIST': 'device is not exist',
        'IOT_DEVICE_OFFLINE': 'device is offline',
        'ACCESS_TOKEN_INVALIDATE': ' access_token is invalidate'
    }
    return {'errorCode': errorCode, 'message': messsage if messsage else messages[errorCode]}