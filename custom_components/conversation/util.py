"""Util for Conversation."""
import re, yaml
import string
import random
import json, os, aiohttp, uuid
from homeassistant.helpers import template, entity_registry, area_registry

def create_matcher(utterance):
    """Create a regex that matches the utterance."""
    # Split utterance into parts that are type: NORMAL, GROUP or OPTIONAL
    # Pattern matches (GROUP|OPTIONAL): Change light to [the color] {name}
    parts = re.split(r"({\w+}|\[[\w\s]+\] *)", utterance)
    # Pattern to extract name from GROUP part. Matches {name}
    group_matcher = re.compile(r"{(\w+)}")
    # Pattern to extract text from OPTIONAL part. Matches [the color]
    optional_matcher = re.compile(r"\[([\w ]+)\] *")

    pattern = ["^"]
    for part in parts:
        group_match = group_matcher.match(part)
        optional_match = optional_matcher.match(part)

        # Normal part
        if group_match is None and optional_match is None:
            pattern.append(part)
            continue

        # Group part
        if group_match is not None:
            pattern.append(r"(?P<{}>[\w ]+?)\s*".format(group_match.groups()[0]))

        # Optional part
        elif optional_match is not None:
            pattern.append(r"(?:{} *)?".format(optional_match.groups()[0]))

    pattern.append("$")
    return re.compile("".join(pattern), re.I)
# 获取本机MAC地址
def get_mac_address(): 
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
########################################## 常量
VERSION = '1.5.8'
DOMAIN = "conversation"
DATA_AGENT = "conversation_agent"
DATA_CONFIG = "conversation_config"
MAC_ADDRESS = get_mac_address().replace(':','').lower()
XIAOAI_API = f"/conversation-xiaoai-{MAC_ADDRESS}"
XIAODU_API = f"/conversation-xiaodu"
TMALL_API = f"/conversation-tmall"
ALIGENIE_API = f"/conversation-aligenie-{MAC_ADDRESS}"
VIDEO_API = '/conversation-video'
########################################## 查询实体
def isMatchDomain(type, domain):
    return type is None or (isinstance(type, list) and type.count(domain) == 1) or (isinstance(type, str) and type == domain)

async def find_entity(hass, name, type = None):
    # 遍历所有实体
    states = hass.states.async_all()
    for state in states:
        entity_id = state.entity_id
        domain = state.domain
        attributes = state.attributes
        friendly_name = attributes.get('friendly_name')
        # 查询对应的设备名称
        if friendly_name is not None and friendly_name.lower() == name.lower():
            # 指定类型
            if isMatchDomain(type, domain):
                return state
    # 如果没有匹配到实体，则开始从区域里查找
    arr = name.split('的', 1)
    if len(arr) == 2:
        area_name = arr[0]
        device_name = arr[1]
        # 获取所有区域
        area = await area_registry.async_get_registry(hass)
        area_list = area.async_list_areas()
        _list = list(filter(lambda item: item.name == area_name, area_list))
        if(len(_list) > 0):
            area_id = _list[0].id
            entity = await entity_registry.async_get_registry(hass)
            entity_list = entity_registry.async_entries_for_area(entity, area_id)
            # 有设备才处理
            if len(entity_list) > 0:
                # 查找完整设备
                _list = list(filter(lambda item: item.name == device_name or item.original_name == device_name, entity_list))
                if(len(_list) > 0):
                    # print(_list)
                    item = _list[0]
                    state = hass.states.get(item.entity_id)
                    if isMatchDomain(type, state.domain):
                        return state
                # 如果直接说了灯或开关
                if device_name == '灯':
                    # 如果只有一个设备
                    if len(entity_list) == 1:
                        item = entity_list[0]
                        state = hass.states.get(item.entity_id)
                        if isMatchDomain(type, state.domain):
                            return state
                    else:
                        # 取第一个含有灯字的设备（这里可以通过其他属性来判断，以后再考虑）
                        for item in entity_list:
                            state = hass.states.get(item.entity_id)
                            friendly_name = state.attributes.get('friendly_name')
                            if '灯' in friendly_name and isMatchDomain(type, state.domain):
                                return state

########################################## 去掉前后标点符号
def trim_char(text):
    return text.strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')
########################################## 汉字转数字
common_used_numerals_tmp ={'零':0, '一':1, '二':2, '两':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '十':10, '百':100, '千':1000, '万':10000, '亿':100000000}
common_used_numerals = {}
for key in common_used_numerals_tmp:
  common_used_numerals[key.encode('cp936').decode('cp936')] = common_used_numerals_tmp[key]

