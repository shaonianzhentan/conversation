import time, re
import homeassistant.util.color as color_util
from homeassistant.helpers import template, entity_registry, area_registry, device_registry

# 发现设备
area_entity = {}
async def discoveryDevice(hass):    
    timestampOfSample = date_now()
    # 获取所有区域
    area = await area_registry.async_get_registry(hass)
    area_list = area.async_list_areas()
    for area_item in area_list:
        # 获取设备
        # entity = await device_registry.async_get_registry(hass)
        # entity_list = device_registry.async_entries_for_area(entity, area_item.id)
        # 获取区域实体
        entity = await entity_registry.async_get_registry(hass)
        entity_list = entity_registry.async_entries_for_area(entity, area_item.id)
        for entity_item in entity_list:
            area_entity.update({
                entity_item.entity_id: {
                        "name": "location",
                        "value": area_item.name,
                        "scale": "",
                        "timestampOfSample": timestampOfSample,
                        "uncertaintyInMilliseconds": 10,
                        "legalValue": "STRING"
                    }
            })
    
    # 获取所有设备    
    devices = []
    states = hass.states.async_all()
    for state in states:
        # 过滤无效设置
        if state.state == 'unavailable':
            continue
        attributes = state.attributes
        entity_id = state.entity_id
        domain = attributes.get('xiaodu_domain', state.domain)
        # 过滤空名称
        friendly_name = get_friendly_name(attributes)
        if friendly_name is None:
            continue
        # 过滤非中文名称
        if re.match(r'^[\u4e00-\u9fff]+$', friendly_name) is None:
            continue
        # 设备类型
        device_type = attributes.get('xiaodu_type')
        # 默认开关操作
        actions = ['setMode', 'unSetMode', 'timingSetMode', 'timingUnsetMode', \
            "turnOn", "timingTurnOn", "turnOff", "timingTurnOff", "getTurnOnState", "setComplexActions", "getLocation"]
        if domain == 'switch' or domain == 'input_boolean':
            # 开关
            device_type = attributes.get('xiaodu_type', 'SWITCH')
        elif domain == 'light':
            # 灯
            device_type = 'LIGHT'
            actions.extend(["setBrightnessPercentage", "incrementBrightnessPercentage", "decrementBrightnessPercentage", \
                "incrementColorTemperature", "decrementColorTemperature", "setColorTemperature", "setColor"])
        elif domain == 'climate':
            # 空调
            device_type = 'AIR_CONDITION'
            actions.extend(["incrementTemperature", "decrementTemperature", "setTemperature", \
                'getTemperatureReading', 'getTemperature', 'getTargetTemperature', 'getHumidity', 'getTargetHumidity', \
                "incrementFanSpeed", "decrementFanSpeed", "setFanSpeed", "setGear"])
        elif domain == 'cover':
            actions.extend(['pause', 'continue', 'setDirection'])
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
                'getTemperatureReading', 'getAirPM25', 'getAirPM10', 'getCO2Quantity', 'getAirQualityIndex', 'getTemperature', \
                'getTargetTemperature', 'getHumidity', 'getTargetHumidity'])
            if '净化' in friendly_name:
                device_type = 'AIR_PURIFIER'
            if '扇' in friendly_name:
                device_type = 'FAN'
        elif domain == 'scene':
            device_type = 'SCENE_TRIGGER'
        elif domain == 'camera':
            device_type = attributes.get('xiaodu_type', 'WEBCAM')
            actions.extend(['setDirection', 'reset'])
        # elif domain == 'script':
        #    device_type = 'ACTIVITY_TRIGGER'
        elif domain == 'sensor':
            # ['getTargetHumidity', 'getTemperatureReading', 'getTargetTemperature']
            if '温度传感器' == friendly_name:
                device_type = 'AIR_MONITOR'
                actions = ['getTemperature', 'getTemperatureReading']
            elif '湿度传感器' == friendly_name:
                device_type = 'AIR_MONITOR'
                actions = ['getHumidity']
        # 不支持设备
        if device_type is None:
            continue

        # 移除开关操作
        if ['sensor'].count(domain) > 0:
            remove_action(actions, 'turnOff')
            remove_action(actions, 'timingTurnOff')

        # 添加设备
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
            'attributes': get_attributes(state)
        })
    return {'discoveredAppliances': devices}


