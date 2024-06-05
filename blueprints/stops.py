from flask import Blueprint, render_template, request, redirect, url_for
from models import Stop
from pypinyin import lazy_pinyin
from extensions import db

from config import AMAP_JS_KEY

bp = Blueprint('stops', __name__, url_prefix='/stops')

@bp.route('/')
def index():
    stops = Stop.query.all()
    return render_template('stops.html', stops=stops)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        label = request.form.get('label')
        address = request.form.get('address')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        #status = request.form.get('status')
        
        status = 1

        # 检查 label 是否为空
        if label == '':
            # 自动生成 label
            subid = 0 # label 后缀
            while True:
                label = '_'.join(lazy_pinyin(name)) + "-" + str(subid) # 从 name 生成, name 拼音化
                if Stop.query.filter_by(label=label).first() == None:
                    break
                subid += 1
        else:
            # 检查 label 是否重复
            if Stop.query.filter_by(label=label).first() != None:
                return "label 重复"
            
        stop = Stop(name=name, label=label, address=address, latitude=latitude, longitude=longitude, status=status)
        db.session.add(stop)
        db.session.commit()
        
        return redirect(url_for('stops.index'))
    if request.method == 'GET':
        return render_template('stops_create.html', amap_js_key=AMAP_JS_KEY)

@bp.route('/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        stop = Stop.query.get(id)
        return render_template('stops_edit.html', stop=stop, amap_js_key=AMAP_JS_KEY)
    if request.method == 'POST':
        id = request.form.get('id')
        name = request.form.get('name')
        label = request.form.get('label')
        address = request.form.get('address')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        status = request.form.get('status')
        
        stop = Stop.query.get(id)
        stop.name = name
        stop.label = label
        stop.address = address
        stop.latitude = latitude
        stop.longitude = longitude
        db.session.commit()
        
        return redirect(url_for('stops.index'))

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    stop = Stop.query.get(id)
    db.session.delete(stop)
    db.session.commit()
    return redirect(url_for('stops.index'))