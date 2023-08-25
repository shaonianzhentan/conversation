import aiohttp, asyncio


async def chat_robot(text):
  
  url = 'https://www.haigeek.com/skillcenter/skillPlate/skillTrial'
  headers = {
    'Content-Type': 'application/json'
  }
  body = {
    "userQuery": text,
    "userId": "d0c6a515-5221-42d3-977e-6d275cec2a70", 
    "deviceId": "2c995a8c-bf38-4788-8614-d40b47ba3b05"
  }
  async with aiohttp.ClientSession(headers=headers) as session:
    timeout = aiohttp.ClientTimeout(total=5)
    async with session.post(url=url, json=body, timeout=timeout) as res:
       result = await res.json(content_type=None)
       if result.get('retCode') == '00000':
        res_data = result['data']
        print(res_data)
        return res_data['response']


if __name__ == '__main__':
  event_loop = asyncio.get_event_loop()
  event_loop.run_until_complete(chat_robot('我想听相声'))