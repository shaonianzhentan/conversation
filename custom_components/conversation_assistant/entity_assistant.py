import logging, datetime, re, random
_LOGGER = logging.getLogger(__name__)

import recognizers_suite as Recognizers
from recognizers_suite import Culture, ModelResult
from urllib.parse import urlparse, parse_qs, parse_qsl, quote
from .api_iptv import IPTV
from .api_http import http_get
from aiodns import DNSResolver

class EntityAssistant:

    def __init__(self, hass, config) -> None:
        self.hass = hass
        self.calendar_id = config.get('calendar_id')
        self.music_id = config.get('music_id')
        self.tv_id = config.get('tv_id')
        self.fm_id = config.get('fm_id')
        self.xiaoai_id = config.get('xiaoai_id')
        self.xiaodu_id = config.get('xiaodu_id')

        self.iptv = IPTV()
        hass.data.setdefault('conversation_iptv', self.iptv)

    async def async_process(self, text):
        result = await self.async_calendar(text)
        if result is not None:
            return result

        result = await self.async_fm(text)
        if result is not None:
            return result

        result = await self.async_music(text)
        if result is not None:
            return result

        result = await self.async_tv(text)
        if result is not None:
            return result

        result = await self.async_xiaoai(text)
        if result is not None:
            return result

        result = await self.async_xiaodu(text)
        if result is not None:
            return result

    async def async_fm(self, text):
        ''' 广播 '''
        entity_id = self.fm_id or self.music_id
        if text.startswith('播放广播') and entity_id:
            text = text[4:]
            resolver = DNSResolver()
            result = await resolver.query("_api._tcp.radio-browser.info", "SRV")
            random.shuffle(result)
            radio_api = f'https://{result[0].host}/json/'

            if text == '':
                url = f'{radio_api}stations/search?limit=30&countrycode=CN&hidebroken=true&order=clickcount&reverse=true'
                index = random.randint(0,29)
            else:
                url = f'{radio_api}stations/search?limit=2&name={quote(text)}&hidebroken=true&order=clickcount&reverse=true'
                index = 0

            result = await http_get(url)
            if result is not None and len(result) > 0:
                item = result[index]
                print(item)
                play_name = item['name']
                play_url = item['url']
                await self.hass.services.async_call('media_player', 'play_media', {
                    'entity_id': entity_id,
                    'media_content_type': 'music',
                    'media_content_id': play_url
                })
                state = self.hass.states.get(entity_id)
                friendly_name = state.attributes.get('friendly_name', '')
                return f'正在{friendly_name}上播放{play_name}'

    async def async_music(self, text):
        ''' 音乐 '''
        if self.music_id is not None:
            service_name = None
            service_data = {
                'entity_id': self.music_id
            }
            if ['播放', '继续播放', '播放音乐'].count(text) == 1:
                service_name= 'media_play'
            elif ['暂停', '暂停音乐'].count(text) == 1:
                service_name= 'media_pause'
            elif ['上一曲', '上一首', '上一个'].count(text) == 1:
                service_name= 'media_previous_track'
            elif ['下一曲', '下一首', '下一个'].count(text) == 1:
                service_name= 'media_next_track'
            elif ['声音小点', '小点声音', '小点声', '小一点声音', '声音小一点'].count(text) == 1:
                service_name= 'volume_down'
            elif ['声音大点', '大点声音', '大点声', '大一点声音', '声音大一点'].count(text) == 1:
                service_name= 'volume_up'
            elif text.startswith('播放每日推荐'):
                service_name = 'play_media'
                service_data.update({
                    'media_content_type': 'music',
                    'media_content_id': 'cloudmusic://163/my/daily'
                })
                text = f'正在播放每日推荐音乐'
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
                pass


            if service_name is not None:
                await self.hass.services.async_call('media_player', service_name, service_data)

                # 返回音量信息
                if ['volume_up', 'volume_down'].count(service_name) == 1:
                    state = self.hass.states.get(self.music_id)
                    friendly_name = state.attributes.get('friendly_name')
                    volume_level = state.attributes.get("volume_level", 0) * 100
                    return f'{friendly_name}的音量是{volume_level}%'

                return f'音乐{text}'

    async def async_tv(self, text):
        ''' 电视 '''
        if self.tv_id is not None and text.startswith('我想看'):
                text = text[3:]
                if text == '':
                    return None

                item = await self.iptv.async_search_play(text)
                if item is not None:
                    await self.hass.services.async_call('media_player', 'play_media', {
                        'media_content_type': 'video',
                        'media_content_id': item.path,
                        'entity_id': self.tv_id
                    })
                    state = self.hass.states.get(self.tv_id)
                    friendly_name = state.attributes.get('friendly_name')
                    return f'正在{friendly_name}上播放{item.title}'
                else:
                    return f'没有找到{text}'

    async def async_xiaoai(self, text):
        ''' 小爱音箱 '''
        if self.xiaoai_id is not None and (text.startswith('小爱') or text.startswith('小艾')):
            text = text[2:]

            service_data = {
                'entity_id': self.xiaoai_id,
                'throw': True
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
                'text': text,
                'entity_id': self.xiaodu_id
            }
            await self.hass.services.async_call('baidu', 'command', service_data)
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
            results = Recognizers.recognize_datetime(time_text, Culture.Chinese)
            length = len(results)
            if length > 0:
                result = results[length - 1]
                values = list(result.resolution.values())[0]
                print(values)
                value = values[0]
                t = value['type']
                v = value['value']

                now = datetime.datetime.now()
                start_date_time = None

                # 早晚
                if len(values) == 2:
                    # 和当前时间比较
                    if t == 'time':
                        if now.strftime('%H:%M:%S') > v:
                            value = values[1]
                            t = value['type']
                            v = value['value']

                if t == 'datetime':
                    start_date_time = v
                elif t == 'time':
                    localtime = now.strftime('%Y-%m-%d %H:%M:%S')
                    if v < localtime[11:]:
                        return '时间已经过去了，没有提醒的必要啦'
                    start_date_time = localtime[:11] + v
                elif t == 'duration':
                    now = now + datetime.timedelta(seconds=+int(v))
                    start_date_time = now.strftime('%Y-%m-%d %H:%M:%S')

                if start_date_time is not None:
                    # 结束时间
                    end_date_time = datetime.datetime.strptime(start_date_time, '%Y-%m-%d %H:%M:%S')
                    end_date_time = end_date_time + datetime.timedelta(seconds=+60)

                    await self.hass.services.async_call('calendar', 'create_event', {
                        'entity_id': self.calendar_id,
                        'start_date_time': start_date_time,
                        'end_date_time': end_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'summary': description,
                        'description': text
                    })
                    return f'【{start_date_time}】{description}'