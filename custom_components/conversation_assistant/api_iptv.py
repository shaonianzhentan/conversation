import os, aiohttp, time

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

    """
        All M3U files start with #EXTM3U.
        If the first line doesn't start with this, we're either
        not working with an M3U or the file we got is corrupted.
    """

    line = infile.readline()
    if not line.startswith('#EXTM3U'):
       return

    # initialize playlist variables before reading file
    playlist=[]
    song=track(None,None,None)

    for line in infile:
        line=line.strip()
        if line.startswith('#EXTINF:'):
            # pull length and title from #EXTINF line
            info,title=line.split('#EXTINF:')[1].split(',',1)
            #print(info, title)

            # 过滤失效
            if '[Timeout]' in title or '[Geo-blocked]' in title:
            #matchObj = re.match(r'(.*)status="online"', info)
            #if matchObj is None:
                continue

            group = '默认列表'
            if 'CCTV' in title:
                group = 'CCTV'
            elif 'NewTV' in title:
                group = 'NewTV'
            elif 'SiTV' in title:
                group = 'SiTV'
            elif '电影' in title or '影视' in title or '影視' in title or '视频' in title:
                group = '电影视频'
            elif '新闻' in title or '新聞' in title or '资讯' in title:
                group = '新闻资讯'
            elif '少儿' in title or '卡通' in title:
                group = '少儿卡通'
            elif '卫视' in title or '衛視' in title:
                group = '卫视'
            elif '上海' in title:
                group = '上海'
            elif '浙江' in title:
                group = '浙江'
            elif '江苏' in title:
                group = '江苏'
            elif '中国' in title or '中文' in title:
                group = '中文频道'
            song=track(group,title,None)
        elif (len(line) != 0):
            # pull song path from all other, non-blank lines
            song.path=line
            if song.group is not None:
                playlist.append(song)
            # reset the song variable so it doesn't use the same EXTINF more than once
            song=track(None,None,None)

    infile.close()

    return playlist

class IPTV():

    def __init__(self) -> None:
        self.playlist = []
        self.groups = []

    async def get_list(self):
        m3ufile = 'iptv.m3u'
        is_download = False
        if os.path.exists(m3ufile) == True:
            # 更新时间小于30分钟，播放列表不为空，则停止更新
            if time.time() < os.path.getmtime(m3ufile) + 60000 * 30:
                if len(self.playlist) > 0:
                    print('每隔30分钟更新一次')
                    return self.playlist
            else:
                is_download = True
        else:
            is_download = True

        if is_download:
            print('拉取最新资源')
            #m3u_url = 'https://ghproxy.com/https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u'
            #m3u_url = 'https://epg.pw/test_channels_china.m3u'
            m3u_url = 'https://ghproxy.com/https://raw.githubusercontent.com/BurningC4/Chinese-IPTV/master/TV-IPV4.m3u'
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

    async def async_search_play(self, name):
        ''' 搜索可播放项 '''
        items = await self.search_list(name)
        if items is not None:
            request_timeout = aiohttp.ClientTimeout(total=2)
            for item in items:
                print(item.title, item.path)
                try:
                    async with aiohttp.ClientSession(timeout=request_timeout) as session:
                        async with session.get(item.path) as response:
                            print(response.status)
                            return item.path
                except Exception as ex:
                    pass