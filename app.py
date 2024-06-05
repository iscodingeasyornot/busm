from flask import Flask, render_template
from flask_assets import Environment, Bundle
from extensions import db
from flask_migrate import Migrate # migrate is a tool for managing database migrations
import config


from blueprints.stops import bp as stops_bp
from blueprints.routes import bp as routes_bp
from blueprints.vehicles import bp as vehicles_bp
from blueprints.api import bp as api_bp
from blueprints.test import bp as test_bp

import pytailwindcss as pytw
import threading
 
app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)

migration = Migrate(app, db)

# assets
assets = Environment(app)

js_from_template = Bundle('js/from_template/*.js', filters='jsmin', output='gen/from_template.js')
css_main = Bundle('css/main.css', output='gen/main.css')
css_from_template = Bundle('css/from_template/*.css', output='gen/from_template.css')

assets.register('js_from_template', js_from_template)
assets.register('css_main', css_main)


#js.build()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/dash')
def dashboard():
    return render_template('dashboard.html')

@app.route('/tables')
def tables():
    return render_template('tables.html')

app.register_blueprint(stops_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(vehicles_bp)
app.register_blueprint(api_bp)
app.register_blueprint(test_bp)

# filters for jinja2
# 循环注册
import filters

for filter_name in dir(filters):
    filter_func = getattr(filters, filter_name)
    if callable(filter_func):
        app.jinja_env.filters[filter_name] = filter_func

DEV = False
DEV = True

if __name__ == '__main__':
    if DEV:
        # 创建一个线程来运行 pytw.run
        pytw_thread = threading.Thread(target=pytw.run, args=(['-i', 'static/css/main.css', '-o', 'static/gen/main.css', '--minify', '--watch'],))
        pytw_thread.daemon = True
        pytw_thread.start()

        # 在主线程中运行 Flask 的 run 方法
        app.run(debug=True,port=50000,host='0.0.0.0')

        # 等待 pytw.run 线程结束
        pytw_thread.join()
    else:
        # 以生产模式运行
        app.run(debug=False,port=50000,host='0.0.0.0')