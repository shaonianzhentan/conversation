from .manifest import manifest
from .util_recognizer import get_calendar_datetime, get_number_value
from .api_http import http_get
from urllib.parse import urlparse, parse_qs, parse_qsl, quote
import logging
import datetime
import re
import random
_LOGGER = logging.getLogger(__name__)

class EntityAssistant:

    def __init__(self, hass, config) -> None:
        self.hass = hass
        self.calendar_id = config.get('calendar_id')
        self.music_id = config.get('music_id')
        self.tv_id = config.get('tv_id')
        self.fm_id = config.get('fm_id')
        self.xiaoai_id = config.get('xiaoai_id')
        self.xiaodu_id = config.get('xiaodu_id')

    async def async_process(self, text):
        result = await self.async_calendar(text)
        if result is not None:
            return result, self.calendar_id

        result = await self.async_fm(text)
        if result is not None:
            return result, self.fm_id

        result = await self.async_music(text)
        if result is not None:
            return result, self.music_id

        result = await self.async_tv(text)
        if result is not None:
            return result, self.tv_id

        result = await self.async_xiaoai(text)
        if result is not None:
            return result, self.xiaoai_id

        result = await self.async_xiaodu(text)
        if result is not None:
            return result, self.xiaodu_id

    async def async_fm(self, text):
        ''' 广播 '''
        entity_id = self.fm_id or self.music_id
        if '播放' in text and '广播' in text and entity_id:
            assistant = self.hass.data[manifest.domain]
            result = await assistant.haier_robot(text)
            if result is not None:
                if result.get('respType') == 'media':
                    await self.hass.services.async_call('media_player', 'play_media', {
                        'entity_id': entity_id,
                        'media_content_type': 'music',
                        'media_content_id': result.get('resourceUrl')
                    })
                    return result['response']

    async def async_music(self, text):
        ''' 音乐 '''
        if self.music_id is not None:
            service_name = None
            service_data = {
                'entity_id': self.music_id
            }
            if ['播放', '继续播放', '播放音乐', '音乐播放'].count(text) == 1:
                service_name = 'media_play'
            elif ['暂停', '暂停音乐', '音乐暂停'].count(text) == 1:
                service_name = 'media_pause'
            elif ['上一曲', '上一首', '上一个'].count(text) == 1:
                service_name = 'media_previous_track'
            elif ['下一曲', '下一首', '下一个'].count(text) == 1:
                service_name = 'media_next_track'
            elif ['声音小点', '小点声音', '小点声', '小一点声音', '声音小一点'].count(text) == 1:
                service_name = 'volume_down'
            elif ['声音大点', '大点声音', '大点声', '大一点声音', '声音大一点'].count(text) == 1:
                service_name = 'volume_up'
            elif text == '随机播放':
                service_name = 'shuffle_set'
                service_data.update({
                    'shuffle': True
                })
            elif text == '单曲循环':
                service_name = 'repeat_set'
                service_data.update({
                    'repeat': 'one'
                })
            elif text == '列表播放':
                await self.hass.services.async_call('media_player', 'shuffle_set', {
                    'shuffle': False,
                    **service_data
                })
                service_name = 'repeat_set'
                service_data.update({
                    'repeat': 'all'
                })
            elif text.startswith('播放每日推荐'):
                service_name = 'play_media'
                service_data.update({
                    'media_content_type': 'music',
                    'media_content_id': 'cloudmusic://163/my/daily'
                })
                text = f'正在播放每日推荐音乐'
            elif text.startswith('播放我喜欢的音乐'):
                service_name = 'play_media'
                service_data.update({
                    'media_content_type': 'music',
                    'media_content_id': 'cloudmusic://163/my/ilike'
                })
                text = f'正在播放我喜欢的音乐'
            elif text.startswith('我想听') and text.endswith('的歌'):
                matchObj = re.match(r'我想听(.+)的歌', text)
                if matchObj is not None:
                    singer = matchObj.group(1)
                    service_name = 'play_media'
                    service_data.update({
                        'media_content_type': 'music',
                        'media_content_id': 'cloudmusic://play/singer?kv=' + singer
                    })
                    text = f'正在播放{singer}的歌'

            elif text.startswith('我想听'):
                arr = text.split('我想听')
                if len(arr) == 2 and arr[1] != '':
                    kv = arr[1]
                    media_id = f'cloudmusic://play/song?kv={kv}'

                    if kv.endswith('歌单'):
                        media_id = f'cloudmusic://play/list?kv={kv}'

                    text = f'正在搜索播放{kv}'

                    service_name = 'play_media'
                    service_data.update({
                        'media_content_type': 'music',
                        'media_content_id': media_id
                    })

            elif text.startswith('播放电台'):
                arr = text.split('播放电台')
                if len(arr) == 2 and arr[1] != '':
                    kv = arr[1]
                    service_name = 'play_media'
                    service_data.update({
                        'media_content_type': 'music',
                        'media_content_id': f'cloudmusic://play/radio?kv={kv}'
                    })
                    text = f'正在播放电台{kv}'

            elif text.startswith('播放歌单'):
                arr = text.split('播放歌单')
                if len(arr) == 2 and arr[1] != '':
                    kv = arr[1]
                    service_name = 'play_media'
                    service_data.update({
                        'media_content_type': 'music',
                        'media_content_id': f'cloudmusic://play/list?kv={kv}'
                    })
                    text = f'正在播放歌单{kv}'

            elif text.startswith('播放专辑'):
                arr = text.split('播放专辑')
                if len(arr) == 2 and arr[1] != '':
                    kv = arr[1]
                    service_name = 'play_media'
                    service_data.update({
                        'media_content_type': 'music',
                        'media_content_id': f'cloudmusic://play/xmly?kv={kv}'
                    })
                    text = f'正在播放喜马拉雅专辑{kv}'

            if service_name is not None:
                await self.hass.services.async_call('media_player', service_name, service_data)

                # 返回音量信息
                if ['volume_up', 'volume_down'].count(service_name) == 1:
                    state = self.hass.states.get(self.music_id)
                    friendly_name = state.attributes.get('friendly_name')
                    volume_level = state.attributes.get(
                        "volume_level", 0) * 100
                    return f'{friendly_name}的音量是{volume_level}%'

                return f'音乐{text}'

    async def async_tv(self, text):
        ''' 电视 '''
        if self.tv_id is not None and text.startswith('我想看'):
            text = text[3:].lower()
            if text == '':
                return None

            media_id = None
            matchObj = re.match(r'中央(.+)台', text)
            if matchObj is not None:
                num = get_number_value(text)
                if num is not None:
                    if num == '1':
                        media_id = 'https://tv.cctv.com/live/cctv1/'
                    elif num == '2':
                        media_id = 'https://tv.cctv.com/live/cctv2/'
                    elif num == '3':
                        media_id = 'https://tv.cctv.com/live/cctv3/'
                    elif num == '4':
                        media_id = 'https://tv.cctv.com/live/cctv4/'
                    elif num == '5':
                        media_id = 'https://tv.cctv.com/live/cctv5/'
                    elif num == '6':
                        media_id = 'https://tv.cctv.com/live/cctv6/'
                    elif num == '7':
                        media_id = 'https://tv.cctv.com/live/cctv7/'
                    elif num == '8':
                        media_id = 'https://tv.cctv.com/live/cctv8/'
                    elif num == '9':
                        media_id = 'https://tv.cctv.com/live/cctvjilu/'
                    elif num == '10':
                        media_id = 'https://tv.cctv.com/live/cctv10/'
                    elif num == '11':
                        media_id = 'https://tv.cctv.com/live/cctv11/'
                    elif num == '12':
                        media_id = 'https://tv.cctv.com/live/cctv12/'
                    elif num == '13':
                        media_id = 'https://tv.cctv.com/live/cctv13/'
                    elif num == '14':
                        media_id = 'https://tv.cctv.com/live/cctvchild/'
                    elif num == '15':
                        media_id = 'https://tv.cctv.com/live/cctv15/'
                    elif num == '16':
                        media_id = 'https://tv.cctv.com/live/cctv16/'
                    elif num == '17':
                        media_id = 'https://tv.cctv.com/live/cctv17/'

            if media_id is not None:
                await self.hass.services.async_call('media_player', 'play_media', {
                    'media_content_type': 'web',
                    'media_content_id': media_id,
                    'entity_id': self.tv_id
                })
                state = self.hass.states.get(self.tv_id)
                friendly_name = state.attributes.get('friendly_name')
                return f'正在{friendly_name}上播放{text}'
            else:
                return f'没有找到{text}'

    async def async_xiaoai(self, text):
        ''' 小爱音箱 '''
        if self.xiaoai_id is not None and (text.startswith('小爱') or text.startswith('小艾')):
            text = text[2:]

            service_data = {
                'entity_id': self.xiaoai_id,
                'throw': False
            }
            if text == '':
                # 唤醒音乐
                await self.hass.services.async_call('xiaomi_miot', 'xiaoai_wakeup', service_data)
                return '小爱音箱正在聆听中...'

            # 执行命令
            service_data.update({
                'text': text,
                'execute': True,
                'silent': True
            })
            await self.hass.services.async_call('xiaomi_miot', 'intelligent_speaker', service_data)
            return text

    async def async_xiaodu(self, text):
        ''' 小度音箱 '''
        if self.xiaodu_id is not None and (text.startswith('小度') or text.startswith('小杜')):
            text = text[2:]
            if text == '':
                return None

            service_data = {
                'media_content_type': 'txt',
                'media_content_id': text,
                'entity_id': self.xiaodu_id
            }
            await self.hass.services.async_call('media_player', 'play_media', service_data)
            return text

    async def async_calendar(self, text):
        if self.calendar_id is not None and '提醒我' in text:
            arr = text.split('提醒我')
            time_text = arr[0]
            description = arr[1]
            if time_text == '' or description == '':
                return None
            # 判断是否输入时间
            if time_text.count(':') == 1:
                time_text = time_text.replace(':', '点')

            result = get_calendar_datetime(time_text)
            if result is not None:
                start_date_time, end_date_time = result
                if start_date_time is None:
                    return '时间已经过去了，没有提醒的必要啦'

                await self.hass.services.async_call('calendar', 'create_event', {
                    'entity_id': self.calendar_id,
                    'start_date_time': start_date_time,
                    'end_date_time': end_date_time,
                    'summary': description,
                    'description': text
                })
                return f'【{start_date_time}】{description}'
