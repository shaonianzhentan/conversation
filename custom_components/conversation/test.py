
import re, requests

from util import matcher_search_video

print(matcher_search_video('打开电视大秦赋第一集'))


'''

def search_video(name):
    res = requests.get(f'https://api.okzy.tv/api.php/provide/vod/at/json/?ac=detail&wd={name}')
    data = res.json()
    if data['total'] > 0:
        obj = data['list'][0]
        text = obj['vod_play_url']
        matchObj = re.findall(r'第(\d+)集\$(.*?)m3u8', text.split('$$$')[1])
        _obj = {}
        for item in matchObj:
            _obj[int(item[0])] = f'{item[1]}m3u8'
        print(_obj)

search_video('大秦赋')

'''
