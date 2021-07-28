
import re, requests, asyncio
from util import matcher_switch

async def test():
    result = matcher_switch('麻烦把吸顶灯打开')
    print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())