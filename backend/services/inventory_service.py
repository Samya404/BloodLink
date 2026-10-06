from extensions import db, socketio
from models.inventory import BloodInventory, AuditLog
from services.notification_service import NotificationService
from services.external_blood_provider import get_blood_provider

class InventoryService:
    @staticmethod
    def get_inventory(hospital_id=None, blood_group=None, component=None):
        query = BloodInventory.query
        if hospital_id:
            query = query.filter_by(hospital_id=hospital_id)
        if blood_group:
            query = query.filter_by(blood_group=blood_group)
        if component:
            query = query.filter_by(component=component)
        return query.all()

    @staticmethod
    def update_inventory(inventory_id, data, user_id):
        inventory = BloodInventory.query.get(inventory_id)
        if not inventory:
            raise ValueError("Inventory not found")
        
        old_units = inventory.units
        inventory.units = data.get('units', inventory.units)
        
        audit = AuditLog(
            inventory_id=inventory.id,
            user_id=user_id,
            action="UPDATE",
            previous_value=str(old_units),
            new_value=str(inventory.units)
        )
        db.session.add(audit)
        db.session.commit()
        
        socketio.emit('inventory_updated', {'inventory_id': inventory.id, 'units': inventory.units})
        InventoryService.check_low_stock(inventory.hospital_id)
        
        return inventory

    @staticmethod
    def add_inventory(hospital_id, data, user_id):
        inventory = BloodInventory(
            hospital_id=hospital_id,
            blood_group=data['blood_group'],
            component=data.get('component', 'WHOLE_BLOOD'),
            units=data['units']
        )
        db.session.add(inventory)
        db.session.commit()
        
        audit = AuditLog(
            inventory_id=inventory.id,
            user_id=user_id,
            action="CREATE",
            previous_value="0",
            new_value=str(inventory.units)
        )
        db.session.add(audit)
        db.session.commit()
        
        socketio.emit('inventory_updated', {'inventory_id': inventory.id, 'units': inventory.units})
        return inventory

    @staticmethod
    def check_low_stock(hospital_id):
        low_stock_items = BloodInventory.query.filter(
            BloodInventory.hospital_id == hospital_id,
            BloodInventory.units < 5
        ).all()
        
        for item in low_stock_items:
            NotificationService.notify_low_stock(hospital_id, item.blood_group, item.units)

    @staticmethod
    def get_availability(blood_group, city=None, component=None):
        # Local DB query
        query = BloodInventory.query.filter_by(blood_group=blood_group)
        if component:
            query = query.filter_by(component=component)
        local_results = query.all()
        
        # External Provider query
        provider = get_blood_provider()
        external_results = provider.search_availability(blood_group, city=city, component=component)
        
        return {
            'local': local_results,
            'external': external_results
        }
