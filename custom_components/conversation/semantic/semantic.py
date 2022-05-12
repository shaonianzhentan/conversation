import match, ha, turn_off, turn_on

def parser(text):
    entities = []
    # Query entity first
    entity = ha.find_entity(text)

    # Then query the area
    area = ha.find_area(text)

    # if the entity is None, the first device in the query area
    if entity is None:
        entities = ha.findAll_entity(area)
    else:
        entities.append(entity)

    # If yes, query the control method
        
    slots = []
    # match turn on
    result = turn_on.parser(text)
    if result is not None:
        slots.append(result)
    # match turn off    
    result = turn_off.parser(text)
    if result is not None:
        slots.append(result)
    return {
        'input': text,
        'slots': slots,
        'area': area,
        'entities': entities
    }