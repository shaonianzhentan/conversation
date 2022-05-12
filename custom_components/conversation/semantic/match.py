import re

def parser_match(text, find):
    matchObj = re.match(rf'(.*)({find})(.*)', text)
    if matchObj is not None:
        return (matchObj.group(1), matchObj.group(2), matchObj.group(3))