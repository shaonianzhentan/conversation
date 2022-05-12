import match
import ha

def parser(text):
    matchObj = match.parser_match(text, '关闭|关掉|关上|关一下|关下')
    if matchObj is not None:
        result = ha.find_area(matchObj[0])
        if result is None:
            result = ha.find_area(matchObj[2])

        if result is not None:
            return {
                'cmd': 'turn_off',
                **result
            }