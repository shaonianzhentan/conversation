import json
import logging
from homeassistant.components.http import HomeAssistantView

from .util import DOMAIN, XIAODU_API
from .xiaodu import discoveryDevice, controlDevice, queryDevice

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

        token = await _hass.auth.async_validate_access_token(payload['accessToken'])
        if token is not None:
            namespace = header['namespace']
            if namespace == 'DuerOS.ConnectedHome.Discovery':
                # 回应名称
                header['name'] = 'DiscoverAppliancesResponse'
                # 发现设备
                result = discoveryDevice(hass)
            elif namespace == 'DuerOS.ConnectedHome.Control':
                # 控制设备
                result = await controlDevice(name, payload)
            elif namespace == 'DuerOS.ConnectedHome.Query':
                # 查询设备
                result = queryDevice(name, payload)
                if not 'errorCode' in result:
                    properties = result
                    result = {}
            else:
                result = errorResult('SERVICE_ERROR')
        else:
            result = errorResult('ACCESS_TOKEN_INVALIDATE')

        # Fill response deviceId
        if 'deviceId' in payload:
            result['deviceId'] = payload['deviceId']

        response = {'header': header, 'payload': result}
        if properties:
            response['properties'] = properties
        _LOGGER.info("Respnose: %s", response)
    
        return self.json(response)
