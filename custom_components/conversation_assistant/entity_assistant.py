import logging, datetime, re
_LOGGER = logging.getLogger(__name__)

import recognizers_suite as Recognizers
from recognizers_suite import Culture, ModelResult
from radios import FilterBy, Order, RadioBrowser

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
        ''' 广播电台 '''
        if self.fm_id is not None and '广播' in text:
            # 搜索广播电台
            async with RadioBrowser(user_agent="MyAwesomeApp/1.0.0") as radios:
                # https://de1.api.radio-browser.info/json/stations/bylanguage/chinese?hidebroken=true&order=changetimestamp
                stations = await radios.stations(
                    filter_by=FilterBy.LANGUAGE,
                    filter_term='chinese',
                    hide_broken=True,
                    order=Order.CHANGE_TIMESTAMP,
                    reverse=False,
                )
                collect = filter(lambda x: x.name == text, stations)
                for item in collect:
                    print(item)
                    await self.hass.services.async_call('media_player', 'play_media', { 
                        'entity_id': self.fm_id,
                        'media_content_type': 'music',
                        'media_content_id': item.url
                    })
                    state = self.hass.states.get(self.fm_id)
                    friendly_name = state.attributes.get('friendly_name', '')
                    return f'正在{friendly_name}上播放{text}'

    async def async_music(self, text):
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
            elif ['声音小点', '小点声音', '小一点声音', '声音小一点'].count(text) == 1:
                service_name= 'volume_down'
            elif ['声音大点', '大点声音', '大一点声音', '声音大一点'].count(text) == 1:
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
                    friendly_name = state.attributes.get('friendly_name', '')
                    volume_level = state.attributes.get("volume_level", 0) * 100
                    return f'{friendly_name}的音量是{volume_level}%'

                return f'音乐{text}'

    async def async_tv(self, text):
        ''' 电视 '''
        if self.tv_id is not None:
            service_name = None
            service_data = {
                'entity_id': self.tv_id
            }
            if text.startswith('我想看'):
                pass
                '''
                service_name = 'play_media'
                service_data.update({
                    'media_content_type': 'video',
                    'media_content_id': ''
                })
                '''

            if service_name is not None:
                await self.hass.services.async_call('media_player', service_name, service_data)
                return text

    async def async_xiaoai(self, text):
        ''' 小爱音箱 '''
        if self.xiaoai_id is not None and (text.startswith('小爱') or text.startswith('小艾')):
            text = text[2:]
            if text == '':
                return None

            service_data = {
                'text': text,
                'entity_id': self.xiaoai_id,
                'execute': True,
                'silent': True,
                'throw': True
            }
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
            # 判断是否输入时间
            if time_text.count(':') == 1:
                time_text = time_text.replace(':', '点')
            description = arr[1]
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