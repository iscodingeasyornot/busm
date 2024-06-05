import json, datetime

from flask import Blueprint, request, jsonify
from models import Vehicle, VehicleLocation, VehicleApiToken, VehiclelMesg, VehiclelMesg, Stop, Route
from extensions import db
import random, string
from amap_api_tools import wgs84_to_gcj02
import math

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 403

@bp.route('/vehicle', methods=['GET', 'POST'])
def vehicle():
    token = request.values.get('token')
    if not token:
        return jsonify(error='token is required'), 403
    v = VehicleApiToken.query.filter_by(token=token).first()
    if not v:
        return jsonify(error='token is invalid'), 403
    action = request.values.get('action')
    if not action:
        return jsonify(error='action is required'), 403
    if action == 'sayHello' or action == '0':
        return sayHello(v.vehicleId)  # 添加 return
    elif action == 'updateStatus' or action == '1':
        return vehicleUpdateStatus(v.vehicleId)  # 添加 return
    elif action == 'updateLocation' or action == '2':
        return vehicleUpdateLocation(v.vehicleId)  # 添加 return
    else:
        return jsonify(error='action is invalid'), 403

def sayHello(vehicleId):
    v = Vehicle.query.filter_by(id=vehicleId).first()
    v.lastOnline = datetime.datetime.now()
    # 记录mesg
    mesgGen(vehicleId, 1, 0, '', 1)
    db.session.commit()
    rName = f'{Route.query.filter_by(id=Vehicle.query.filter_by(id=vehicleId).first().onRoute).first().name} - {Route.query.filter_by(id=Vehicle.query.filter_by(id=vehicleId).first().onRoute).first().rSubName}'

    return jsonify(message=['hello',v.plate,rName], task=vehicleTaskCheck(vehicleId,False,False)), 200

def vehicleUpdateStatus(vehicleId):
    status = request.values.get('status')
    if not status:
        return returnParameterMissing('status')
    # 没查status是否合法
    vehicle = Vehicle.query.filter_by(id=vehicleId).first()
    vehicle.status = int(status)
    db.session.commit()
    return f'OK', 200
    
def vehicleUpdateLocation(vehicleId):
    lat = request.values.get('lat')
    lon = request.values.get('lon')
    if not lat or not lon:
        return returnParameterMissing()
    # 没有引入速度
    # 坐标系转换
    lon, lat = wgs84_to_gcj02(lon, lat)
    # 取小数点后6位
    lat = round(float(lat), 6)
    lon = round(float(lon), 6)

    location = VehicleLocation(vehicleId=vehicleId, latitude=lat, longitude=lon, updated_at=datetime.datetime.now())
    db.session.add(location)
    mesgGen(vehicleId, 1, 2, f'{lat},{lon}', 1)
    db.session.commit()
    # 在这里检查任务
    task = vehicleTaskCheck(vehicleId, lat, lon)
    rName = f'{Route.query.filter_by(id=Vehicle.query.filter_by(id=vehicleId).first().onRoute).first().name} - {Route.query.filter_by(id=Vehicle.query.filter_by(id=vehicleId).first().onRoute).first().rSubName}'
    return jsonify(message=1, location=f'{lat},{lon}', task=task, rName=rName), 200


