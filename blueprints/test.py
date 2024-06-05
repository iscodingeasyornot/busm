from flask import Blueprint, render_template, request, redirect, url_for
from models import Route, Stop, VehicleLocation
from extensions import db 
from config import AMAP_JS_KEY
bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/route_demo')
def route_demo():
    return render_template('/test/route_demo.html')

@bp.route('/lp')
def lp():
    return render_template('/test/lp.html', amap_js_key=AMAP_JS_KEY, ls=VehicleLocation.query.all())