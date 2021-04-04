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
        name = header['name']

        token = await hass.auth.async_validate_access_token(payload['accessToken'])
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
        response = {'header': header, 'payload': result}
        _LOGGER.info("Respnose: %s", response)    
        return self.json(response)