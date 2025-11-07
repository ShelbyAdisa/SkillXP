from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Bus(models.Model):
    class BusStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        MAINTENANCE = 'MAINTENANCE', 'Under Maintenance'
        INACTIVE = 'INACTIVE', 'Inactive'
        RETIRED = 'RETIRED', 'Retired'

    class FuelType(models.TextChoices):
        DIESEL = 'DIESEL', 'Diesel'
        PETROL = 'PETROL', 'Petrol'
        ELECTRIC = 'ELECTRIC', 'Electric'
        HYBRID = 'HYBRID', 'Hybrid'
        CNG = 'CNG', 'CNG'

    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='buses')
    bus_number = models.CharField(max_length=20, unique=True)
    license_plate = models.CharField(max_length=15, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2030)])
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices, default=FuelType.DIESEL)
    status = models.CharField(max_length=15, choices=BusStatus.choices, default=BusStatus.ACTIVE)
    
    # Tracking
    current_driver = models.ForeignKey('Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_bus')
    current_route = models.ForeignKey('Route', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_buses')
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    mileage = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    insurance_expiry = models.DateField(null=True, blank=True)
    
    # Features
    has_gps = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_seatbelts = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buses'
        verbose_name_plural = 'Buses'
        ordering = ['bus_number']
    
    def __str__(self):
        return f"{self.bus_number} - {self.make} {self.model}"

class Driver(models.Model):
    class LicenseType(models.TextChoices):
        LMV = 'LMV', 'Light Motor Vehicle'
        HMV = 'HMV', 'Heavy Motor Vehicle'
        PSV = 'PSV', 'Public Service Vehicle'
        INTERNATIONAL = 'INTERNATIONAL', 'International'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=20, unique=True)
    license_type = models.CharField(max_length=15, choices=LicenseType.choices, default=LicenseType.PSV)
    license_expiry = models.DateField()
    years_experience = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Contact
    emergency_contact = models.CharField(max_length=20, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(default=timezone.now)
    
    # Assignments
    assigned_bus = models.OneToOneField(Bus, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_driver')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'drivers'
        ordering = ['user__first_name']
    
    def __str__(self):
        return f"{self.user.get_display_name()} ({self.license_number})"

class Route(models.Model):
    class RouteStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'

    school = models.ForeignKey('users.School', on_delete=models.CASCADE, related_name='routes')
    name = models.CharField(max_length=100)
    route_number = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=RouteStatus.choices, default=RouteStatus.ACTIVE)
    
    # Route details
    total_distance = models.DecimalField(max_digits=6, decimal_places=2, default=0) 
    estimated_duration = models.IntegerField(default=0) 
    color = models.CharField(max_length=7, default='#3B82F6')  
    
    # Schedule
    morning_start_time = models.TimeField(null=True, blank=True)
    evening_start_time = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'routes'
        unique_together = ['school', 'route_number']
        ordering = ['route_number']
    
    def __str__(self):
        return f"{self.route_number} - {self.name}"

class BusStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=100)
    sequence = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField(blank=True)
    
    # Timing estimates
    estimated_arrival_offset = models.IntegerField(default=0) 
    
    # Properties
    is_pickup_point = models.BooleanField(default=True)
    is_dropoff_point = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'bus_stops'
        ordering = ['route', 'sequence']
        unique_together = ['route', 'sequence']
    
    def __str__(self):
        return f"{self.name} (Stop #{self.sequence})"

class Trip(models.Model):
    class TripStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        DELAYED = 'DELAYED', 'Delayed'

    class TripType(models.TextChoices):
        MORNING_PICKUP = 'MORNING_PICKUP', 'Morning Pickup'
        EVENING_DROPOFF = 'EVENING_DROPOFF', 'Evening Dropoff'
        SPECIAL = 'SPECIAL', 'Special Trip'

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    trip_type = models.CharField(max_length=15, choices=TripType.choices)
    status = models.CharField(max_length=15, choices=TripStatus.choices, default=TripStatus.SCHEDULED)
    
    # Schedule
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Real-time tracking
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Metrics
    students_onboard = models.IntegerField(default=0)
    average_speed = models.DecimalField(max_digits=5, decimal_places=2, default=0) 
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trips'
        ordering = ['-scheduled_start']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.route.name} - {self.get_trip_type_display()}"

class LocationUpdate(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='location_updates')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed = models.DecimalField(max_digits=5, decimal_places=2, default=0) 
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) 
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'location_updates'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Location update for {self.trip} at {self.created_at}"

class StudentTransport(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='transport_assignment',
                                  limit_choices_to={'role': User.Role.STUDENT})
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='student_assignments')
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='student_assignments')
    
    # Schedule
    morning_pickup_time = models.TimeField(null=True, blank=True)
    evening_dropoff_time = models.TimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_transport'
        unique_together = ['student', 'route']
    
    def __str__(self):
        return f"{self.student.get_display_name()} - {self.route.name}"

class AttendanceLog(models.Model):
    class AttendanceType(models.TextChoices):
        PICKUP = 'PICKUP', 'Pickup'
        DROPOFF = 'DROPOFF', 'Dropoff'

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='attendance_logs')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transport_attendance',
                               limit_choices_to={'role': User.Role.STUDENT})
    bus_stop = models.ForeignKey(BusStop, on_delete=models.CASCADE, related_name='attendance_logs')
    attendance_type = models.CharField(max_length=10, choices=AttendanceType.choices)
    
    # Timing
    scheduled_time = models.DateTimeField()
    actual_time = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_attendance')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'attendance_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.get_display_name()} - {self.get_attendance_type_display()} - {status}"

class MaintenanceLog(models.Model):
    class MaintenanceType(models.TextChoices):
        ROUTINE = 'ROUTINE', 'Routine Maintenance'
        REPAIR = 'REPAIR', 'Repair'
        INSPECTION = 'INSPECTION', 'Inspection'
        EMERGENCY = 'EMERGENCY', 'Emergency Repair'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=15, choices=MaintenanceType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    
    # Details
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mileage = models.DecimalField(max_digits=10, decimal_places=2) 
    
    # Schedule
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    # Personnel
    assigned_mechanic = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_maintenance')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'maintenance_logs'
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.bus.bus_number} - {self.get_maintenance_type_display()} - {self.scheduled_date}"

class NotificationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transport_notifications')
    
    # Notification types
    bus_delayed = models.BooleanField(default=True)
    bus_arriving = models.BooleanField(default=True)
    bus_location = models.BooleanField(default=False)
    attendance_marked = models.BooleanField(default=True)
    route_changes = models.BooleanField(default=True)
    emergency_alerts = models.BooleanField(default=True)
    
    # Delivery methods
    push_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    
    # Timing
    arrival_alert_minutes = models.IntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(60)])
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        unique_together = ['user']

class EmergencyAlert(models.Model):
    class AlertType(models.TextChoices):
        ACCIDENT = 'ACCIDENT', 'Accident'
        BREAKDOWN = 'BREAKDOWN', 'Vehicle Breakdown'
        MEDICAL = 'MEDICAL', 'Medical Emergency'
        WEATHER = 'WEATHER', 'Weather Emergency'
        SECURITY = 'SECURITY', 'Security Issue'
        OTHER = 'OTHER', 'Other'

    class SeverityLevel(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='emergency_alerts')
    alert_type = models.CharField(max_length=15, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=SeverityLevel.choices, default=SeverityLevel.MEDIUM)
    
    # Details
    description = models.TextField()
    location_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'emergency_alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.trip.bus.bus_number} - {self.created_at}"