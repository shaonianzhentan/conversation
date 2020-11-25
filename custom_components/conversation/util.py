"""Util for Conversation."""
import re
import string
import random

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

########################################## 常量
VERSION = '1.6'
DOMAIN = "conversation"
DATA_AGENT = "conversation_agent"
DATA_CONFIG = "conversation_config"
XIAOAI_API = "/conversation-xiaoai"
########################################## 查询实体
def find_entity(hass, name, type = ''):
    # 遍历所有实体
    states = hass.states.async_all()
    for state in states:
        entity_id = state.entity_id
        attributes = state.attributes
        friendly_name = attributes.get('friendly_name')
        # 查询对应的设备名称
        if friendly_name is not None and friendly_name.lower() == name.lower():
            # 指定类型
            if type == '' or entity_id.find(f'{type}.') == 0:
                return state

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

########################################## 颜色调整
def matcher_color(text):
    matchObj = re.match(r'(.+)(调成|设为|设置为|调为)(.*)色', text)
    if matchObj is not None:
        name = matchObj.group(1) 
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

########################################## 亮度调整
def matcher_brightness(text):
    matchObj = re.match(r'(.+)亮度(调成|调到|调为|设为)(.*)', text)
    if matchObj is not None:
        name = matchObj.group(1) 
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

########################################## (执行|触发|打开|关闭)自动化
def matcher_automation(text):
    matchObj = re.match(r'(执行|触发|打开|关闭)自动化(.*)', text)
    if matchObj is not None:
        return (matchObj.group(1), matchObj.group(2))

########################################## 查看设备状态
def matcher_query_state(text):
    matchObj = re.match(r'(查看|查询)(.*)的状态', text)
    if matchObj is not None:
        return matchObj.group(2)

    matchObj = re.match(r'(查看|查询)(.*)', text)
    if matchObj is not None:
        return matchObj.group(2)
    
    matchObj = re.match(r'(.*)的状态', text)
    if matchObj is not None:
        return matchObj.group(1)