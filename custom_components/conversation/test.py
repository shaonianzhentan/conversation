import re

text = '公交到站时间的状态'
matchObj = re.match(r'(查看|查询)(.*)', text)
if matchObj is not None:
    print(matchObj.group(2))
else:    
    matchObj = re.match(r'(.*)的状态', text)
    if matchObj is not None:
        print(matchObj.group(1))