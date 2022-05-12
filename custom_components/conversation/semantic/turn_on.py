import match
import ha

def parser(text):
    matchObj = match.parser_match(text, '打开|开启|启动|开一下|开下')
    if matchObj is not None:
        result = ha.find_area(matchObj[0])
        if result is None:
            result = ha.find_area(matchObj[2])

        if result is not None:
            return {
                'cmd': 'turn_on',
                **result
            }