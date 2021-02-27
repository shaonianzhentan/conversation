from .util import DOMAIN, ALIGENIE_API
from .aligenie import discoveryDevice, controlDevice, queryDevice

_LOGGER = logging.getLogger(__name__)

class AliGenieView(HomeAssistantView):

    url = ALIGENIE_API
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        try:
            data = await request.json()
            """Handle request"""
            header = data['header']
            payload = data['payload']
            properties = None
            name = header['name']
            _LOGGER.info("Handle Request: %s", data)
            # 验证权限
            token = await hass.auth.async_validate_access_token(payload['accessToken'])
            if token is not None:
                namespace = header['namespace']
                if namespace == 'AliGenie.Iot.Device.Discovery':
                    # 发现设备
                    result = discoveryDevice(hass)
                elif namespace == 'AliGenie.Iot.Device.Control':
                    # 控制设备
                    result = await controlDevice(name, payload)
                elif namespace == 'AliGenie.Iot.Device.Query':
                    # 查询设备
                    result = queryDevice(name, payload)
                    if not 'errorCode' in result:
                        properties = result
                        result = {}
                else:
                    result = errorResult('SERVICE_ERROR')
            else:
                result = errorResult('ACCESS_TOKEN_INVALIDATE')

            # Check error and fill response name
            header['name'] = ('Error' if 'errorCode' in result else name) + 'Response'

            # Fill response deviceId
            if 'deviceId' in payload:
                result['deviceId'] = payload['deviceId']

            response = {'header': header, 'payload': result}
            if properties:
                response['properties'] = properties
            _LOGGER.info("Respnose: %s", response)
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
            response = {'header': {'name': 'errorResult'}, 'payload': errorResult('SERVICE_ERROR', 'service exception')}

        return self.json(response)
