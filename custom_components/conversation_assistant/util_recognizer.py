import datetime
import recognizers_suite as Recognizers
from recognizers_suite import Culture, ModelResult

def get_number_value(number_text):
    results = Recognizers.recognize_number(number_text, Culture.Chinese)
    length = len(results)
    if length > 0:
        result = results[length - 1]
        values = list(result.resolution.values())[0]
        return values[0]

def get_calendar_datetime(time_text):
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