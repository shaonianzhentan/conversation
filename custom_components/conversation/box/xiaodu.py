import time
from homeassistant.helpers import template, entity_registry, area_registry

# 10位时间戳
def date_now():
    return int(time.time())

# 异步调用服务
def call_service(hass, service, data={}):
    arr = service.split('.')
    domain = arr[0]
    action = arr[1]
    hass.async_create_task(hass.services.async_call(domain, action, data))
    entity_id = data['entity_id']
    state = hass.states.get(entity_id)
    attributes = state.attributes
    friendly_name = attributes.get('device_name', attributes.get('friendly_name'))
    timestampOfSample = date_now()
    powerState = state.state.upper()
    if action == 'turn_off':
        powerState = 'OFF'
    if action == 'turn_on':
        powerState = 'ON'
    attrs = [
        {
            "name": "name",
            "value": friendly_name,
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "STRING"
        },
        {
            "name": "powerState",
            "value": powerState,
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(ON, OFF)"
        },
        {
            "name": "connectivity",
            "value": "REACHABLE",
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(UNREACHABLE, REACHABLE)"
        }
    ]
    if domain == 'light':
        brightness = attributes.get('brightness', 255)
        attrs.extend([
            {
                "name": "brightness",
                "value": int(brightness / 255 * 100),
                "scale": "%",
                "timestampOfSample": timestampOfSample,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ])
    return {
        'attributes': attrs
    }

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

# 实体属性
def entity_attributes(hass, entity_id):
    domain = entity_id.split('.')[0]
    state = hass.states.get(entity_id)
    attributes = state.attributes
    friendly_name = attributes.get('device_name', attributes.get('friendly_name'))
    timestampOfSample = date_now()
    attrs = [
        {
            "name": "name",
            "value": friendly_name,
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "STRING"
        },
        {
            "name": "powerState",
            "value": state.state.upper(),
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(ON, OFF)"
        },
        {
            "name": "turnOnState",
            "value": state.state.upper(),
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10
        },
        {
            "name": "connectivity",
            "value": "REACHABLE",
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(UNREACHABLE, REACHABLE)"
        }
    ]
    if domain == 'light':
        brightness = attributes.get('brightness', 255)
        attrs.extend([
            {
                "name": "brightness",
                "value": int(brightness / 255 * 100),
                "scale": "%",
                "timestampOfSample": timestampOfSample,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        ])
    return attrs



# 发现设备
async def discoveryDevice(hass):
    devices = []    
    # 获取所有区域
    area = await area_registry.async_get_registry(hass)
    area_list = area.async_list_areas()
    for area_item in area_list:
        entity = await entity_registry.async_get_registry(hass)
        entity_list = entity_registry.async_entries_for_area(entity, area_item.id)
        # 有设备才处理
        for entity_item in entity_list:
            state = hass.states.get(entity_item.entity_id)
            # 过滤无效设置
            if state.state == 'unavailable':
                continue
            attributes = state.attributes
            entity_id = state.entity_id
            domain = state.domain
            # 过滤名称
            friendly_name = attributes.get('device_name', attributes.get('friendly_name'))
            if friendly_name is None:
                continue
            # 设备类型
            device_type = None
            # 默认开关操作
            actions = ["turnOn", "timingTurnOn", "turnOff", "timingTurnOff", "getTurnOnState"]
            if domain == 'switch' or domain == 'input_boolean':
                # 开关
                device_type = 'SWITCH'
            elif domain == 'light':
                # 灯
                device_type = 'LIGHT'
                actions.extend(["setBrightnessPercentage", "incrementBrightnessPercentage", "decrementBrightnessPercentage", \
                    "incrementColorTemperature", "decrementColorTemperature", "setColorTemperature", "setColor"])
            elif domain == 'climate':
                # 空调
                device_type = 'AIR_CONDITION'
                actions.extend(["incrementTemperature", "decrementTemperature", "setTemperature", \
                    "incrementFanSpeed", "decrementFanSpeed", "setFanSpeed", "setGear", "setMode"])
            elif domain == 'cover':
                actions.extend(['pause'])
                # 窗帘 和 晾衣架
                if '窗帘' in friendly_name:
                    device_type = 'CURTAIN'
                elif '晾衣架' in friendly_name:
                    device_type = 'CLOTHES_RACK'
                    actions.extend(['incrementHeight', 'decrementHeight'])
            elif domain == 'media_player':
                actions.extend(['pause', 'continue', 'incrementVolume', 'decrementVolume', 'setVolume', 'setVolumeMute'])
                if '电视' in friendly_name:
                    device_type = 'TV_SET'
                    actions.extend(['decrementTVChannel', 'incrementTVChannel', 'setTVChannel', 'returnTVChannel'])
            elif domain == 'fan':
                actions.extend(['incrementFanSpeed', 'decrementFanSpeed', 'setFanSpeed', 'setGear', \
                    'setMode', 'unSetMode', 'timingSetMode', 'timingUnsetMode', \
                    'getTemperatureReading', 'getAirPM25', 'getAirPM10', 'getCO2Quantity', 'getAirQualityIndex', 'getTemperature', \
                    'getTargetTemperature', 'getHumidity', 'getTargetHumidity'])
                if '空气净化器' in friendly_name:
                    device_type = 'AIR_PURIFIER'
                if '风扇' in friendly_name:
                    device_type = 'FAN'
            elif domain == 'scene':
                device_type = 'SCENE_TRIGGER'

            # 不支持设备
            if device_type is None:
                continue
            attrs = entity_attributes(hass, entity_id)
            attrs.extend([{
                "name": "location",
                "value": area_item.name,
                "scale": "",
                "timestampOfSample": date_now(),
                "uncertaintyInMilliseconds": 10,
                "legalValue": "STRING"
            }])
            devices.append({
                'applianceId': entity_id,
                'friendlyName': friendly_name,
                'friendlyDescription': friendly_name,
                'additionalApplianceDetails': {},
                'applianceTypes': [ device_type ],
                'isReachable': True,
                'manufacturerName': 'HomeAssistant',
                'modelName': domain,
                'version': '1.0',
                'actions': actions,
                'attributes': attrs
            })

    return {'discoveredAppliances': devices}


# 控制设备
async def controlDevice(hass, action, payload):
    applianceDic = payload['appliance']
    additionalApplianceDetails = applianceDic.get('additionalApplianceDetails', {})
    # 实体ID
    entity_id = applianceDic['applianceId']
    domain = entity_id.split('.')[0]
    # 单位秒
    timestamp = payload.get('timestamp')
    # 亮度
    if 'brightness' in payload:
        brightness = payload['brightness']['value']
    # 增量百分比
    if 'deltaPercentage' in payload:
        deltaPercentage = payload['deltaPercentage']['value']
    # 定时
    timeInterval = payload.get('timeInterval')
    # 高度
    deltValue = payload.get('deltValue')
    # 色温
    colorTemperatureInKelvin = payload.get('colorTemperatureInKelvin')
    print(action)
    # 服务名称
    ################ 打开关闭设备
    if action == 'TurnOnRequest':
        return call_service(hass, domain + '.turn_on', {'entity_id': entity_id})
    elif action == 'TurnOffRequest':
        return call_service(hass, domain + '.turn_off', {'entity_id': entity_id})
    elif action == 'TimingTurnOnRequest':
        print('定时打开')
    elif action == 'TimingTurnOffRequest':
        print('定时关闭')
        service_name = 'turn_off'
    elif action == 'PauseRequest':
        # 暂停
        print('暂停')
    elif action == 'ContinueRequest':
        # 继续
        print('继续')
    elif action == 'StartUpRequest':
        # 启动
        print('启动')
    ################ 可控灯光设备
    elif action == 'SetBrightnessPercentageRequest':
        # 亮度
        result = call_service(hass, 'light.turn_on', {
            'entity_id': entity_id,
            'brightness_pct': brightness
        })
        result.update({
            "previousState": {
                "brightness": {
                    "value": 50
                }
            },
            "brightness": {
                "value": 100
            }
        })
        return result
    elif action == 'IncrementBrightnessPercentageRequest':
        # 增加亮度
        result = call_service(hass, 'light.turn_on', {
            'entity_id': entity_id,
            'brightness_step_pct': deltaPercentage
        })
        state = hass.states.get(entity_id)
        result.update({
            "previousState": {
                "brightness": {
                    "value": 50
                }
            },
            "brightness": {
                "value": int(state.attributes.get('brightness', 255) / 255 * 100)
            }
        })
        return result
    elif action == 'DecrementBrightnessPercentageRequest':
        # 减少亮度
        result = call_service(hass, 'light.turn_on', {
            'entity_id': entity_id,
            'brightness_step_pct': -deltaPercentage
        })
        state = hass.states.get(entity_id)
        result.update({
            "previousState": {
                "brightness": {
                    "value": 50
                }
            },
            "brightness": {
                "value": int(state.attributes.get('brightness', 255) / 255 * 100)
            }
        })
        return result
    elif action == 'SetColorRequest':
        # 启动
        color = payload['color']
        print(color['hue'], color['saturation'], color['brightness'])
    elif action == 'IncrementColorTemperatureRequest':
        print('增加色温')
    elif action == 'DecrementColorTemperatureRequest':
        print('减少色温')
    elif action == 'SetColorTemperatureRequest':
        # '设置色温'
        return call_service(hass, 'light.turn_on', {
            'entity_id': entity_id,
            'kelvin': colorTemperatureInKelvin
        })
    '''
    ################ 可控温度设备    
    elif action == 'IncrementTemperatureRequest':
    elif action == 'DecrementTemperatureRequest':
    elif action == 'SetTemperatureRequest':
    ################ 可控风速设备
    elif action == 'IncrementFanSpeedRequest':
    elif action == 'DecrementFanSpeedRequest':
    elif action == 'SetFanSpeedRequest':
    ################ 可控速度设备
    elif action == 'IncrementSpeedRequest':
    elif action == 'DecrementSpeedRequest':
    elif action == 'SetSpeedRequest':
    ################ 设备模式设置
    elif action == 'SetModeRequest':
    elif action == 'UnsetModeRequest':
    elif action == 'TimingSetModeRequest':
    ################ 电视频道设置
    elif action == 'IncrementTVChannelRequest':
    elif action == 'DecrementTVChannelRequest':
    elif action == 'SetTVChannelRequest':
    elif action == 'ReturnTVChannelRequest':
    ################ 可控音量设备
    elif action == 'IncrementVolumeRequest':
    elif action == 'DecrementVolumeRequest':
    elif action == 'SetVolumeRequest':
    elif action == 'SetVolumeMuteRequest':
    ################ 可锁定设备
    elif action == 'SetLockStateRequest':
    ################ 打印设备
    elif action == 'SubmitPrintRequest':
    ################ 可控吸力设备
    elif action == 'SetSuctionRequest':
    ################ 可控水量设备
    elif action == 'SetWaterLevelRequest':
    ################ 可控电量设备
    elif action == 'ChargeRequest':
    elif action == 'DischargeRequest':
    ################ 可控方向设备
    elif action == 'SetDirectionRequest':
    elif action == 'SetCleaningLocationRequest':
    elif action == 'SetComplexActionsRequest':
    ################ 可控高度设备
    elif action == 'IncrementHeightRequest':
        # 晾衣架调高
    elif action == 'DecrementHeightRequest':
        # 晾衣架调低
    ################ 可控定时设备
    elif action == 'SetTimerRequest':
        # 定时
        timeInterval = payload['timeInterval']
    elif action == 'TimingCancelRequest':
        # 取消定时
    ################ 可复位设备
    elif action == 'ResetRequset':
    ################ 可控楼层设备
    elif action == 'SetFloorRequest':
    elif action == 'IncrementFloorRequest':
    elif action == 'DecrementFloorRequest':
    ################ 可控湿度类设备
    elif action == 'SetHumidityRequest':
    '''
    return errorResult('IOT_DEVICE_OFFLINE')

# 查询设备
def queryDevice(hass, name, payload):
    applianceDic = payload['appliance']
    additionalApplianceDetails = applianceDic.get('additionalApplianceDetails', {})
    # 实体ID
    entity_id = applianceDic['applianceId']
    state = hass.states.get(entity_id)
    attributes = state.attributes
    if name == 'GetTemperatureReadingRequest':
        return {
            "temperatureReading": {
                "value": state.state,
                "scale": "CELSIUS"
            },
            "applianceResponseTimestamp": date_now()
        }

    return {
        'attributes': [
            {
                "name": "turnOnState",
                "value": state.state.upper(),
                "scale": "",
                "timestampOfSample":date_now(),
                "uncertaintyInMilliseconds": 10
            }
        ]
    }