def chinese2digits(uchars_chinese):
    try:
        uchars_chinese = uchars_chinese.encode('cp936').decode('cp936')
        total = 0
        r = 1              #表示单位：个十百千...
        for i in range(len(uchars_chinese) - 1, -1, -1):
            val = common_used_numerals.get(uchars_chinese[i])
            if val >= 10 and i == 0:  #应对 十三 十四 十*之类
                if val > r:
                    r = val
                    total = total + val
                else:
                    r = r * val
                #total =total + r * x
            elif val >= 10:
                if val > r:
                    r = val
                else:
                    r = r * val
            else:
                total = total + r * val
        return total
    except Exception as ex:
        return None

# 判断是否数字
def is_number(s):
    result = re.match(r'\d+', s)
    if result:
        return True
    else:
        return False

def format_number(num):
    if is_number(num) == False:
        num = chinese2digits(num)
    return float(num)

########################################## 颜色调整
def matcher_light_color(text):
    matchObj = re.match(r'(.+)(调成|设为|设置为|调为)(.*)色', text)
    if matchObj is not None:
        name = trim_char(matchObj.group(1)) 
        color = matchObj.group(3)
        colorObj = {
            '红': 'red',
            '橙': 'orange',
            '黄': 'yellow',
            '绿': 'green',
            '青': 'teal',
            '蓝': 'blue',
            '紫': 'purple',
            '粉': 'pink',
            '白': 'white',
            '紫红': 'fuchsia',
            '橄榄': 'olive'
        }
        # 设备
        if name[0:1] == '把':
            name = name[1:]
        # 随机颜色
        if color == '随机':
            color = random.choice(list(colorObj))
        # 固定颜色
        if color in colorObj:
            return (name, colorObj[color], color)

########################################## 模式调整
def matcher_light_mode(text):
    matchObj = re.match(r'(.+)(调成|设为|设置为|调为)(.*)模式', text)
    if matchObj is not None:
        name = trim_char(matchObj.group(1)) 
        mode = matchObj.group(3)
        modeObj = {
            '随机': 'Random',
            '闪光': 'Strobe',
            '闪烁': 'Twinkle',
            '顔色闪烁': 'Random Twinkle',
            '彩虹': 'Rainbow',
            '跑马灯': 'Color Wipe',
            '扫描': 'Scan',
            '烟火': 'Fireworks'
        }
        # 设备
        if name[0:1] == '把':
            name = name[1:]
        # 固定颜色
        if mode in modeObj:
            return (name, modeObj[mode], mode)

########################################## 亮度调整
def matcher_brightness(text):
    matchObj = re.match(r'(.+)亮度(调成|调到|调为|设为)(.*)', text)
    if matchObj is not None:
        name = trim_char(matchObj.group(1)) 
        brightness = matchObj.group(3)
        # print(brightness)
        # 设备
        if name[0:1] == '把':
            name = name[1:]
        if name[-1] == '的':
            name = name[:-1]
        # 判断是否数字，然后转意
        if re.match(r'^\d+$', brightness):
            brightness = int(brightness)
            if brightness > 100:
                brightness = 100
        # 亮度
        elif brightness == '最亮':
            brightness = 100
        elif brightness == '最暗':
            brightness = 1
        else:
            brightness = chinese2digits(brightness)
            if brightness is None:
                brightness = 0
        # 如果亮度大于0，返回设备名称和亮度值
        if brightness > 0:
            return (name, brightness)

########################################## 执行脚本
def matcher_script(text):
    matchObj = re.match(r'执行脚本(.*)', text)
    if matchObj is not None:
        return matchObj.group(1)

########################################## (执行|触发|打开|关闭|切换)自动化
def matcher_automation(text):
    matchObj = re.match(r'(执行|触发|打开|关闭|切换)自动化(.*)', text)
    if matchObj is not None:
        return (matchObj.group(1), trim_char(matchObj.group(2)))

########################################## 媒体播放器(播放|暂停|下一曲|上一曲)
def matcher_media_player(text):
    matchObj = re.match(r'(.*)(播放|暂停|下一曲|上一曲)', text)
    if matchObj is not None:
        return (matchObj.group(1), matchObj.group(2))

########################################## (执行|触发|打开|关闭)开关
def matcher_switch(text):
    action = None
    name = None
    # 把 设备 操作
    matchObj = re.match(r'.*把((.+)(打开|开启|启动|开一下|开下|关闭|关掉|关上|关一下|关下|切换))', text)
    if matchObj is not None:
        action = matchObj.group(3)
        name = matchObj.group(2)
    else:
        matchObj = re.match(r'.*((打开|开启|启动|开一下|开下|关闭|关掉|关上|关一下|关下|切换)(.+))', text)
        if matchObj is not None: 
            action = matchObj.group(2)
            name = matchObj.group(3)
    
    if action is not None:
        service_type = ''
        intent_type = ''
        if ['打开', '开启', '启动', '开一下', '开下'].count(action) == 1:
            service_type = 'turn_on'
            intent_type = 'HassTurnOn'
        elif ['关闭', '关掉', '关上', '关一下', '关下'].count(action) == 1:
            service_type = 'turn_off'
            intent_type = 'HassTurnOff'
        elif action == '切换':
            service_type = 'toggle'
            intent_type = 'HassToggle'
        
        if service_type != '' and intent_type != '':
            return (trim_char(name), service_type, intent_type, action)


