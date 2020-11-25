import re

text = '请帮我打开彩灯'
matchObj = re.match(r'.*((打开|开启|启动|关闭|关掉|关上|切换)(.+))', text)
if matchObj is not None:
    action = matchObj.group(2)
    print(matchObj.group(2))
    print(matchObj.group(3))