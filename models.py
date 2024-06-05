from extensions import db
from datetime import datetime


class Stop(db.Model):
    __tablename__ = 'stops'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    label = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Double, nullable=False) # Float only has 6 digits of precision, so use Double
    longitude = db.Column(db.Double, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 数据库使用, 线路编号
    rId = db.Column(db.Integer, nullable=False) # 线路编号
    name = db.Column(db.String(64), nullable=False) # 线路名称
    rSubId = db.Column(db.Integer, nullable=False) # 线路子编号
    rSubName = db.Column(db.String(64), nullable=False) # 线路子名称
    boardName = db.Column(db.String(64), nullable=False) # 展示名称
    stops = db.Column(db.String(255), nullable=False) # 站点
    status = db.Column(db.Integer, nullable=False) # 状态
    created_at = db.Column(db.DateTime, default=datetime.now) # 创建时间
    firstBusTime = db.Column(db.String(4), nullable=False) # 首班车时间
    lastBusTime = db.Column(db.String(4), nullable=False) # 末班车时间

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 数据库使用
    plate = db.Column(db.String(32), nullable=False) # 车牌号
    size = db.Column(db.Integer, nullable=False) # 车辆大小(标准, 大, 小)
    onRoute = db.Column(db.Integer, nullable=True) # 所属线路
    status = db.Column(db.Integer, nullable=False) # 状态
    lastOnline = db.Column(db.DateTime) # 最后在线时间
    #route = db.relationship('Route', backref='vehicles') # 关联表

class VehicleLocation(db.Model):
    __tablename__ = 'vehicle_location'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 数据库使用
    vehicleId = db.Column(db.Integer, nullable=False) # 车辆编号 - vehicles.id
    longitude = db.Column(db.Double, nullable=False) # 经度
    latitude = db.Column(db.Double, nullable=False) # 纬度
    updated_at = db.Column(db.DateTime, default=datetime.now) # 更新时间


class VehicleApiToken(db.Model):
    __tablename__ = 'vehicle_api_tokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 数据库使用
    vehicleId = db.Column(db.Integer, nullable=False) # 车辆编号 - vehicles.id
    token = db.Column(db.String(255), nullable=False) # API Token
    status = db.Column(db.Integer, nullable=True) # 状态
    #created_at = db.Column(db.DateTime, default=datetime.now) # 创建时间
    #updated_at = db.Column(db.DateTime, default=datetime.now) # 更新时间

class VehiclelMesg(db.Model):
    __tablename__ = 'vehicle_mesg'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) # 数据库使用
    vehicleId = db.Column(db.Integer, nullable=False) # 车辆编号 - vehicles.id
    mesgLabel = db.Column(db.String(8), nullable=False) # 消息标签
    mesgFrom = db.Column(db.Integer, nullable=False) # 消息来源, 0为系统, 1为用户
    mesgType = db.Column(db.Integer, nullable=False) # 消息类型
    message = db.Column(db.String(255), nullable=False) # 消息
    status = db.Column(db.Integer, nullable=False) # 状态
    time = db.Column(db.DateTime, default=datetime.now) # 创建时间


