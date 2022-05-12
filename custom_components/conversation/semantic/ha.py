import match

areas = ['卫生间', '卧室', '阳台']
entitys = ['吸顶灯', '台灯', '彩灯']

# match entity name
def find_entity(text):
    for entity in entitys:
        if text.count(entity) > 0:
            return {
                'domain': 'fan',
                'entity_id': 'fan.cai_deng',
                'entity_name': entity
            }

def findAll_entity(area):
    arr = []
    if area is not None and areas.count(area.get('area_name')) > 0:
        for entity in entitys:
            arr.append({
                'domain': 'light',
                'entity_id': 'light.cai_deng',
                'entity_name': entity            
            })
    return arr

# match area
def find_area(text):
    area_str = '|'.join(areas)
    area = ''
    entity = None
    words = match.parser_match(text, area_str)
    if words is not None:
        area = words[1]
        entity = find_entity(words[2])
    else:
        entity = find_entity(text)
    
    if entity is not None:
        return {
            'area_id': '',
            'area_name': area,
            'area_words': words,
            **entity
        }

    if area != '':
        return {
            'area_id': '',
            'area_name': area,
            'area_words': words
        }