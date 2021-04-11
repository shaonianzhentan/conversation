import time, re
import homeassistant.util.color as color_util
from homeassistant.helpers import template, entity_registry, area_registry, device_registry

'''
区域：https://open.bot.tmall.com/oauth/api/placelist
设备类型：https://doc-bot.tmall.com/docs/doc.htm?treeId=393&articleId=108271&docType=1
新版文档：https://www.yuque.com/qw5nze/ga14hc/cmhq2c
'''

def discoveryDevice(hass):
    # 获取所有设备    
    devices = []
    states = hass.states.async_all()
    for state in states:
        # 过滤无效设置
        if state.state == 'unavailable':
            continue
        attributes = state.attributes
        entity_id = state.entity_id
        domain = attributes.get('tmall_domain', state.domain)
        # 过滤空名称
        friendly_name = get_friendly_name(attributes)
        if friendly_name is None:
            continue
        # 过滤非中文名称
        if re.match(r'^[\u4e00-\u9fff]+$', friendly_name) is None:
            continue
        # 设备类型
        device_type = attributes.get('tmall_type')
        if domain == 'switch' or domain == 'input_boolean':
            # 开关
            device_type = attributes.get('tmall_type', 'switch')
        elif domain == 'light':
            device_type = 'light'
        elif domain == 'climate':
            # 空调
            device_type = 'aircondition'
        elif domain == 'cover':
            # 窗帘 和 晾衣架
            if '窗帘' in friendly_name:
                device_type = 'curtain'
            elif '晾衣架' in friendly_name:
                device_type = 'hanger'
        elif domain == 'media_player':
            if '电视' in friendly_name:
                device_type = 'television'
        elif domain == 'fan':
            if '净化' in friendly_name:
                device_type = 'airpurifier'
            if '扇' in friendly_name:
                device_type = 'fan'
        elif domain == 'camera':
            device_type = 'camera'
        elif domain == 'sensor':
            device_type = 'sensor'
        # 不支持设备
        if device_type is None:
            continue

        # 添加设备
        devices.append({
            'deviceId': entity_id,
            'deviceName': friendly_name,
            'deviceType': device_type,
            'brand': 'HASSKIT',
            'model': 'x1',
            'zone': '',
            "status": get_attributes(state),
            "extensions": {}
        })
    return {'devices': devices}

async def controlDevice(hass, action, payload):
    deviceResponseList = []
    deviceIds = payload['deviceIds']
    params = payload['params']
    powerstate = params.get('powerstate')
    brightness = params.get('brightness')
    # 根据设备ID，找到对应的实体ID
    for entity_id in deviceIds:
        service_name = None
        service_data = {'entity_id': entity_id}
        state = hass.states.get(entity_id)
        attributes = state.attributes
        # 设置属性
        if action == 'thing.attribute.set':
            if powerstate == 1:
                service_name = 'turn_on'
            elif powerstate == 0:
                service_name = 'turn_off'
            # 设置亮度
            if brightness is not None:
                service_data.update({'brightness_pct': brightness})
        elif action == 'thing.attribute.adjust':
            # 增加/减少亮度
            if brightness is not None:
                service_data.update({'brightness_pct': int(attributes.get('brightness', 255) / 255 * 100) + brightness})

        if service_name is not None:
            hass.async_create_task(hass.services.async_call(state.domain, service_name, service_data))
        
        # 返回结果
        deviceResponseList.append({
            "deviceId": entity_id,
            "errorCode": "SUCCESS",
            "message": "SUCCESS"
        })
    return deviceResponseList

def queryDevice(name, payload):
    deviceId = payload['deviceId']
    deviceType = payload['deviceType']
    return errorResult('IOT_DEVICE_OFFLINE')

# 获取名称
def get_friendly_name(attributes):
    return attributes.get('tmall_name', attributes.get('friendly_name'))

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

# 获取默认属性
def get_attributes(state, default_state=None):
    status = {}
    domain = state.domain
    attributes = state.attributes
    if state.state.upper() == 'ON':
        status.update({ powerstate: 1 })
    else if state.state.upper() == 'OFF':
        status.update({ powerstate: 0 })

    if domain == 'light':
        brightness = attributes.get('brightness', 255)
        status.update({ brightness: int(brightness / 255 * 100) })
        
    return status