"""海尔机器人语音服务"""
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)

HAIER_URL = 'https://www.haigeek.com/skillcenter/skillPlate/skillTrial'
HAIER_USER_ID = 'd0c6a515-5221-42d3-977e-6d275cec2a70'
HAIER_DEVICE_ID = '2c995a8c-bf38-4788-8614-d40b47ba3b05'


async def async_haier_robot(text: str) -> dict | None:
    """调用海尔机器人，返回 data 字段。"""
    timeout = aiohttp.ClientTimeout(total=5)
    headers = {'Content-Type': 'application/json'}
    body = {
        'userQuery': text,
        'userId': HAIER_USER_ID,
        'deviceId': HAIER_DEVICE_ID,
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url=HAIER_URL, json=body, timeout=timeout) as res:
            result = await res.json(content_type=None)
            _LOGGER.debug(result)
            if result.get('retCode') == '00000':
                return result['data']
    return None
