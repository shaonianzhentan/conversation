
import re, asyncio

def matcher_media_player(text):
    matchObj = re.match(r'(上|下|前|后|左|右)1(曲|首|个|页|条|段)', text)
    if matchObj is not None:
        print(text.replace('1', '一'))

async def test():
    result = matcher_media_player('上1曲')

loop = asyncio.get_event_loop()
loop.run_until_complete(test())