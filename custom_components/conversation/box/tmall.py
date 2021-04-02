'''
区域：https://open.bot.tmall.com/oauth/api/placelist
设备类型：https://doc-bot.tmall.com/docs/doc.htm?treeId=393&articleId=108271&docType=1
'''

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

def discoveryDevice(hass):
    devices = []
    devices.append({
        'deviceId': 'entity_id',
        'deviceName': '彩灯',
        'deviceType': 'light',
        'zone': '卧室',
        'brand': 'HomeAssistant',
        'model': '彩灯',
        'icon': 'https://home-assistant.io/images/favicon-192x192.png',
        'properties': [ "brightness" ],
        'actions': ['TurnOn', 'TurnOff', 'Query']
        })
    return {'devices': devices}

async def controlDevice(action, payload):
    deviceId = payload['deviceId']
    # 根据设备ID，找到对应的实体ID
    return errorResult('IOT_DEVICE_OFFLINE')

def queryDevice(name, payload):
    deviceId = payload['deviceId']
    deviceType = payload['deviceType']
    return errorResult('IOT_DEVICE_OFFLINE')