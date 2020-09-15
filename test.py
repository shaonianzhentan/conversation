import re
text = "把音量调到10"

matchObj = re.match(r'.*(音量调到|音量设置|设置音量)(.*)', text)
if matchObj is not None:
    print(matchObj.group(2))