from amap_api_tools import get_drive_distance_db
from models import Stop, Route

def format_time(time_str):
    if len(time_str) != 4:
        return time_str

    hours = time_str[:2]
    minutes = time_str[2:]

    return f"{hours}:{minutes}"
'''
def format_status(status):
    if status == 1:
        return "正常"
    elif status == 0:
        return "停运"
    else:
        return "未知"
'''    

# 暂停(替代)...
def format_status_for_stop(n):
    if n == 1:
        return "启用"
    elif n == 0:
        return "暂停"
    else:
        return "未知"

def route_stops_count(s):
    return len(s.split(','))

def calc_route_total_distance(s):
    stops = s.split(',')
    total_distance = 0
    for i in range(len(stops) - 1):
        distance = get_drive_distance_db(int(stops[i]), int(stops[i + 1]))
        total_distance += int(distance)
    total_distance = round(total_distance / 1000, 2)
    return f'{total_distance} km'

def get_stop_name(stop_ids, index):
    stop_id = stop_ids.split(',')[index]
    stop = Stop.query.get(stop_id)
    return stop.name

def get_route_full_name(onRoute):
    if onRoute == None:
        return '未指定'
    else:
        route = Route.query.get(onRoute)
        return f'{route.name} - {route.rSubName}'