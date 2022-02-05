import time, re, logging
import homeassistant.util.color as color_util
from homeassistant.helpers import template, entity_registry, area_registry, device_registry

_LOGGER = logging.getLogger(__name__)
'''
区域：https://open.bot.tmall.com/oauth/api/placelist
设备类型：https://doc-bot.tmall.com/docs/doc.htm?treeId=393&articleId=108271&docType=1
新版文档：https://www.yuque.com/qw5nze/ga14hc/cmhq2c
'''

# 发现设备
area_entity = {}
async def discoveryDevice(hass):
    # 获取所有区域
    area = await area_registry.async_get_registry(hass)
    area_list = area.async_list_areas()
    for area_item in area_list:
        # 获取区域实体
        entity = await entity_registry.async_get_registry(hass)
        entity_list = entity_registry.async_entries_for_area(entity, area_item.id)
        for entity_item in entity_list:
            area_entity.update({
                entity_item.entity_id: area_item.name
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
        '''
        elif domain == 'sensor':
            device_type = 'sensor'
        '''
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
            'zone': area_entity.get(entity_id, ''),
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
    motorControl = params.get('motorControl')
    volume = params.get('volume')
    muteMode = params.get('muteMode')
    playControl = params.get('playControl')
    # 颜色转换
    color = get_color_name(params.get('color'))
    # 电视频道
    if 'channelName' in params:
        channelName = get_tv_name(params.get('channelName'))
    # 根据设备ID，找到对应的实体ID
    for entity_id in deviceIds:
        service_name = None
        service_data = {'entity_id': entity_id}
        state = hass.states.get(entity_id)
        attributes = state.attributes
        domain = state.domain
        # 查询属性
        if action == 'thing.attribute.get':
            print('查询')
        else:
            # 设置属性
            if action == 'thing.attribute.set':
                if powerstate == 1:
                    service_name = 'turn_on'
                elif powerstate == 0:
                    service_name = 'turn_off'
                # 设置亮度
                if brightness is not None:
                    service_name = 'turn_on'
                    service_data.update({'brightness_pct': brightness})
                # 设置颜色
                if color is not None:
                    service_name = 'turn_on'
                    service_data.update({'rgb_color': color_util.color_name_to_rgb(color)})
                # 设置电机控制
                if motorControl is not None:
                    # 判断是否晾衣架
                    if domain == 'cover':
                        if motorControl == 0:
                            service_name = 'stop_cover'
                        elif motorControl == 1:
                            service_name = 'open_cover'
                        elif motorControl == 2:
                            service_name = 'close_cover'
                # 媒体播放器
                if domain == 'media_player':
                    # 设置音量
                    if volume is not None:
                        if volume == -1:
                            # 声音小
                            service_name = 'volume_down'
                        elif volume == 1:
                            # 声音大
                            service_name = 'volume_up'
                        else:
                            service_name = 'volume_set'
                            service_data.update({'volume_level': volume / 100})
                    # 静音
                    if muteMode is not None:
                        service_name = 'volume_mute'
                        service_data.update({'is_volume_muted': muteMode == 1})
                    # 播放控制
                    if playControl is not None:
                        if playControl == 1:
                            service_name = 'media_play'
                        elif playControl == 2:
                            service_name = 'media_pause'
                        elif playControl == 3:
                            service_name = 'media_previous_track'
                        elif playControl == 4:
                            service_name = 'media_next_track'
            elif action == 'thing.attribute.adjust':
                # 增加/减少亮度
                if brightness is not None:
                    service_name = 'turn_on'
                    service_data.update({'brightness_pct': int(attributes.get('brightness', 255) / 255 * 100) + brightness})

            if service_name is not None:
                # 脚本执行
                if domain == 'script':
                    service_name = entity_id.split('.')[1]
                    service_data = {}
                _LOGGER.debug('执行服务：' + domain + '.' + service_name)
                hass.async_create_task(hass.services.async_call(domain, service_name, service_data))
            else:        
                # 天猫事件数据
                tmall_data = {
                    'type': action,
                    'domain': domain,
                    'entity_id': entity_id
                }
                tmall_data.update(params)
                hass.bus.async_fire("tmall_event", tmall_data)
        # 返回结果
        deviceResponseList.append({
            "deviceId": entity_id,
            "errorCode": "SUCCESS",
            "message": "SUCCESS"
        })
    return { "deviceResponseList": deviceResponseList }

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
    state_value = state.state.upper()
    if state_value == 'ON':
        status.update({ 'powerstate': 1 })
    elif state_value == 'OFF':
        status.update({ 'powerstate': 0 })

    if domain == 'light':
        brightness = attributes.get('brightness', 255)
        status.update({ 'brightness': int(brightness / 255 * 100) })
        
    return status

# 获取颜色名称
def get_color_name(tmall_color):
    obj = {
        16711680: 'red',
        16753920: 'orange',
        16776960: 'yellow',
        65280: 'green',
        65535: 'cyan',
        255: 'blue',
        8388736: 'purple',
        16761035: 'pink',
        16777215: 'white',
        0: 'black',
        8900331: 'skyblue', # 天蓝色
        139: 'darkblue', # 深蓝色
        35723: 'darkcyan', # 深青色
    }
    return obj.get(tmall_color)

# 获取频道名称
def get_tv_name(tmall_tv):
    obj = {
        1: '浙江卫视',
        2: '湖南卫视',
        95: 'CCTV1',
        96: 'CCTV2',
        97: 'CCTV3',
        98: 'CCTV4',
        99: 'CCTV5',
        100: 'CCTV6',
        101: 'CCTV7',
        103: 'CCTV8',
        104: 'CCTV9',
        105: 'CCTV10',
        106: 'CCTV11',
        107: 'CCTV12',
        108: 'CCTV13',
        109: 'CCTV14',
        110: 'CCTV15',
        113: '东方卫视',
        119: '湖北卫视',
    }
    return obj.get(tmall_tv)