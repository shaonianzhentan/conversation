import re
text = "xxx调成红色"

matchObj = re.match(r'(.+)(调成|设为|调为)(.*)色', text)
if matchObj is not None:
    name = matchObj.group(1) 
    color = matchObj.group(3)
    colorObj = {
        '红': 'red',
        '橙': 'orange',
        '黄': 'yellow',
        '绿': 'green',
        '青': 'red',
        '蓝': 'blue',
        '紫': 'red',
        '粉': 'pink',
        '白': 'white'
    }
    # 设备
    if name[0:1] == '把':
        name = name[1:]
    print(name)
    # 颜色
    if color in colorObj:
        print(colorObj[color])