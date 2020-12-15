import re

def trim_char(text):
    return text.strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')

def matcher_on_off(text):
    matchObj = re.match(r'(打开|关闭)(.+)(打开|关闭)(.+)', text)
    if matchObj is not None:
        name1 = matchObj.group(2)
        name2 = matchObj.group(4)
        if name1 is not None and name2 is not None:
            type1 = matchObj.group(1) == '打开' and 'turn_on' or 'turn_off'
            type2 = matchObj.group(3) == '打开' and 'turn_on' or 'turn_off'
            _list1 = list(filter(lambda x: x != '', name1.split('和')))
            _list2 = list(filter(lambda x: x != '', name2.split('和')))
            return ((type1, _list1), (type2, _list2))

print(matcher_on_off('打开吸顶灯和墙壁灯关闭卫生间的灯'))
print(matcher_on_off('关闭xxx打开和xxx'))