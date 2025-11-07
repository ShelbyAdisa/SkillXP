from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Bus, Driver, Route, BusStop, Trip, LocationUpdate,
    StudentTransport, AttendanceLog, MaintenanceLog,
    NotificationPreference, EmergencyAlert, GPSDevice
)
from .services import GPSService

User = get_user_model()

class GPSDeviceSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source='bus.bus_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = GPSDevice
        fields = [
            'id', 'device_id', 'bus', 'bus_number', 'device_model', 'imei_number',
            'status', 'status_display', 'last_communication', 'battery_level',
            'update_interval', 'gps_accuracy_threshold', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class BusSerializer(serializers.ModelSerializer):
    current_driver_name = serializers.CharField(source='current_driver.user.get_display_name', read_only=True)
    current_route_name = serializers.CharField(source='current_route.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    fuel_type_display = serializers.CharField(source='get_fuel_type_display', read_only=True)
    gps_status_display = serializers.CharField(source='get_gps_status_display', read_only=True)
    
    class Meta:
        model = Bus
        fields = [
            'id', 'school', 'bus_number', 'license_plate', 'make', 'model', 'year',
            'capacity', 'fuel_type', 'fuel_type_display', 'status', 'status_display',
            'current_driver', 'current_driver_name', 'current_route', 'current_route_name',
            'gps_device_id', 'last_gps_update', 'gps_status', 'gps_status_display',
            'last_maintenance_date', 'next_maintenance_date', 'mileage', 'insurance_expiry',
            'has_gps', 'has_ac', 'has_seatbelts', 'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'created_at', 'updated_at']

class DriverSerializer(serializers.ModelSerializer):
    user_display_name = serializers.CharField(source='user.get_display_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.profile.phone', read_only=True)
    license_type_display = serializers.CharField(source='get_license_type_display', read_only=True)
    assigned_bus_number = serializers.CharField(source='assigned_bus.bus_number', read_only=True)
    
    class Meta:
        model = Driver
        fields = [
            'id', 'user', 'user_display_name', 'user_email', 'user_phone',
            'license_number', 'license_type', 'license_type_display', 'license_expiry',
            'years_experience', 'emergency_contact', 'emergency_contact_name',
            'is_active', 'joined_date', 'assigned_bus', 'assigned_bus_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class BusStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusStop
        fields = [
            'id', 'route', 'name', 'sequence', 'latitude', 'longitude',
            'address', 'estimated_arrival_offset', 'is_pickup_point',
            'is_dropoff_point', 'created_at'
        ]
        read_only_fields = ['created_at']

class RouteSerializer(serializers.ModelSerializer):
    stops = BusStopSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    active_trips_count = serializers.SerializerMethodField()
    assigned_students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        fields = [
            'id', 'school', 'name', 'route_number', 'description', 'status', 'status_display',
            'total_distance', 'estimated_duration', 'color', 'morning_start_time',
            'evening_start_time', 'stops', 'active_trips_count', 'assigned_students_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['school', 'created_at', 'updated_at']
    
    def get_active_trips_count(self, obj):
        return obj.trips.filter(status=Trip.TripStatus.IN_PROGRESS).count()
    
    def get_assigned_students_count(self, obj):
        return obj.student_assignments.filter(is_active=True).count()

class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = [
            'id', 'trip', 'latitude', 'longitude', 'accuracy', 'altitude',
            'speed', 'heading', 'device_id', 'battery_level', 'signal_strength',
            'created_at'
        ]
        read_only_fields = ['created_at']

class TripSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source='bus.bus_number', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    driver_name = serializers.CharField(source='driver.user.get_display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    trip_type_display = serializers.CharField(source='get_trip_type_display', read_only=True)
    current_location = serializers.SerializerMethodField()
    next_stop = serializers.SerializerMethodField()
    eta_to_school = serializers.SerializerMethodField()
    gps_metadata = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = [
            'id', 'bus', 'bus_number', 'route', 'route_name', 'driver', 'driver_name',
            'trip_type', 'trip_type_display', 'status', 'status_display',
            'scheduled_start', 'scheduled_end', 'actual_start', 'actual_end',
            'current_latitude', 'current_longitude', 'last_location_update',
            'location_accuracy', 'location_heading', 'location_altitude',
            'distance_traveled', 'average_speed', 'max_speed',
            'next_stop_eta', 'school_eta', 'students_onboard',
            'current_location', 'next_stop', 'eta_to_school', 'gps_metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_current_location(self, obj):
        if obj.current_latitude and obj.current_longitude:
            return {
                'latitude': float(obj.current_latitude),
                'longitude': float(obj.current_longitude),
                'accuracy': float(obj.location_accuracy) if obj.location_accuracy else None,
                'heading': float(obj.location_heading) if obj.location_heading else None,
                'last_update': obj.last_location_update.isoformat() if obj.last_location_update else None
            }
        return None
    
    def get_next_stop(self, obj):
        from .services import RealTimeTrackingService
        if obj.current_latitude and obj.current_longitude:
            next_stop, distance = RealTimeTrackingService.calculate_next_stop(
                obj, float(obj.current_latitude), float(obj.current_longitude)
            )
            if next_stop:
                return {
                    'name': next_stop.name,
                    'sequence': next_stop.sequence,
                    'latitude': float(next_stop.latitude),
                    'longitude': float(next_stop.longitude),
                    'distance_km': round(distance, 2),
                    'eta_minutes': GPSService.calculate_eta(
                        float(obj.current_latitude), float(obj.current_longitude),
                        float(next_stop.latitude), float(next_stop.longitude),
                        float(obj.average_speed or 30)
                    ) if obj.average_speed else None
                }
        return None
    
    def get_eta_to_school(self, obj):
        if obj.school_eta:
            return obj.school_eta.isoformat()
        return None
    
    def get_gps_metadata(self, obj):
        return {
            'distance_traveled_km': float(obj.distance_traveled) if obj.distance_traveled else 0,
            'average_speed_kmh': float(obj.average_speed) if obj.average_speed else 0,
            'max_speed_kmh': float(obj.max_speed) if obj.max_speed else 0,
            'location_updates_count': obj.location_updates.count()
        }

class StudentTransportSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_display_name', read_only=True)
    student_grade = serializers.CharField(source='student.grade_level', read_only=True)
    route_name = serializers.CharField(source='route.name', read_only=True)
    bus_stop_name = serializers.CharField(source='bus_stop.name', read_only=True)
    bus_stop_address = serializers.CharField(source='bus_stop.address', read_only=True)
    
    class Meta:
        model = StudentTransport
        fields = [
            'id', 'student', 'student_name', 'student_grade', 'route', 'route_name',
            'bus_stop', 'bus_stop_name', 'bus_stop_address', 'morning_pickup_time',
            'evening_dropoff_time', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AttendanceLogSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_display_name', read_only=True)
    trip_details = serializers.CharField(source='trip.__str__', read_only=True)
    bus_stop_name = serializers.CharField(source='bus_stop.name', read_only=True)
    attendance_type_display = serializers.CharField(source='get_attendance_type_display', read_only=True)
    marked_by_name = serializers.CharField(source='marked_by.get_display_name', read_only=True)
    
    class Meta:
        model = AttendanceLog
        fields = [
            'id', 'trip', 'trip_details', 'student', 'student_name', 'bus_stop', 'bus_stop_name',
            'attendance_type', 'attendance_type_display', 'scheduled_time', 'actual_time',
            'is_present', 'marked_by', 'marked_by_name', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']

class MaintenanceLogSerializer(serializers.ModelSerializer):
    bus_number = serializers.CharField(source='bus.bus_number', read_only=True)
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_display_name', read_only=True)
    
    class Meta:
        model = MaintenanceLog
        fields = [
            'id', 'bus', 'bus_number', 'maintenance_type', 'maintenance_type_display',
            'status', 'status_display', 'description', 'cost', 'mileage',
            'scheduled_date', 'completed_date', 'assigned_mechanic',
            'approved_by', 'approved_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'bus_delayed', 'bus_arriving', 'bus_location',
            'attendance_marked', 'route_changes', 'emergency_alerts',
            'push_notifications', 'email_notifications', 'sms_notifications',
            'arrival_alert_minutes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

class EmergencyAlertSerializer(serializers.ModelSerializer):
    trip_details = serializers.CharField(source='trip.__str__', read_only=True)
    bus_number = serializers.CharField(source='trip.bus.bus_number', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_display_name', read_only=True)
    
    class Meta:
        model = EmergencyAlert
        fields = [
            'id', 'trip', 'trip_details', 'bus_number', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'description', 'location_latitude',
            'location_longitude', 'is_resolved', 'resolved_at', 'resolved_notes',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

# Real-time tracking serializers
class LiveLocationSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField(required=False)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    speed = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, default=0)
    heading = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    accuracy = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    altitude = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    device_id = serializers.CharField(required=False, default='')
    battery_level = serializers.IntegerField(required=False, allow_null=True)
    signal_strength = serializers.IntegerField(required=False, allow_null=True)

class TripStartSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField(required=False)
    start_location_lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    start_location_lng = serializers.DecimalField(max_digits=9, decimal_places=6)

class TripEndSerializer(serializers.Serializer):
    trip_id = serializers.IntegerField(required=False)
    end_location_lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    end_location_lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    notes = serializers.CharField(required=False)

# Dashboard serializers
class TransportDashboardSerializer(serializers.Serializer):
    active_trips = serializers.IntegerField()
    active_buses = serializers.IntegerField()
    total_students_transported = serializers.IntegerField()
    on_time_performance = serializers.FloatField()
    maintenance_alerts = serializers.IntegerField()

class BusLocationSerializer(serializers.Serializer):
    bus_id = serializers.IntegerField()
    bus_number = serializers.CharField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    status = serializers.CharField()
    route_name = serializers.CharField()
    students_onboard = serializers.IntegerField()
    last_update = serializers.DateTimeField()