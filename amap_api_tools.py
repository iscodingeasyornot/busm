# 与高德地图的API交互
import requests
from extensions import db
from models import Stop

import config

# 计算两点(两站)的驾驶距离, 以用于计算"线路"页面中的线路距离
def get_drive_distance_db(a, b):
    a = db.session.query(Stop).filter(Stop.id == a).first()
    origin = f"{a.longitude},{a.latitude}"
    b = db.session.query(Stop).filter(Stop.id == b).first()
    destination = f"{b.longitude},{b.latitude}"
    distance = get_drive_distance(origin, destination)
    return distance


def get_drive_distance(origin, destination):
    url = "https://restapi.amap.com/v3/direction/driving"
    parameters = {
        'key': config.AMAP_KEY,
        'origin': origin,
        'destination': destination,
        'output': 'json'
    }
    response = requests.get(url, params=parameters)
    data = response.json()

    if data['status'] == '1':
        route = data['route']
        for path in route['paths']:
            distance = path['distance']
            return distance
    else:
        return "Error: " + data['info']

# 坐标转换 - wgs84 to gcj02
def wgs84_to_gcj02(lng, lat):
    url = "https://restapi.amap.com/v3/assistant/coordinate/convert"
    parameters = {
        'key': config.AMAP_KEY,
        'locations': f"{lng},{lat}",
        'coordsys': 'gps'
    }
    response = requests.get(url, params=parameters)
    data = response.json()
    if data['status'] == '1':
        location = data['locations']
        lng = location.split(',')[0]
        lat = location.split(',')[1]
        return lng, lat
    else:
        return "Error: " + data['info']

# 从高德地图导入车站
import pandas as pd
import json
import re
import time
import math

def get_dt(city,line):
    key = config.AMAP_KEY
    url = 'https://restapi.amap.com/v3/bus/linename?s=rsv3&extensions=all&key='+key+'&output=json&city={}&offset=2&keywords={}&platform=JS'.format(city,line)
    r = requests.get(url).text
    rt = json.loads(r)
    try:
        if rt['buslines']:
            if len(rt['buslines']) == 0:  #有名称没数据
                print('no data in list..')
            else:
                du = []
                for cc in range(len(rt['buslines'])):
                    dt = {}
                    dt['line_name'] = rt['buslines'][cc]['name'] 
                    st_name = []
                    st_coords = []
                    st_sequence = []
                    for st in rt['buslines'][cc]['busstops']:
                        st_name.append(st['name'])
                        st_coords.append(st['location'])
                        st_sequence.append(st['sequence'])
    
                    dt['station_name'] = st_name
                    dt['station_coords'] = st_coords
                    dt['sequence'] = st_sequence
                    du.append(dt)                
                dm = pd.DataFrame(du)
                return dm
        else:
            pass
    except:
        print('error..try it again..')
        time.sleep(2)
        get_dt(city,line)