# 控制设备
async def controlDevice(hass, action, payload):
    applianceDic = payload['appliance']
    additionalApplianceDetails = applianceDic.get('additionalApplianceDetails', {})
    # 实体ID
    entity_id = applianceDic['applianceId']
    # 服务数据
    service_data = { 'entity_id': entity_id }
    state = hass.states.get(entity_id)
    domain = entity_id.split('.')[0]   
    # 小度事件数据
    xiaodu_data = {
        'type': action,
        'domain': domain,
        'entity_id': entity_id
    }
    # 高度
    if 'deltValue' in payload:
        deltValue = payload.get('deltValue')
        if isinstance(deltValue, dict):
            deltValue = deltValue['value']
        xiaodu_data.update({'deltValue': deltValue})
    # 温度
    if 'deltaValue' in payload:
        deltaValue = payload.get('deltaValue')
        if isinstance(deltaValue, dict):
            deltaValue = deltaValue['value']
        xiaodu_data.update({'deltaValue': deltaValue})
    # 颜色
    if 'color' in payload:
        xiaodu_data.update({'color': payload['color']})
    # 色温
    if 'colorTemperatureInKelvin' in payload:
        xiaodu_data.update({'colorTemperatureInKelvin': payload['colorTemperatureInKelvin']})
    # 单位秒
    if 'timestamp' in payload:
        xiaodu_data.update({'timestamp': payload['timestamp']})
    # 定时
    if 'timeInterval' in payload:
        xiaodu_data.update({'timeInterval': payload['timeInterval']})
    # 亮度
    if 'brightness' in payload:
        xiaodu_data.update({'brightness': payload['brightness']['value']})
    # 增量百分比
    if 'deltaPercentage' in payload:
        xiaodu_data.update({'deltaPercentage': payload['deltaPercentage']['value']})
    # 模式
    if 'mode' in payload:
        xiaodu_data.update({'mode': payload['mode']['value']})
    # 风速
    if 'fanSpeed' in payload:
        xiaodu_data.update({'fanSpeed': payload['fanSpeed']['value']})
    # 温度
    if 'targetTemperature' in payload:
        xiaodu_data.update({'targetTemperature': payload['targetTemperature']['value']})
    
    # 服务名称
    ################ 打开关闭设备
    if action == 'TurnOnRequest':
        return call_service(hass, domain + '.turn_on', service_data)
    elif action == 'TurnOffRequest':
        return call_service(hass, domain + '.turn_off', service_data)
    elif action == 'TimingTurnOnRequest':
        return call_service(hass, domain + '.turn_on', service_data)
    elif action == 'TimingTurnOffRequest':
        return call_service(hass, domain + '.turn_off', service_data)
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
        service_data.update({ 'brightness_pct': xiaodu_data['brightness'] })
        result = call_service(hass, 'light.turn_on', service_data)
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
        service_data.update({ 'brightness_step_pct': xiaodu_data['deltaPercentage'] })
        result = call_service(hass, 'light.turn_on', service_data)
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
        service_data.update({ 'brightness_step_pct': -xiaodu_data['deltaPercentage'] })
        result = call_service(hass, 'light.turn_on', service_data)
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
        color = xiaodu_data['color']
        service_data.update({ 'rgb_color': color_util.color_hsb_to_RGB(color['hue'], color['saturation'], color['brightness']) })
        return call_service(hass, 'light.turn_on', service_data) 
    elif action == 'IncrementColorTemperatureRequest':
        print('增加色温')
    elif action == 'DecrementColorTemperatureRequest':
        print('减少色温')
    elif action == 'SetColorTemperatureRequest':
        # 设置色温
        print('设置色温', xiaodu_data['colorTemperatureInKelvin'])
    ################ 可控温度设备    
    elif action == 'IncrementTemperatureRequest':
        service_data.update({ 'temperature': state.attributes.get('temperature') + deltaValue })
        return call_service(hass, 'climate.set_temperature', service_data)
    elif action == 'DecrementTemperatureRequest':
        service_data.update({ 'temperature': state.attributes.get('temperature') - deltaValue })
        return call_service(hass, 'climate.set_temperature', service_data)
    elif action == 'SetTemperatureRequest':
        service_data.update({ 'temperature': xiaodu_data['targetTemperature'] })
        return call_service(hass, 'climate.set_temperature', service_data)
    ################ 设备模式设置
    elif action == 'SetModeRequest':
        mode = xiaodu_data['mode']
        # 空调
        if domain == 'climate':
            '''
            # 上下摆风
            if mode == 'UP_DOWN_SWING':
                return call_service(hass, 'climate.set_swing_mode', {'entity_id': entity_id, 'hvac_mode': mode.lower()})
            # 左右摆风
            elif mode == 'LEFT_RIGHT_SWING':
                return call_service(hass, 'climate.set_swing_mode', {'entity_id': entity_id, 'hvac_mode': mode.lower()})
            '''
            if mode == 'COOL' or mode == 'HEAT' or mode == 'AUTO':
                service_data.update({ 'hvac_mode': mode.lower() })
                return call_service(hass, 'climate.set_hvac_mode', service_data)
        # 电视
        elif domain == 'media_player':
            if mode == 'MUTE':
                service_data.update({ 'is_volume_muted': True })
                return call_service(hass, 'media_player.volume_mute', service_data)
    elif action == 'UnsetModeRequest':
        # 空调
        if domain == 'climate':
            service_data.update({ 'hvac_mode': 'auto' })
            return call_service(hass, 'climate.set_hvac_mode', service_data)
    elif action == 'TimingSetModeRequest':
        # 空调
        if domain == 'climate':
            mode = xiaodu_data['mode']
            if mode == 'COOL' or mode == 'HEAT' or mode == 'AUTO':
                service_data.update({ 'hvac_mode': mode.lower() })
                return call_service(hass, 'climate.set_hvac_mode', service_data)
    ################ 可控风速设备
    elif action == 'IncrementFanSpeedRequest':
        # 空调
        if domain == 'climate':
            service_data.update({ 'hvac_mode': 'high' })
            return call_service(hass, 'climate.set_fan_mode', service_data)
    elif action == 'DecrementFanSpeedRequest':
        # 空调
        if domain == 'climate':
            service_data.update({ 'hvac_mode': 'low' })
            return call_service(hass, 'climate.set_fan_mode', service_data)
    elif action == 'SetFanSpeedRequest':
        print('设置风速')
    ################ 可控音量设备
    elif action == 'IncrementVolumeRequest':
        # 电视
        if domain == 'media_player':
            return call_service(hass, 'media_player.volume_up', service_data)
    elif action == 'DecrementVolumeRequest':
        # 电视
        if domain == 'media_player':
            return call_service(hass, 'media_player.volume_down', service_data)
    elif action == 'SetVolumeRequest':
        # 电视
        if domain == 'media_player':
            service_data.update({ 'volume_level': deltaValue / 100 })
            return call_service(hass, 'media_player.volume_set', service_data)
    elif action == 'SetVolumeMuteRequest':
        # 电视
        if domain == 'media_player':
            service_data.update({ 'is_volume_muted': deltaValue == 'on' })
            return call_service(hass, 'media_player.volume_mute', service_data)
    ################ 电视频道设置
    elif action == 'IncrementTVChannelRequest':
        print('上一个频道')
    elif action == 'DecrementTVChannelRequest':
        print('下一个频道')
    elif action == 'SetTVChannelRequest':
        print(f'播放指定频道: {deltaValue}')
    elif action == 'ReturnTVChannelRequest':
        print('返回上一个观看频道')
    ################ 可控高度设备
    elif action == 'IncrementHeightRequest':
        # 晾衣架调高
        if domain == 'cover':
            return call_service(hass, 'cover.close_cover', service_data)
    elif action == 'DecrementHeightRequest':
        # 晾衣架调低
        if domain == 'cover':
            return call_service(hass, 'cover.open_cover', service_data)
    '''
    ################ 可控速度设备
    elif action == 'IncrementSpeedRequest':
    elif action == 'DecrementSpeedRequest':
    elif action == 'SetSpeedRequest':
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
    ################ 可控定时设备
    elif action == 'SetTimerRequest':
        # 定时
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
    # 发送事件
    hass.bus.async_fire("xiaodu_event", xiaodu_data)
    # 调用python_script
    if hass.services.has_service('python_script', 'xiaodu_event'):
        hass.async_create_task(hass.services.async_call('python_script', 'xiaodu_event', xiaodu_data))
    return {
        "attributes": []
    }

# 查询设备
def queryDevice(hass, name, payload):
    applianceDic = payload['appliance']
    additionalApplianceDetails = applianceDic.get('additionalApplianceDetails', {})
    # 实体ID
    entity_id = applianceDic['applianceId']
    state = hass.states.get(entity_id)
    attributes = state.attributes
    value = state.state
    if name == 'GetTemperatureReadingRequest' or name == 'GetTargetTemperatureRequest':
        # 查询设备温度
        xiaodu_entity_id = attributes.get('xiaodu_temperature')
        if xiaodu_entity_id is not None:
            value = hass.states.get(xiaodu_entity_id).state
        else:
            if state.domain == 'fan':
                value = attributes.get('temperature')
            if state.domain == 'climate':
                value = attributes.get('current_temperature', 0)
        return {
            "temperatureReading": {
                "value": value,
                "scale": "CELSIUS"
            },
            "applianceResponseTimestamp": date_now()
        }
    elif name == 'GetHumidityRequest' or name == 'GetTargetHumidityRequest':
        # 查询设备湿度
        xiaodu_entity_id = attributes.get('xiaodu_humidity')
        if xiaodu_entity_id is not None:
            value = hass.states.get(xiaodu_entity_id).state
        else:
            if state.domain == 'fan':
                value = attributes.get('humidity')
        return {
            "attributes": [{
                "name": "humidity",
                "value": value,
                "scale": "%",
                "timestampOfSample":date_now(),
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }]
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

# 移除操作
def remove_action(actions, name):
    if actions.count(name) > 0:
        actions.remove(name)
        
# 获取名称
def get_friendly_name(attributes):
    return attributes.get('xiaodu_name', attributes.get('friendly_name'))

# 获取默认属性
def get_attributes(state, default_state=None):
    domain = state.domain
    attributes = state.attributes
    friendly_name = get_friendly_name(attributes)
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
            "name": "connectivity",
            "value": "REACHABLE",
            "scale": "",
            "timestampOfSample": timestampOfSample,
            "uncertaintyInMilliseconds": 10,
            "legalValue": "(UNREACHABLE, REACHABLE)"
        }
    ]
    if default_state is None:
        default_state = state.state.upper()
    # [传感器、场景]没有开关
    if ['sensor'].count(domain) == 0:
        attrs.extend([
            {
                "name": "powerState",
                "value": default_state,
                "scale": "",
                "timestampOfSample": timestampOfSample,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "(ON, OFF)"
            },
            {
                "name": "turnOnState",
                "value": default_state,
                "scale": "",
                "timestampOfSample": timestampOfSample,
                "uncertaintyInMilliseconds": 10
            },
        ])

    if domain == 'light':
        brightness = attributes.get('brightness', 255)
        attrs.append(
            {
                "name": "brightness",
                "value": int(brightness / 255 * 100),
                "scale": "%",
                "timestampOfSample": timestampOfSample,
                "uncertaintyInMilliseconds": 10,
                "legalValue": "[0, 100]"
            }
        )
    # 加入区域属性
    area_entity_attrs = area_entity.get(state.entity_id)
    if area_entity_attrs is not None:
        attrs.append(area_entity_attrs)
    return attrs


# 10位时间戳
def date_now():
    return int(time.time())

# 异步调用服务
def call_service(hass, service, data={}):
    arr = service.split('.')
    domain = arr[0]
    action = arr[1]
    entity_id = data['entity_id']
    state = hass.states.get(entity_id)
    powerState = state.state.upper()
    if action == 'turn_off':
        powerState = 'OFF'
    if action == 'turn_on':
        powerState = 'ON'
    
    # 脚本执行
    if domain == 'script':
        action = entity_id.split('.')[1]
        data = {}

    hass.async_create_task(hass.services.async_call(domain, action, data))
    
    return {
        'attributes': get_attributes(state, powerState)
    }
