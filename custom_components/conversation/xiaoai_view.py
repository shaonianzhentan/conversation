import json
from homeassistant.components.http import HomeAssistantView
from .const import DOMAIN

from .xiaoai import (XiaoAIAudioItem, XiaoAIDirective, XiaoAIOpenResponse,
                    XiaoAIResponse, XiaoAIStream, XiaoAIToSpeak, XiaoAITTSItem,
                    xiaoai_request, xiaoai_response)

# 文本回复
def build_text_message(to_speak, is_session_end, open_mic):
    xiao_ai_response = XiaoAIResponse(
        to_speak=XiaoAIToSpeak(type_=0, text=to_speak),
        open_mic=open_mic)
    response = xiaoai_response(XiaoAIOpenResponse(version='1.0',
                                                  is_session_end=is_session_end,
                                                  response=xiao_ai_response))
    return response

# 音乐回复
def build_music_message(to_speak, mp3_urls):
    all_list = []
    if to_speak is not None:
        info_tts = XiaoAIDirective(
            type_='tts',
            tts_item=XiaoAITTSItem(
                type_='0', text=to_speak
            ))

        all_list.append(info_tts)
    for url in mp3_urls:
        info_audio = XiaoAIDirective(
            type_='audio',
            audio_item=XiaoAIAudioItem(stream=XiaoAIStream(url=url))
        )
        all_list.append(info_audio)
    xiao_ai_response = XiaoAIResponse(directives=all_list, open_mic=False)
    response = xiaoai_response(XiaoAIOpenResponse(
        version='1.0', is_session_end=True, response=xiao_ai_response))
    return response

# 格式转换
def parse_input(event, hass):
    req = xiaoai_request(event)
    # 插槽：req.request.slot_info.intent_name
    intent_name = ''
    if hasattr(req.request.slot_info, 'intent_name'):
        intent_name = req.request.slot_info.intent_name
    # 消息内容：req.query
    print(req.query)
    if req.request.type == 0:
        # 技能进入请求
        return build_text_message('欢迎使用你的家庭助理', is_session_end=False, open_mic=True)
    elif req.request.type == 1:        
        # 退出意图
        if intent_name == 'Mi_Exit':
            return build_text_message('再见了您！', is_session_end=True, open_mic=False)
        else:
            hass.async_create_task(hass.services.async_call('conversation', 'process', {'text': req.query}))
            return build_text_message('收到，还有什么事吗？', is_session_end=False, open_mic=True)
    elif req.request.type == 2:
        return build_text_message('再见了您！', is_session_end=True, open_mic=False)

    return build_text_message('我没听懂欸', is_session_end=True, open_mic=False)

# 网关视图
class XiaoaiGateView(HomeAssistantView):

    url = f"/{DOMAIN}-xiaoai"
    name = DOMAIN
    requires_auth = False

    async def post(self, request):
        data = await request.json()
        # print(data)
        hass = request.app["hass"]        
        response = parse_input(data, hass)
        return self.json(json.loads(response))

