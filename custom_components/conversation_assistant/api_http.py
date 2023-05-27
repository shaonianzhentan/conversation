import aiohttp

async def http_get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()