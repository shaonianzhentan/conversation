
import re, requests, asyncio, aiohttp
from util import matcher_query_state

async def test():
    result = matcher_query_state('查看卧室的温度')
    print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())