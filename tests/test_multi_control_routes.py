import pytest
from flask import json
from datetime import datetime, timedelta
from app.extensions import db
from app.models.user_app import UserApp
from app.apps.multi_control.models import (
    Field, Equipment, Zone, IrrigationPlan, Alert, Log, Firmware
)
import io


@pytest.fixture
def test_client(app):
    return app.test_client()


@pytest.fixture
def init_database():
    # Create test data
    test_account_id = 1
    test_field = Field(
        account_id=test_account_id,
        name="Test Field",
        pressure=50.0,
        flow_rate=20.0,
        current_zone="Zone 1"
    )
    db.session.add(test_field)
    db.session.commit()

    test_equipment = Equipment(
        account_id=test_account_id,
        field_id=test_field.id,
        name="Test Controller",
        controller_id="CTRL001"
    )
    db.session.add(test_equipment)
    db.session.commit()

    yield {
        'account_id': test_account_id,
        'field_id': test_field.id,
        'equipment_id': test_equipment.id,
        'controller_id': test_equipment.controller_id
    }

    # Cleanup
    db.session.query(Field).delete()
    db.session.query(Equipment).delete()
    db.session.query(Zone).delete()
    db.session.query(IrrigationPlan).delete()
    db.session.query(Alert).delete()
    db.session.query(Log).delete()
    db.session.query(Firmware).delete()
    db.session.commit()


class TestFieldManagement:
    def test_get_fields(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/fields/?account_id={init_database["account_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0
        assert data[0]['name'] == "Test Field"

    def test_get_field_details(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/fields/{init_database["field_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == "Test Field"

    def test_upload_kml(self, test_client, init_database):
        data = {'field_id': init_database['field_id']}
        file_data = io.BytesIO(b"Test KML content")
        response = test_client.post(
            '/multi_controls/fields/upload_kml',
            data={'file': (file_data, 'test.kml'), **data},
            content_type='multipart/form-data'
        )
        assert response.status_code == 200


class TestEquipmentManagement:
    def test_list_equipment(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/equipment/?account_id={init_database["account_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) > 0
        assert data[0]['name'] == "Test Controller"

    def test_get_equipment_details(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/equipment/{init_database["controller_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == "Test Controller"

    def test_add_equipment(self, test_client, init_database):
        data = {
            'name': 'New Controller',
            'controller_id': 'CTRL002',
            'field_id': init_database['field_id'],
            'account_id': init_database['account_id']
        }
        response = test_client.post(
            '/multi_controls/equipment/',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 201


class TestZoneManagement:
    def test_create_zone(self, test_client, init_database):
        data = {
            'name': 'Test Zone',
            'equipment_id': init_database['equipment_id'],
            'account_id': init_database['account_id'],
            'application_rate': 10.0,
            'area': 100.0
        }
        response = test_client.post(
            '/multi_controls/zones/',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 201

    def test_list_zones(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/zones/?account_id={init_database["account_id"]}')
        assert response.status_code == 200


class TestAlertManagement:
    def test_create_alert(self, test_client, init_database):
        data = {
            'field_id': init_database['field_id'],
            'account_id': init_database['account_id'],
            'alert_type': 'pressure_low',
            'message': 'Pressure below threshold'
        }
        response = test_client.post(
            '/multi_controls/alerts/',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 201

    def test_list_alerts(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/alerts/?account_id={init_database["account_id"]}')
        assert response.status_code == 200


class TestLogsAndReports:
    def test_get_logs(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/logs/?account_id={init_database["account_id"]}')
        assert response.status_code == 200

    def test_water_usage_report(self, test_client, init_database):
        response = test_client.get(
            f'/multi_controls/reports/water-usage?account_id={init_database["account_id"]}'
            f'&start_date={datetime.utcnow().isoformat()}'
            f'&end_date={(datetime.utcnow() + timedelta(days=1)).isoformat()}'
        )
        assert response.status_code == 200

    def test_system_health_report(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/reports/system-health?account_id={init_database["account_id"]}')
        assert response.status_code == 200


class TestFirmwareManagement:
    def test_list_firmware(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/firmware/?account_id={init_database["account_id"]}')
        assert response.status_code == 200

    def test_update_firmware(self, test_client, init_database):
        # First create a test firmware
        firmware = Firmware(
            account_id=init_database['account_id'],
            equipment_id=init_database['equipment_id'],
            version='1.0.0',
            release_date=datetime.utcnow(),
            changelog='Test changelog'
        )
        db.session.add(firmware)
        
        # Set equipment status to ACTIVE
        equipment = db.session.get(Equipment, init_database['equipment_id'])
        equipment.status = 'ACTIVE'
        
        db.session.commit()

        data = {'firmware_id': firmware.id}
        response = test_client.post(
            f'/multi_controls/firmware/update/{init_database["controller_id"]}',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200


class TestSystemStatus:
    def test_system_status(self, test_client, init_database):
        response = test_client.get(f'/multi_controls/status/?account_id={init_database["account_id"]}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'equipment' in data

    def test_ping(self, test_client):
        response = test_client.get('/multi_controls/ping')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok' 