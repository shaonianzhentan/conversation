import re

def trim_char(text):
    return text.strip(' 。，、＇：∶；?‘’“”〝〞ˆˇ﹕︰﹔﹖﹑·¨….¸;！´？！～—ˉ｜‖＂〃｀@﹫¡¿﹏﹋﹌︴々﹟#﹩$﹠&﹪%*﹡﹢﹦﹤‐￣¯―﹨ˆ˜﹍﹎+=<­­＿_-\ˇ~﹉﹊（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】︵︷︿︹︽_﹁﹃︻︶︸﹀︺︾ˉ﹂﹄︼')

def matcher_light_mode(text):
    matchObj = re.match(r'(.+)(调成|设为|设置为|调为)(.*)模式', text)
    if matchObj is not None:
        name = trim_char(matchObj.group(1)) 
        mode = matchObj.group(3)
        modeObj = {
            '随机': 'random',
            '橙': 'strobe',
            '闪光': 'flicker',
            '彩虹': 'addressable_rainbow',
            '颜色流动': 'addressable_color_wipe',
            '扫描': 'addressable_scan',
            '闪烁': 'addressable_twinkle',
            '随机闪烁': 'addressable_random_twinkle',
            '烟火': 'addressable_fireworks'
            # '闪光': 'addressable_flicker'
        }
        # 设备
        if name[0:1] == '把':
            name = name[1:]
        # 固定颜色
        if mode in modeObj:
            return (name, modeObj[mode], mode)

print(matcher_light_mode('把xx灯设为随机闪烁模式'))