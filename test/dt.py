import datetime
import recognizers_suite as Recognizers
from recognizers_suite import Culture, ModelResult

def get_calendar_datetime(time_text):
    print(time_text)
    results = Recognizers.recognize_datetime(time_text, Culture.Chinese)
    length = len(results)
    if length > 0:
        result = results[length - 1]
        values = list(result.resolution.values())[0]
        
        now = datetime.datetime.now()
        start_date_time = None

        dt_type = None
        dt_value = None

        for value in values:
            dt_type = value['type']
            _value = value['value']
            # 提醒时间大于当前时间才可行
            if dt_type == 'datetime':
                if _value > now.strftime('%Y-%m-%d %H:%M:%S'):
                    dt_value = _value
                    break
            elif dt_type == 'time':
                if _value > now.strftime('%H:%M:%S'):
                    dt_value = f'{now.strftime("%Y-%m-%d")} {_value}'
                    break
            elif dt_type == 'duration':
                dt_value = now + datetime.timedelta(seconds=+int(_value))
        # print(dt_type, dt_value)

        if dt_value is not None:
            start_date_time = dt_value
            # 结束时间
            end_date_time = datetime.datetime.strptime(start_date_time, '%Y-%m-%d %H:%M:%S')
            end_date_time = end_date_time + datetime.timedelta(seconds=+60)
            return start_date_time, end_date_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None, None

print(get_calendar_datetime('周三下午三点'))
print('=========================')
print(get_calendar_datetime('凌晨三点'))
print('=========================')
print(get_calendar_datetime('下午三点'))
print('=========================')
print(get_calendar_datetime('晚上三点'))
print('=========================')
print(get_calendar_datetime('周五三点'))
print('=========================')
print(get_calendar_datetime('明天三点'))
print('=========================')
print(get_calendar_datetime('后天三点'))
print('=========================')
print(get_calendar_datetime('前天三点'))
print('=========================')
print(get_calendar_datetime('三分钟后'))
print('=========================')
print(get_calendar_datetime('十五秒后'))
print('=========================')
print(get_calendar_datetime('过时'))