########################################## (打开|关闭)设备(打开|关闭)设备
def matcher_on_off(text):
    matchObj = re.match(r'(打开|开一下|开下|关闭|关一下|关下)(.+)(打开|开一下|开下|关闭|关一下|关下)(.+)', text)
    if matchObj is not None:
        name1 = matchObj.group(2)
        name2 = matchObj.group(4)
        if name1 is not None and name2 is not None:
            type1 = ['打开', '开一下', '开下'].count(matchObj.group(1)) == 1 and 'turn_on' or 'turn_off'
            type2 = ['打开', '开一下', '开下'].count(matchObj.group(3)) == 1 and 'turn_on' or 'turn_off'
            _list1 = list(filter(lambda x: x != '', name1.split('和')))
            _list2 = list(filter(lambda x: x != '', name2.split('和')))
            return ((type1, _list1), (type2, _list2))

########################################## 查看设备状态
def matcher_query_state(text):
    matchObj = re.match(r'(查看|查询)(.*)的状态', text)
    if matchObj is not None:
        return trim_char(matchObj.group(2))

    matchObj = re.match(r'(查看|查询)(.*)', text)
    if matchObj is not None:
        return trim_char(matchObj.group(2))
    
    matchObj = re.match(r'(.*)的状态', text)
    if matchObj is not None:
        return trim_char(matchObj.group(1))

########################################## 看电视
# 视频源地址：https://raw.githubusercontent.com/Hunlongyu/ZY-Player/master/src/lib/dexie/iniData/Iptv.json
def matcher_watch_tv(text):
    matchObj = re.match(r'打开中央(.+)台', text)
    if matchObj is not None:
        num = format_number(matchObj.group(1))
        if num >= 1 and num <= 17 and num != 16:
            return f'CCTV{num}'

    matchObj = re.match(r'打开(湖北|湖南|四川|吉林|海南|东南|广东|江苏|东方|云南|北京|浙江|天津|广西|山东|安徽|辽宁|重庆|陕西|北京)卫视', text)
    if matchObj is not None:
        name = matchObj.group(1)
        return f'{name}卫视'

def matcher_watch_video(text):
    matchObj = re.match(r'打开电视剧(.+)第(.+)集', text)
    if matchObj is not None:
        name = matchObj.group(1)
        num = int(format_number(matchObj.group(2)))
        if name is not None and num is not None:
            return (name, num)

def matcher_watch_movie(text):
    matchObj = re.match(r'打开电影(.+)', text)
    if matchObj is not None:
        name = matchObj.group(1)
        if name is not None:
            return (name)

async def http_code(url):
    async with aiohttp.request("GET", url) as response:
        return response.status

async def http_get(url):
    async with aiohttp.request("GET", url) as response:
        return json.loads(await response.text())

# 获取本地视频链接
async def get_local_video_url(video_path, name, num):
    if video_path == '':
        return None
    _url = f'{video_path}/{name}'
    print(f'查找资源：')
    # 判断是否为链接
    if video_path[:4] == 'http':
        # 暂时还没想好怎么处理
        return None
    elif os.path.exists(_url):
        # 读取目录里的文件
        files = os.listdir(_url)
        for f in files:
            if os.path.isfile(f'{_url}/{f}'):
                # 判断集数是否存在
                arr = f.split('.')
                if arr[0] == str(num):
                    return f'{name}/{f}'

########################################## 接口配置
class ApiConfig():

    def __init__(self, _dir):
        if os.path.exists(_dir) == False:           
            self.mkdir(_dir)
        self.dir = _dir

    def get_config(self):
        content = self.read('conversation.yaml')
        if content is None:
            content = {}
        return content

    def save_config(self, data):
        content = self.get_config()
        content.update(data)
        self.write('conversation.yaml', content)

    # 创建文件夹
    def mkdir(self, path):
        folders = []
        while not os.path.isdir(path):
            path, suffix = os.path.split(path)
            folders.append(suffix)
        for folder in folders[::-1]:
            path = os.path.join(path, folder)
            os.mkdir(path)

    # 获取路径
    def get_path(self, name):
        return self.dir + '/' + name

    # 读取文件内容
    def read(self, name):
        fn = self.get_path(name)
        if os.path.isfile(fn):
            with open(fn,'r', encoding='utf-8') as f:
                content = yaml.load(f, Loader=yaml.FullLoader)
                return content
        return None

    # 写入文件内容
    def write(self, name, obj):
        with open(self.get_path(name), 'w', encoding='utf-8') as f:
            yaml.dump(obj, f)
