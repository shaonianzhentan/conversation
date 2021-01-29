
import re, requests, asyncio, aiohttp
from util import get_video_url

async def test():
    result = await get_video_url('无间道', -1)
    print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())