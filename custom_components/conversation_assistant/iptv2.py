import os, aiohttp, time
from .langconv import Converter

def tradition2simple(line):
    # 将繁体转换成简体
    line = Converter('zh-hans').convert(line.encode().decode('utf-8'))
    return line

class track():
    def __init__(self, group, title, path):
        self.group = group
        self.title = title
        self.path = path

def parseM3U(infile):
    try:
        assert(type(infile) == '_io.TextIOWrapper')
    except AssertionError:
        infile = open(infile,'r')

    playlist=[]

    for line in infile:
        line=line.strip()
        if line != '' and '[geo-blocked]' not in line and '#' not in line and '.m3u8' in line:
            arr = line.split(',')
            title = tradition2simple(arr[0])
            url = arr[1]
            
            group = '默认列表'
            if 'CCTV' in title:
                group = 'CCTV'
            elif 'NewTV' in title:
                group = 'NewTV'
            elif 'SiTV' in title:
                group = 'SiTV'
            elif '电影' in title or '影视' in title or '视频' in title:
                group = '电影视频'
            elif '新闻' in title or '资讯' in title:
                group = '新闻资讯'
            elif '少儿' in title or '卡通' in title:
                group = '少儿卡通'
            elif '卫视' in title:
                group = '卫视'
            elif '上海' in title:
                group = '上海'
            elif '浙江' in title:
                group = '浙江'
            elif '江苏' in title:
                group = '江苏'
            elif '中国' in title or '中文' in title:
                group = '中文频道'
            song=track(group, title, url)
            playlist.append(song)

    infile.close()
    playlist.sort(key=lambda x: x.title)
    return playlist

class IPTV():

    def __init__(self) -> None:
        self.playlist = []
        self.groups = []

    async def get_list(self):
        m3ufile = 'iptv2.m3u'
        is_download = False
        if os.path.exists(m3ufile) == True:
            # 更新时间小于60分钟，播放列表不为空，则停止更新
            if time.time() < os.path.getmtime(m3ufile) + 60000 * 60:
                if len(self.playlist) > 0:
                    print('每隔60分钟更新一次')
                    return self.playlist
            else:
                is_download = True
        else:
            is_download = True

        if is_download:
            print('拉取最新资源')
            m3u_url = 'https://epg.pw/test_channels_china.txt'
            # 下载文件
            request_timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=request_timeout) as session:
                async with session.get(m3u_url) as response:
                    with open(m3ufile,"wb") as fs:
                        fs.write(await response.read())
        # 解析文件
        playlist = parseM3U(m3ufile)
        self.playlist = playlist
        # 分组
        self.groups = list(set(map(lambda x: x.group, playlist)))

        return self.playlist

    async def search_list(self, name):
        ''' 列表搜索 '''
        playlist = await self.get_list()
        return list(filter(lambda x: name.lower() in x.title.lower(), playlist))

    async def search_item(self, name):
        ''' 列表项搜索 '''
        playlist = await self.get_list()
        _list = list(filter(lambda x: name.lower() in x.title.lower(), playlist))
        if len(_list) > 0:
            return _list[0]

    async def search_url(self, name):
        ''' 播放URL搜索 '''
        item = await self.search_item(name)
        if item is not None:
            return item.path
