
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

# 发现设备
def discoveryDevice():

    devices = []

    # devices.append({
    #     'applianceId': 'sensor.temperature_158d0001830246',
    #     'friendlyName': '卧室温度',
    #     'friendlyDescription': '卧室温度',
    #     'additionalApplianceDetails': [],
    #     'applianceTypes': ['AIR_CONDITION'],
    #     'isReachable': True,
    #     'manufacturerName': 'HomeAssistant',
    #     'modelName': 'HomeAssistantLight',
    #     'version': '1.0',
    #     'actions': ["getTemperatureReading"],
    # })
 
    return {'discoveredAppliances': devices}


# 控制设备
async def controlDevice(action, payload):
    applianceDic = payload['appliance']
    entity_id = applianceDic['applianceId']
    # 根据设备ID，找到对应的实体ID
    return errorResult('IOT_DEVICE_OFFLINE')

# 查询设备
def queryDevice(name, payload):
    deviceId = payload['deviceId']
    deviceType = payload['deviceType']

    return errorResult('IOT_DEVICE_OFFLINE')