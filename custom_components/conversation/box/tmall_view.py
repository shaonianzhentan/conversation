import logging, json
from homeassistant.components.http import HomeAssistantView
from ..util import DOMAIN, TMALL_API
from .tmall import discoveryDevice, controlDevice, queryDevice, errorResult

_LOGGER = logging.getLogger(__name__)

class TmallView(HomeAssistantView):

    url = TMALL_API
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        try:
            data = await request.json()
            """Handle request"""
            header = data['header']
            payload = data['payload']
            name = header['name']
            _LOGGER.debug("Handle Request: %s", data)
            # 验证权限
            token = await hass.auth.async_validate_access_token(payload['accessToken'])
            if token is not None:
                namespace = header['namespace']
                if namespace == 'AliGenie.Iot.Device.Discovery':
                    # 发现设备
                    result = discoveryDevice(hass)
                    name = 'DiscoveryDevicesResponse'
                elif namespace == 'AliGenie.Iot.Device.Control':
                    # 控制设备
                    result = await controlDevice(hass, name, payload)
                    name = 'CorrectResponse'
                elif namespace == 'AliGenie.Iot.Device.Query':
                    # 查询设备
                    result = queryDevice(name, payload)
                else:
                    result = errorResult('SERVICE_ERROR')
            else:
                result = errorResult('ACCESS_TOKEN_INVALIDATE')

            # Check error and fill response name
            header['name'] = name
            
            response = {'header': header, 'payload': result}
            _LOGGER.debug("Respnose: %s", response)
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
            response = {'header': {'name': 'errorResult'}, 'payload': errorResult('SERVICE_ERROR', 'service exception')}

        return self.json(response)