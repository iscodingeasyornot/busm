from flask import Blueprint, render_template, request, redirect, url_for
from models import Route, Stop
from extensions import db   

from config import AMAP_JS_KEY

bp = Blueprint('routes', __name__, url_prefix='/routes')

@bp.route('/')
def index():
    routes = Route.query.all()
    return render_template('routes.html', routes=routes)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        stops = Stop.query.all()
        stops = [stop_to_dict(stop) for stop in stops]
        return render_template('routes_create.html', amap_js_key=AMAP_JS_KEY, stops=stops)
    if request.method == 'POST':
        name = request.form.get('name')
        rId = request.form.get('rId')
        subname = request.form.get('subname')
        boardname = request.form.get('boardname')
        stops = request.form.get('stopIdsString')
        firstBusTime = request.form.get('first_hour') + request.form.get('first_min')
        lastBusTime = request.form.get('last_hour') + request.form.get('last_min')

        if Route.query.filter_by(name=name).first() == None:
            rSubId = 1
        elif Route.query.filter_by(name=name).first() != None:
            rSubId = Route.query.filter_by(name=name).count() + 1
        elif subname == '环线':
            rSubId = 0

        status = 1

        route = Route(name=name, rId=rId, rSubName=subname, boardName=boardname, stops=stops, firstBusTime=firstBusTime, lastBusTime=lastBusTime, rSubId=rSubId, status=status)
        db.session.add(route)
        db.session.commit()
        return redirect(url_for('routes.index'))
    
def stop_to_dict(stop):
    return {
        'id': stop.id,
        'name': stop.name,
        'label': stop.label,
        #'address': stop.address,
        'latitude': stop.latitude,
        'longitude': stop.longitude,
        'status': stop.status,
        'created_at': stop.created_at.isoformat() if stop.created_at else None,
    }

@bp.route('/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        route = Route.query.get(id)
        stops = Stop.query.all()
        stops = [stop_to_dict(stop) for stop in stops]
        return render_template('routes_edit.html', route=route, amap_js_key=AMAP_JS_KEY, stops=stops)
    if request.method == 'POST':
        name = request.form.get('name')
        rId = request.form.get('rId')
        subname = request.form.get('subname')
        boardname = request.form.get('boardname')
        stops = request.form.get('stopIdsString')
        firstBusTime = request.form.get('first_hour') + request.form.get('first_min')
        lastBusTime = request.form.get('last_hour') + request.form.get('last_min')

        if Route.query.filter_by(name=name).first() == None:
            rSubId = 1
        elif Route.query.filter_by(name=name).first() != None:
            rSubId = Route.query.filter_by(name=name).count() + 1
        elif subname == '环线':
            rSubId = 0

        status = 1
        route = Route.query.get(id)
        route.name = name
        route.rId = rId
        route.rSubName = subname
        route.boardName = boardname
        route.stops = stops
        if firstBusTime != '':
            route.firstBusTime = firstBusTime
        if lastBusTime != '':
            route.lastBusTime = lastBusTime
        route.rSubId = rSubId
        route.status = status

        db.session.commit()
        return redirect(url_for('routes.index'))