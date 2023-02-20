from recognizers_suite import recognize_datetime, Culture, ModelResult
import json, time

ENTITY_ID = ''

async def async_conversation_calendar(text):
    if '提醒我' in text:
        arr = text.split('提醒我')
        time_text = arr[0]
        thing = arr[1]
        results = recognize_datetime(time_text, Culture.Chinese)
        length = len(results)
        if length > 0:
            result = results[length - 1]
            values = list(result.resolution.values())[0]
            value = values[len(values) - 1]
            print(value)
            t = value['type']
            v = value['value']

            start_date_time = None
            if t == 'time':
                localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                if v < localtime[11:]:
                    return '时间已经过去了'
                start_date_time = localtime[:11] + v
            elif t == 'datetime':
                start_date_time = v

            if start_date_time is not None:
                service.call('calendar', 'create_event', entity_id=ENTITY_ID, start_date_time=start_date_time)
                return f'【{start_date_time}】{thing}'

hass.data.set('async_conversation_calendar', async_conversation_calendar)