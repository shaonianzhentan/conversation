import re
from homeassistant.helpers import template, entity_registry, area_registry
from .util import create_matcher

class Semantic():
    
    def __init__(self, hass):
        self.hass = hass

    # cache data
    async def update(self, text):
        entities = []
        self.areas = []
        # all state
        states = self.hass.states.async_all()
        arr = []
        for state in states:
            arr.append(state)
            friendly_name = state.attributes.get('friendly_name', '')
            if friendly_name != '' and friendly_name in text:
                entities.append({
                    'domain': state.entity_id.split('.')[0],
                    'entity_id': state.entity_id,
                    'entity_name': friendly_name,
                    'state': state.state
                })
        arr.sort(reverse=True, key=lambda x:x.last_changed)
        self.states = arr
        # all area
        area = await area_registry.async_get_registry(self.hass)
        self.area_list = area.async_list_areas()
        for item in self.area_list:
            if item.name in text:
                self.areas.append(item.name)
        # sort words
        entities.sort(reverse=True, key=lambda x:len(x['entity_name']))
        tmp_text = text
        for index, entity in enumerate(entities):
            entity_name = entity['entity_name']
            if entity_name in tmp_text:
                tmp_text = tmp_text.replace(entity_name, '')
            else:
                entities[index] = None
        self.entities = list(filter(lambda x:x is not None, entities))

    # match entity name
    async def find_entity(self, text):
        states = self.states
        for state in states:
            entity_id = state.entity_id
            domain = entity_id.split('.')[0]
            attributes = state.attributes
            friendly_name = attributes.get('friendly_name', '')
            if friendly_name != '' and friendly_name in text:
                return {
                    'domain': domain,
                    'entity_id': entity_id,
                    'entity_name': friendly_name,
                    'state': state.state
                }
    
    # match entity name
    async def find_entity_multiple(self, text):
        arr = []
        for state in self.states:
            friendly_name = state.attributes.get('friendly_name', '')
            if friendly_name != '' and friendly_name in text:
                arr.append({
                    'domain': state.entity_id.split('.')[0],
                    'entity_id': state.entity_id,
                    'entity_name': friendly_name,
                    'state': state.state
                })
        arr.sort(reverse=True, key=lambda x:len(x['entity_name']))
        tmp_text = text
        for index, entity in enumerate(arr):
            entity_name = entity['entity_name']
            if entity_name in tmp_text:
                tmp_text = tmp_text.replace(entity_name, '')
            else:
                arr[index] = None
        return list(filter(lambda x:x is not None, arr))

    # match entity name
    async def find_entity_name(self, name):
        arr = []
        states = self.states
        for state in states:
            entity_id = state.entity_id
            domain = entity_id.split('.')[0]
            attributes = state.attributes
            friendly_name = attributes.get('friendly_name', '')
            if friendly_name == '':
                continue
            # 执行自定义脚本
            if domain == 'script':
                # 判断是否自定义匹配命令
                intents = attributes.get('intents', [])
                if len(intents) > 0:
                    for intent in intents:
                        match = create_matcher(intent).match(name)
                        if match is not None:
                            return {
                                'domain': domain,
                                'entity_id': entity_id,
                                'entity_name': friendly_name,
                                'reply': attributes.get('reply'),
                                'slots': {key: value for key, value in match.groupdict().items()}
                            }

                cmd = friendly_name.split('=')
                if cmd.count(name) > 0:
                    return {
                        'domain': domain,
                        'entity_id': entity_id,
                        'entity_name': friendly_name,
                        'reply': attributes.get('reply')
                    }
            if friendly_name == name:
                arr.append({
                    'domain': domain,
                    'entity_id': entity_id,
                    'entity_name': friendly_name,
                    'state': state.state
                })
        if len(arr) > 0:
            return arr

    # match entity name
    async def find_entity_like(self, key):
        states = self.states
        for state in states:
            entity_id = state.entity_id
            domain = entity_id.split('.')[0]
            attributes = state.attributes
            state_value = state.state
            friendly_name = attributes.get('friendly_name', '')
            if friendly_name != '' and friendly_name.count(key) > 0:
                return {
                    'domain': domain,
                    'entity_id': entity_id,
                    'entity_name': friendly_name
                }

    async def get_area(self, name):
        _list = list(filter(lambda item: item.name == name, self.area_list))
        if len(_list) > 0:
            return _list[0]

    async def findAll_entity(self, area):
        arr = []
        if area is not None:
            obj = await self.get_area(area.get('area_name'))
            if obj is not None:
                word = area.get('area_words')[2].strip('的')
                registry_entity = await entity_registry.async_get_registry(self.hass)
                entities = entity_registry.async_entries_for_area(registry_entity, obj.id)
                for entity in entities:
                    state = self.hass.states.get(entity.entity_id)
                    friendly_name = state.attributes.get('friendly_name', '')
                    if friendly_name == '':
                        continue
                    if word in friendly_name:
                        entity_id = entity.entity_id
                        domain = entity_id.split('.')[0]
                        arr.append({
                            'domain': domain,
                            'entity_id': entity_id,
                            'entity_name': friendly_name
                        })
        return arr

    # match area
    async def find_area(self, text):
        areas = []
        for item in self.area_list:
            areas.append(item.name)
        area_str = '|'.join(areas)
        area = ''
        entity = None
        words = self.parser_match(text, area_str)
        if words is not None:
            area = words[1]
            entity = await self.find_entity(words[2])
        else:
            entity = await self.find_entity(text)
        
        if entity is not None:
            return {
                'area_name': area,
                'area_words': words,
                **entity
            }

        if area != '':
            return {
                'area_name': area,
                'area_words': words
            }

    async def parser_turn_off(self, text, entity):
        cmd = 'turn_off'
        if entity is not None:
            domain = entity.get('domain')
            if domain == 'cover':
                cmd = 'close_cover'
            elif domain == 'lock':
                cmd = 'lock'
        return await self.parser_turn_cmd(text, cmd, '关闭|关掉|关上|关一下|关下')

    async def parser_turn_on(self, text, entity):
        cmd = 'turn_on'
        if entity is not None:
            domain = entity.get('domain')
            if domain == 'cover':
                cmd = 'open_cover'
            elif domain == 'lock':
                cmd = 'unlock'
        return await self.parser_turn_cmd(text, cmd, '打开|开启|开一下|开下')

    async def parser_turn_cmd(self, text, cmd, key):
        matchObj = self.parser_match(text, key)
        if matchObj is not None:
            result = await self.find_area(matchObj[0])
            if result is None:
                result = await self.find_area(matchObj[2])
            if result is None:
                result = await self.find_entity_like(matchObj[2])

            if result is not None:
                return {
                    'cmd': cmd,
                    'cmd_text': matchObj[1],
                    **result
                }

    def parser_match(self, text, find):
        matchObj = re.match(rf'(.*)({find})(.*)', text)
        if matchObj is not None:
            return (matchObj.group(1), matchObj.group(2), matchObj.group(3))