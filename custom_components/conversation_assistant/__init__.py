from __future__ import annotations

from functools import partial
import logging, datetime, re
from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, MATCH_ALL
from homeassistant.core import HomeAssistant, Context
from homeassistant.exceptions import ConfigEntryNotReady, TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid
from home_assistant_intents import get_domains_and_languages, get_intents

from .conversation_assistant import ConversationAssistant
DATA_VOICE = "conversation_voice"

_LOGGER = logging.getLogger(__name__)

# 文本识别库引入
try:
    import recognizers_suite as Recognizers
    from recognizers_suite import Culture, ModelResult
except Exception as ex:
    _LOGGER.warning(ex)
    print(ex)
    Recognizers = None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    assistant = ConversationAssistantAgent(hass, entry)
    conversation.async_set_agent(hass, entry, assistant)

    async def recognize(text, conversation_id=None):
        result = await assistant.async_process(
            conversation.ConversationInput(
                text=text,
                context=Context(),
                conversation_id=conversation_id,
            )
        )
        return result
    hass.data[DATA_VOICE] = ConversationAssistant(hass, recognize)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    conversation.async_unset_agent(hass, entry)
    return True


class ConversationAssistantAgent(conversation.AbstractConversationAgent):

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        # 预定义实体
        self.calendar_id = self.entry.options.get("calendar_id")
        self.music_id = self.entry.options.get("music_id")

    @property
    def attribution(self):
        """Return the attribution."""
        return {"name": "由 shaonianzhentan 提供技术支持", "url": "https://github.com/shaonianzhentan/conversation"}

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        return get_domains_and_languages()["homeassistant"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process a sentence."""
        conversation_id = user_input.conversation_id
        # 兼容中文语句
        language = user_input.language or self.hass.config.language
        country = self.hass.config.country
        if language == "zh-Hans":
            language = "zh-cn"
        elif language == "zh-Hant":
            if country == "HK":
                language = "zh-hk"
            elif country == "TW":
                language = "zh-tw"

        # 处理意图
        conversation_voice = self.hass.data[DATA_VOICE]
        text = conversation_voice.trim_char(user_input.text)
        conversation_voice.fire_text(text)

        # 调用内置服务
        conversation_result = await conversation.async_converse(
                hass=self.hass,
                text=text,
                conversation_id=conversation_id,
                context=user_input.context,
                language=language,
                agent_id='homeassistant'
            )
        intent_response = conversation_result.response
        if intent_response.error_code is not None:
            # 插件意图
            intent_response = await conversation_voice.async_process(text)

        speech = intent_response.speech.get('plain')
        if speech is not None:
            result = speech.get('speech')
            conversation_voice.update(text, result)

        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )
    
    async def async_music(self, text):
        if self.music_id is not None:
            service_name = None
            service_data = {
                'entity_id': self.music_id
            }
            if text == '播放':
                service_name= 'media_play'
            elif text == '暂停':
                service_name= 'media_pause'
            elif text == '上一曲':
                service_name= 'media_previous_track'
            elif text == '下一曲':
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

    async def async_calendar(self, text):
        if self.calendar_id is not None and '提醒我' in text and Recognizers is not None:
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