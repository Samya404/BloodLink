from flask import Blueprint, request
from extensions import db, socketio
from models.inventory import BloodInventory
from models.hospital import Hospital
from models.audit import AuditLog
from utils.helpers import success_response, error_response
from utils.decorators import roles_required
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('inventory', __name__)

@bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
@roles_required('HOSPITAL', 'ADMIN')
def get_inventory():
    current_user_id = int(get_jwt_identity())
    hospital = Hospital.query.filter_by(user_id=current_user_id).first()
    
    if not hospital:
        # If Admin or hospital profile not yet linked
        inventory = BloodInventory.query.all()
    else:
        inventory = BloodInventory.query.filter_by(hospital_id=hospital.id).all()
        
    return success_response([item.to_dict() for item in inventory], 200)

@bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
@roles_required('HOSPITAL')
def add_inventory():
    current_user_id = int(get_jwt_identity())
    hospital = Hospital.query.filter_by(user_id=current_user_id).first()
    
    if not hospital:
        return error_response("NOT_FOUND", "Hospital profile not found", 404)

    data = request.get_json() or {}
    blood_group = data.get('blood_group')
    component = data.get('component', 'Whole Blood')
    units = data.get('units') if 'units' in data else data.get('available_units', 0)
    
    if not blood_group:
        return error_response("INVALID_REQUEST", "Blood group is required", 400)
        
    try:
        units = int(units)
    except (ValueError, TypeError):
        return error_response("INVALID_REQUEST", "Units must be an integer", 400)

    if units < 0:
        return error_response("INVALID_REQUEST", "Units cannot be negative", 400)

    inventory = BloodInventory.query.filter_by(
        hospital_id=hospital.id, 
        blood_group=blood_group.upper(), 
        component=component
    ).first()

    if inventory:
        old_units = inventory.available_units
        inventory.available_units = units
        action = "UPDATE_INVENTORY"
        desc = f"Updated {blood_group} {component} from {old_units} to {units}"
    else:
        inventory = BloodInventory(
            hospital_id=hospital.id,
            blood_group=blood_group.upper(),
            component=component,
            available_units=units,
            source_type='LOCAL'
        )
        db.session.add(inventory)
        action = "ADD_INVENTORY"
        desc = f"Added {units} units of {blood_group} {component}"

    db.session.flush()

    # Audit log
    audit = AuditLog(
        user_id=current_user_id,
        action=action,
        entity_type="BloodInventory",
        entity_id=inventory.id,
        description=desc
    )
    db.session.add(audit)
    db.session.commit()

    # Emit socket event
    socketio.emit('inventory_updated', {
        'hospital_id': hospital.id,
        'hospital_name': hospital.name,
        'blood_group': inventory.blood_group,
        'component': inventory.component,
        'available_units': inventory.available_units,
        'units': inventory.available_units
    })

    return success_response(inventory.to_dict(), 201)

@bp.route('/', methods=['PATCH'], strict_slashes=False)
@bp.route('/<int:id>', methods=['PATCH', 'PUT'])
@jwt_required()
@roles_required('HOSPITAL', 'ADMIN')
def update_inventory(id=None):
    current_user_id = int(get_jwt_identity())
    hospital = Hospital.query.filter_by(user_id=current_user_id).first()
    data = request.get_json() or {}

    inventory = None
    if id:
        inventory = BloodInventory.query.get(id)
    elif hospital and 'blood_group' in data:
        bg = data['blood_group'].upper()
        comp = data.get('component', 'Whole Blood')
        inventory = BloodInventory.query.filter_by(hospital_id=hospital.id, blood_group=bg).first()

    if not inventory:
        if hospital and 'blood_group' in data:
            # Create if doesn't exist
            units = data.get('units') if 'units' in data else data.get('available_units', 0)
            if int(units) < 0:
                return error_response("INVALID_REQUEST", "Units cannot be negative", 400)
            inventory = BloodInventory(
                hospital_id=hospital.id,
                blood_group=data['blood_group'].upper(),
                component=data.get('component', 'Whole Blood'),
                available_units=int(units),
                source_type='LOCAL'
            )
            db.session.add(inventory)
        else:
            return error_response("NOT_FOUND", "Inventory item not found", 404)

    units = data.get('units') if 'units' in data else data.get('available_units')
    if units is not None:
        try:
            units = int(units)
        except (ValueError, TypeError):
            return error_response("INVALID_REQUEST", "Units must be an integer", 400)

        if units < 0:
            return error_response("INVALID_REQUEST", "Units cannot be negative", 400)
        
        inventory.available_units = units

    if 'reserved_units' in data:
        inventory.reserved_units = int(data['reserved_units'])

    db.session.flush()

    audit = AuditLog(
        user_id=current_user_id,
        action="UPDATE_INVENTORY",
        entity_type="BloodInventory",
        entity_id=inventory.id,
        description=f"Updated inventory {inventory.blood_group} to {inventory.available_units} units"
    )
    db.session.add(audit)
    db.session.commit()

    socketio.emit('inventory_updated', {
        'hospital_id': inventory.hospital_id,
        'blood_group': inventory.blood_group,
        'component': inventory.component,
        'available_units': inventory.available_units,
        'units': inventory.available_units
    })

    return success_response(inventory.to_dict(), 200)

@bp.route('/audit', methods=['GET'])
@jwt_required()
@roles_required('HOSPITAL', 'ADMIN')
def get_inventory_audit():
    current_user_id = int(get_jwt_identity())
    logs = AuditLog.query.filter_by(entity_type="BloodInventory").order_by(AuditLog.created_at.desc()).all()
    return success_response([l.to_dict() for l in logs], 200)
