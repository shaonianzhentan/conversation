
import re, requests, asyncio, aiohttp
from util import get_video_url

async def test():
    video_url = await get_video_url('半泽直树', 2)
    print(video_url)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())