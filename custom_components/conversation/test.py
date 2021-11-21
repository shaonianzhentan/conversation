
import re, asyncio

def matcher_media_player(text):
    matchObj = re.match(r'(.*)(播放|暂停|下一曲|上一曲)$', text)
    if matchObj is not None:
        return (matchObj.group(1),)

async def test():
    result = matcher_media_player('云音乐暂停')
    print(result[0])

loop = asyncio.get_event_loop()
loop.run_until_complete(test())