def vehicleTaskCheck(vehicleId, lat, lon):
    def firstStop(stop):
        # 生成任务消息, message格式为[stop,status] - stop表示当前任务站点, status表示任务状态:0 - 在途, 1 - 到达
        # 以上内容弃用，因为SQL中列不能存储列表/数组
        # message现在只存储站点，状态由status存储: 100 - 在途, 101 - 到达
        mesgGen(vehicleId, 0, 3, stop, 100)
        # 返回: 当前任务, 任务状态, 下一任务
        #return [stop, 0, stops[1]]
        return [f'下一站: {Stop.query.filter_by(id=stop).first().name}','在途中',f'下一站: {Stop.query.filter_by(id=int(stops[1])).first().name}']
    
    # 从Vehicle中取出关联线路
    routeId = Vehicle.query.filter_by(id=vehicleId).first().onRoute
    if not routeId:
        return jsonify(error='vehicle has no route'), 403
    route = Route.query.filter_by(id=routeId).first()
    stops = [int(stop) for stop in route.stops.split(',')]  
    # 从VehicleMesg中取出最新的任务消息
    taskLatest = VehiclelMesg.query.filter_by(vehicleId=vehicleId, mesgType=3).order_by(VehiclelMesg.time.desc()).first()
    # 若没有，分配关联线路的第一个站点
    if not taskLatest:
        return firstStop(stops[0])
    # 若有
    taskLatest.message = int(taskLatest.message) # 转换为int
    # 检查最新的任务是否是所属线路的最后一站且状态为到达(101)
    if taskLatest.message == stops[-1] and taskLatest.status == 101:
        # 若是, 分配关联线路的第一个站点
        return firstStop(stops[0])
    # 若不是，检查当前任务状态
    '''
    # 检查最新的任务是否是所属线路的最后一站
    if taskLatest.message == stops[-1]:
        # 若状态为到达(101), 分配关联线路的第一个站点
        if taskLatest.status == 101:
            return firstStop(stops[0])
        # 若状态为在途
    '''
    # 从Stop中取出任务站点
    stop = Stop.query.filter_by(id=taskLatest.message).first()
    # 若为100，检查最新的车辆位置是否距离车站小于60m(直线距离)
    if taskLatest.status == 100:
        # 若传入lat, lon, 则使用传入的坐标
        if lat and lon:
            distance = math.sqrt((lat - stop.latitude)**2 + (lon - stop.longitude)**2)
        else:
        # 从VehicleLocation中取出最新的车辆位置
            locationLatest = VehicleLocation.query.filter_by(vehicleId=vehicleId).order_by(VehicleLocation.updated_at.desc()).first()
            # 计算距离
            distance = math.sqrt((locationLatest.latitude - stop.latitude)**2 + (locationLatest.longitude - stop.longitude)**2)
        if distance < 0.0006:
            # 若小于60m, 生成任务消息, message格式为[stop,status] - stop表示当前任务站点, status表示任务状态:0 - 在途, 1 - 到达
            mesgGen(vehicleId, 0, 3, taskLatest.message, 101)
            return [f'下一站: {Stop.query.filter_by(id=taskLatest.message).first().name}','到达',f'下一站: {Stop.query.filter_by(id=stops[stops.index(taskLatest.message)+1]).first().name}']
        else:
            # 若大于60m, 返回: 当前任务, 任务状态, 下一任务
            return [f'下一站: {Stop.query.filter_by(id=taskLatest.message).first().name}','在途',f'下一站: {Stop.query.filter_by(id=stops[stops.index(taskLatest.message)+1]).first().name}']
    # 若为1，检查最新的车辆位置是否距离车站大于60m(直线距离)
    if taskLatest.status == 101:
        # 若传入lat, lon, 则使用传入的坐标
        if lat and lon:
            distance = math.sqrt((lat - stop.latitude)**2 + (lon - stop.longitude)**2)
        else:
        # 从VehicleLocation中取出最新的车辆位置
            locationLatest = VehicleLocation.query.filter_by(vehicleId=vehicleId).order_by(VehicleLocation.updated_at.desc()).first()
            # 计算距离
            distance = math.sqrt((locationLatest.latitude - stop.latitude)**2 + (locationLatest.longitude - stop.longitude)**2)
        if distance < 0.0006:
            # 若小于60m - 未离站
            return [f'下一站: {Stop.query.filter_by(id=taskLatest.message).first().name}','到达',f'下一站: {Stop.query.filter_by(id=stops[stops.index(taskLatest.message)+1]).first().name}']
        else:
            # 若大于60m - 离站 - 进入下一任务
            # 从Route中取出下一站
            stop = stops[stops.index(taskLatest.message)+1]
            # 生成任务消息, message格式为[stop,status] - stop表示当前任务站点, status表示任务状态:0 - 在途, 1 - 到达
            mesgGen(vehicleId, 0, 3, stop, 100)
            # 返回: 当前任务, 任务状态, 下一任务
            return [f'下一站: {Stop.query.filter_by(id=stop).first().name}','在途中',f'下一站: {Stop.query.filter_by(id=stops[stops.index(taskLatest.message)+2]).first().name}']



def returnParameterMissing(parameter):
    if parameter:
        return jsonify(error=f'{parameter} is required'), 403
    else:
        return jsonify(error='parameter missing'), 403
    
# mesgFrom: 0 - 系统, 1 - 用户(车辆)
# mesgType: 0 - 通用消息, 1 - 回应消息, 2 - 位置消息, 3 - 任务消息
def mesgGen(vehicleId, mesgFrom, mesgType, message, status):
    mesgLabel = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    mesg = VehiclelMesg(vehicleId=vehicleId, mesgLabel=mesgLabel, mesgFrom=mesgFrom, mesgType=mesgType, message=message, status=status, time=datetime.datetime.now())
    db.session.add(mesg)
    db.session.commit()

@bp.route('/user', methods=['GET', 'POST'])
def userQuery():
    lat = float(request.values.get('lat'))
    lon = float(request.values.get('lon'))
    # 坐标系转换
    #lon, lat = wgs84_to_gcj02(lon, lat)
    # 查询(直线距离)最近的车站
    stops = Stop.query.all()
    stopDistances = []
    for stop in stops:
        distance = math.sqrt((lat - stop.latitude)**2 + (lon - stop.longitude)**2)
        stopDistances.append([stop.id, distance])
    stopDistances.sort(key=lambda x: x[1])

    # 获取每个站点的路线信息
    stopsInfo = []
    for i, (stopId, distance) in enumerate(stopDistances):
        stop = Stop.query.get(stopId)
        routes = Route.query.filter(Route.stops.contains(stop)).all()
        routesInfo = []
        for route in routes:
            routesInfo.append({
                "name": route.boardName,
                "towards": "火车站",  # 需要替换为实际的目的地信息
                "status": "尚未发车"  # 需要替换为实际的状态信息
            })
        stopsInfo.append({
            "order": i + 1,
            "name": stop.name,
            "distance": distance,
            "routes": routesInfo
        })

    return jsonify({"stops": stopsInfo})