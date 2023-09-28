import re, logging
from homeassistant.core import split_entity_id
from homeassistant.helpers import template, entity_registry, area_registry
from .util import create_matcher

_LOGGER = logging.getLogger(__name__)

class Semantic():
    
    def __init__(self, hass):
        self.hass = hass
        self.entity_registry = None

    # cache data
    async def update(self, text):
        # 注册实体
        self.entity_registry = entity_registry.async_get(self.hass)

        entities = []
        self.areas = []
        # all state
        states = self.hass.states.async_all()
        arr = []
        for state in states:
            arr.append(state)
            entity_id = state.entity_id
            domain = split_entity_id(entity_id)[0]
            if domain == text:
                # 完全匹配到domain
                return (0, domain)

            friendly_name = state.attributes.get('friendly_name')
            if friendly_name != '' and friendly_name is not None:
                if friendly_name in text or self.aliases_in(entity_id, text):
                    entities.append({
                        'domain': domain,
                        'entity_id': entity_id,
                        'entity_name': friendly_name,
                        'state': self.hass.formatEntityState(state)
                    })
        arr.sort(reverse=True, key=lambda x:x.last_changed)
        self.states = arr
        # all area
        area = area_registry.async_get(self.hass)
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
        self.extra_entities = list(map(lambda state: { 'id': state['entity_id'], 'name': state['entity_name'], 'state': state['state'] }, self.entities))

    def get_entities_by_domain(self, domain):
      ''' 获取实体 '''
      states = self.hass.states.async_all()
      return list(filter(lambda state: split_entity_id(state.entity_id)[0] == domain, states))

    # 获取别名
    def get_aliases(self, entity_id):
        _list = []
        entity = self.entity_registry.async_get(entity_id)
        if entity is not None:
            if entity.entity_category or entity.hidden:
                # Skip configuration/diagnostic/hidden entities
                return []

            if entity.aliases:
                for alias in entity.aliases:
                    _list.append(alias)
        return _list

    # 完全匹配
    def in_aliases(self, entity_id, name) -> bool:
        aliases = self.get_aliases(entity_id)
        return len(list(filter(lambda x:name in x, aliases))) > 0

    # 模糊匹配
    def aliases_in(self, entity_id, name):
        aliases = self.get_aliases(entity_id)
        _list = list(filter(lambda x:x in name, aliases))
        if len(_list) > 0:
            return _list[0]

    # 完全匹配
    def equal_aliases(self, entity_id, name) -> bool:
        aliases = self.get_aliases(entity_id)
        return aliases.count(name) > 0

    # match entity name
    async def find_entity(self, text):
        states = self.states
        for state in states:
            entity_id = state.entity_id
            domain = entity_id.split('.')[0]
            attributes = state.attributes
            friendly_name = attributes.get('friendly_name')
            if friendly_name != '' and friendly_name is not None:
                if friendly_name in text or self.aliases_in(state.entity_id, text):
                    return {
                        'domain': domain,
                        'entity_id': entity_id,
                        'entity_name': friendly_name,
                        'state': self.hass.formatEntityState(state)
                    }
    
    # match entity name
    async def find_entity_multiple(self, text):
        _LOGGER.debug('[find_entity_multiple] %s', text)
        arr = []
        for state in self.states:
            friendly_name = state.attributes.get('friendly_name')
            if friendly_name != '' and friendly_name is not None:
                if friendly_name in text or self.aliases_in(state.entity_id, text):
                    arr.append({
                        'domain': state.entity_id.split('.')[0],
                        'id': state.entity_id,
                        'name': friendly_name,
                        'state': self.hass.formatEntityState(state)
                    })
        arr.sort(reverse=True, key=lambda x:len(x['name']))
        tmp_text = text
        for index, entity in enumerate(arr):
            entity_name = entity['name']
            alias = self.aliases_in(entity['id'], tmp_text)
            if entity_name in tmp_text:
                tmp_text = tmp_text.replace(entity_name, '')
            elif alias:
                tmp_text = tmp_text.replace(alias, '')
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
            friendly_name = attributes.get('friendly_name')
            if friendly_name is None or friendly_name == '':
                continue
            
            # 执行自定义脚本
            if domain == 'script':
                extra_data = attributes.get('extra_data')
                reply = attributes.get('reply')
                # 判断是否自定义匹配命令
                intents = attributes.get('intents', [])

                # 使用别名定义意图脚本
                if '意图脚本' in friendly_name and len(intents) == 0:
                    intents = self.get_aliases(entity_id)

                if len(intents) > 0:
                    for intent in intents:
                        match = create_matcher(intent).match(name)
                        if match is not None:
                            return {
                                'domain': domain,
                                'entity_id': entity_id,
                                'entity_name': friendly_name,
                                'extra_data': extra_data,
                                'reply': reply,
                                'slots': {key: value for key, value in match.groupdict().items()}
                            }

                cmd = friendly_name.split('=')
                if cmd.count(name) > 0:
                    return {
                        'domain': domain,
                        'entity_id': entity_id,
                        'entity_name': friendly_name,
                        'extra_data': extra_data,
                        'reply': reply
                    }
            if friendly_name == name or self.equal_aliases(entity_id, name):
                arr.append({
                    'domain': domain,
                    'entity_id': entity_id,
                    'entity_name': friendly_name,
                    'state': self.hass.formatEntityState(state),
                    'unit': attributes.get('unit_of_measurement', '')
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
            friendly_name = attributes.get('friendly_name')
            if friendly_name != '' and friendly_name is not None:
                if key in friendly_name or self.in_aliases(state.entity_id, key):
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
                registry_entity = entity_registry.async_get(self.hass)
                entities = entity_registry.async_entries_for_area(registry_entity, obj.id)
                for entity in entities:
                    entity_id = entity.entity_id
                    state = self.hass.states.get(entity_id)
                    friendly_name = state.attributes.get('friendly_name')
                    if friendly_name is None or friendly_name == '':
                        continue                    
                    if word in friendly_name or self.in_aliases(entity_id, word):
                        domain = entity_id.split('.')[0]
                        arr.append({
                            'domain': domain,
                            'id': entity_id,
                            'name': friendly_name,
                            'state': self.hass.formatEntityState(state)
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
            entity_name = words[2]
            if entity_name is not None:
                entity = await self.find_entity(entity_name)
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

    def parser_match(self, text, find):
        matchObj = re.match(rf'(.*)({find})(.*)', text)
        if matchObj is not None:
            result = (matchObj.group(1), matchObj.group(2), matchObj.group(3))
            _LOGGER.debug(result)
            return result