
import re, requests, asyncio, aiohttp
from util import http_get

async def get_video_url(name, num):
    print(f'{name} - {num}')
    # b搜索
    _url = f'https://api.bilibili.com/x/web-interface/search/type?context=&search_type=media_ft&order=&keyword={name}'
    print(_url)
    data = await http_get(_url)
    # print(data)
    result = data['data'].get('result', [])
    if len(result) > 0:
        # 这里可以过滤电视剧。。。懒得搞了，先就这样
        eps = result[0]['eps']
        for item in eps:
            # 过滤会员，查找集数
            if len(item.get('badges', [])) == 0 and int(item['index_title']) == num:
                # 查询视频链接
                res = await http_get(f"https://api.bilibili.com/pgc/player/web/playurl/html5?ep_id={item['id']}")
                # print(res)
                return res['result']['durl'][0]['url']

    # 辣鸡视频
    _url = f'https://api.okzy.tv/api.php/provide/vod/at/json/?ac=detail&wd={name}'
    print(_url)
    data = await http_get(_url)
    # print(data)
    if data['total'] > 0:
        for obj in data['list']:
            # 如果没有播放地址，则去找下一个
            vod_play_url = obj.get('vod_play_url', '')
            if vod_play_url == '':
                continue
            # 获取m3u8列表
            vod_play_url_list = vod_play_url.split('$$$')
            url_list = vod_play_url_list[1]
            # 判断后缀格式
            if url_list[-5:] != '.m3u8':
                url_list = vod_play_url_list[0]
            # 匹配集数
            matchObj = re.findall(r'第(\d+)集\$(.*?)m3u8', url_list)
            # 如果集数，大于当前列表，则去找下一个
            if num > len(matchObj):
                continue
            # 遍历当前视频集合
            for item in matchObj:
                print(item)
                if int(item[0]) == num:
                    return f'{item[1]}m3u8'

async def test():
    video_url = await get_video_url('名侦探柯南', 8)
    print(video_url)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())