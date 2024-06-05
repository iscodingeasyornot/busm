from flask import Blueprint, render_template, request, redirect, url_for
from models import Route, Vehicle, VehicleApiToken
from extensions import db   

bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@bp.route('/')
def index():
    vehicles = Vehicle.query.all()
    
    return render_template('vehicles.html', vehicles=vehicles)

@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        plate = request.form.get('plate')
        size = request.form.get('size')
        onRoute = request.form.get('on_route')
        token = request.form.get('token')
        #status = request.form.get('status')
        status = 1
        
        # 先添加车辆到Vehicle, 再拿到id添加到VehicleApiToken
        vehicle = Vehicle(plate=plate, size=size, onRoute=onRoute, status=status)
        db.session.add(vehicle)

        vehicle = Vehicle.query.filter_by(plate=plate).first()
        vehicleId = vehicle.id
        vehicleApiToken = VehicleApiToken(vehicleId=vehicleId, token=token)
        db.session.add(vehicleApiToken)

        db.session.commit()
        
        return redirect(url_for('vehicles.index'))
    if request.method == 'GET':
        return render_template('vehicle_add.html')
