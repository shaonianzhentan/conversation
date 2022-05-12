import re
from homeassistant.helpers import template, entity_registry, area_registry

class Semantic():
    
    def __init__(self, hass):
        self.hass = hass

    async def parser(self, text):
        entities = []
        # Query entity first
        entity = await self.find_entity(text)

        # Then query the area
        area = await self.find_area(text)

        # if the entity is None, the first device in the query area
        if entity is None:
            entities = await self.findAll_entity(area)
        else:
            entities.append(entity)

        slots = []
        # match turn on
        result = await self.parser_turn_on(text)
        if result is not None:
            slots.append(result)
        # match turn off
        result = await self.parser_turn_off(text)
        if result is not None:
            slots.append(result)
        return {
            'input': text,
            'slots': slots,
            'area': area,
            'entities': entities
        }

    # match entity name
    async def find_entity(self, text):
        states = self.hass.states.async_all()
        for state in states:
            entity_id = state.entity_id
            domain = entity_id.split('.')[0]
            attributes = state.attributes
            state_value = state.state
            friendly_name = attributes.get('friendly_name')
            # 执行自定义脚本
            if domain == 'script':
                cmd = friendly_name.split('=')
                if cmd.count(text) > 0:
                    return {
                        'domain': domain,
                        'entity_id': entity_id,
                        'entity_name': friendly_name
                    }
            if friendly_name is not None and text.count(friendly_name) > 0:
                return {
                    'domain': domain,
                    'entity_id': entity_id,
                    'entity_name': friendly_name
                }

    # match entity name
    async def find_entity_like(self, key):
        states = self.hass.states.async_all()
        for state in states:
            entity_id = state.entity_id
            domain = entity_id.split('.')[0]
            attributes = state.attributes
            state_value = state.state
            friendly_name = attributes.get('friendly_name')
            if friendly_name is not None and friendly_name.count(key) > 0:
                return {
                    'domain': domain,
                    'entity_id': entity_id,
                    'entity_name': friendly_name
                }

    async def get_area_list(self):
        area = await area_registry.async_get_registry(self.hass)
        return area.async_list_areas()

    async def get_area(self, name):
        area_list = await self.get_area_list()
        _list = list(filter(lambda item: item.name == name, area_list))
        if len(_list) > 0:
            return _list[0]

    async def findAll_entity(self, area):
        arr = []
        if area is not None:
            obj = await self.get_area(area.get('area_name'))
            if obj is not None:
                print(obj)
                word = area.get('area_words')[2].strip('的')

                registry_entity = await entity_registry.async_get_registry(self.hass)
                entities = entity_registry.async_entries_for_area(registry_entity, obj.id)
                for entity in entities:
                    entity_id = entity.entity_id
                    entity_name = entity.name or entity.original_name
                    domain = entity_id.split('.')[0]

                    if word in entity_name:
                        arr.append({
                            'domain': domain,
                            'entity_id': entity_id,
                            'entity_name': entity_name
                        })
        return arr

    # match area
    async def find_area(self, text):
        area_list = await self.get_area_list()
        areas = []
        for item in area_list:
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

    async def parser_turn_off(self, text):
        return await self.parser_turn_cmd(text, 'turn_off', '关闭|关掉|关上|关一下|关下')

    async def parser_turn_on(self, text):
        return await self.parser_turn_cmd(text, 'turn_on', '打开|开启|启动|开一下|开下')

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