# db
HOSTNAME = ''
PORT = ''
DATABASE = ''
USERNAME = ''
PASSWORD = ''
DB_URI = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8'
SQLALCHEMY_DATABASE_URI = DB_URI

# 高德地图 Web API
AMAP_KEY = ''

# 高德地图 JS API
AMAP_JS_KEY = {
    'key': '',
    'scode': ''
}