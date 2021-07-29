import logging, json
from homeassistant.components.http import HomeAssistantView
from ..util import DOMAIN, TMALL_API
from .tmall import discoveryDevice, controlDevice, errorResult

_LOGGER = logging.getLogger(__name__)

class TmallView(HomeAssistantView):

    url = TMALL_API
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        hass = request.app["hass"]
        data = await request.json()
        _LOGGER.debug("======= 天猫精灵API接口信息：%s", data)
        header = data['header']
        payload = data['payload']
        name = header['name']
        accessToken = payload['accessToken']
        # 验证权限
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
            if namespace == 'AliGenie.Iot.Device.Discovery':
                # 发现设备
                result = await discoveryDevice(hass)
                name = 'DiscoveryDevicesResponse'
            elif namespace == 'AliGenie.Iot.Device.Control':
                # 控制设备
                result = await controlDevice(hass, name, payload)
                name = 'CorrectResponse'
        else:
            result = errorResult('ACCESS_TOKEN_INVALIDATE')

        # Check error and fill response name
        header['name'] = name
        
        response = {'header': header, 'payload': result}
        
        _LOGGER.debug("Respnose: %s", response)
        return self.json(response)