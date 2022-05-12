import semantic

arr = [
    '关闭卫生间的吸顶灯',
    '打开彩灯',
    '打开电视',
    '空气净化器设为自动模式',
    '空调强劲模式',
    '现在几点了',
    '老婆到哪里了',
    '今天天气怎么样',
    '来点音乐',
    '播放周杰伦的稻香',
    '我想听林俊杰的歌',
    '播放',
    '暂停',
    '换一个',
    '无意义的兔子',
    '句子没有意义还有错别字',
    '关闭全部的设备',
    '关闭全部的灯',
    '关掉卧室全部的灯',
    '关掉卧室所有灯',
    '句子没有意义还有错别字',
    '全部的灯很重要',
    '哦，把全部的灯打开'
]

for text in arr:
    result = semantic.parser(text)
    slots = result['slots']
    if len(slots) > 0:
        print(text)
        for slot in slots:
            entity_id = slot.get('entity_id')
            if entity_id is None:
                for entity in result.get('entities'):
                    server_name = f'{entity["domain"]}.{slot["cmd"]}'
                    print(server_name, entity['entity_id'])
            else:
                server_name = f'{slot["domain"]}.{slot["cmd"]}'
                print(server_name, entity_id)