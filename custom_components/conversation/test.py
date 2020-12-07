import re

text = '请帮我打开彩灯跟吸顶灯和墙壁灯'
matchObj = re.match(r'.*((打开|开启|启动|关闭|关掉|关上|切换)(.+))', text)
if matchObj is not None:
    action = matchObj.group(2)
    name = matchObj.group(3) 
    print(action)
    print(name)
    if name.count('灯') > 1:
        matchObj = re.findall(r'((.*?)灯)', name)
        for item in matchObj:
            print(item[0].strip('和跟'))

print(text[-1])