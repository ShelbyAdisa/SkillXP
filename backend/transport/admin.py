from django.contrib import admin
from .models import (
    Bus, Driver, Route, BusStop, Trip, LocationUpdate,
    StudentTransport, AttendanceLog, MaintenanceLog,
    NotificationPreference, EmergencyAlert
)

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'license_plate', 'make', 'model', 'year', 'capacity', 'status', 'current_driver', 'current_route')
    list_filter = ('status', 'fuel_type', 'school', 'year')
    search_fields = ('bus_number', 'license_plate', 'make', 'model')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'bus_number', 'license_plate', 'make', 'model', 'year', 'capacity')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'fuel_type', 'current_driver', 'current_route')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance_date', 'next_maintenance_date', 'mileage', 'insurance_expiry')
        }),
        ('Features', {
            'fields': ('has_gps', 'has_ac', 'has_seatbelts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'license_type', 'license_expiry', 'is_active', 'assigned_bus')
    list_filter = ('license_type', 'is_active', 'user__school')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'license_number')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Driver Information', {
            'fields': ('user', 'license_number', 'license_type', 'license_expiry', 'years_experience')
        }),
        ('Contact & Status', {
            'fields': ('emergency_contact', 'emergency_contact_name', 'is_active', 'joined_date')
        }),
        ('Assignment', {
            'fields': ('assigned_bus',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_number', 'name', 'school', 'status', 'total_distance', 'estimated_duration')
    list_filter = ('status', 'school')
    search_fields = ('route_number', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    
    fieldsets = (
        ('Route Information', {
            'fields': ('school', 'name', 'route_number', 'description', 'status')
        }),
        ('Route Details', {
            'fields': ('total_distance', 'estimated_duration', 'color')
        }),
        ('Schedule', {
            'fields': ('morning_start_time', 'evening_start_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'sequence', 'latitude', 'longitude', 'is_pickup_point', 'is_dropoff_point')
    list_filter = ('route', 'is_pickup_point', 'is_dropoff_point')
    search_fields = ('name', 'address', 'route__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Stop Information', {
            'fields': ('route', 'name', 'sequence')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Timing & Properties', {
            'fields': ('estimated_arrival_offset', 'is_pickup_point', 'is_dropoff_point')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'trip_type', 'status', 'scheduled_start', 'actual_start', 'students_onboard')
    list_filter = ('trip_type', 'status', 'bus__school', 'scheduled_start')
    search_fields = ('bus__bus_number', 'route__name', 'driver__user__first_name')
    readonly_fields = ('created_at', 'updated_at', 'last_location_update')
    list_editable = ('status',)
    
    fieldsets = (
        ('Trip Information', {
            'fields': ('bus', 'route', 'driver', 'trip_type', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_start', 'scheduled_end', 'actual_start', 'actual_end')
        }),
        ('Real-time Tracking', {
            'fields': ('current_latitude', 'current_longitude', 'last_location_update')
        }),
        ('Metrics', {
            'fields': ('students_onboard', 'average_speed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ('trip', 'latitude', 'longitude', 'speed', 'created_at')
    list_filter = ('trip__bus__school', 'created_at')
    search_fields = ('trip__bus__bus_number', 'trip__route__name')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Location Information', {
            'fields': ('trip', 'latitude', 'longitude')
        }),
        ('Movement Data', {
            'fields': ('speed', 'heading', 'accuracy')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(StudentTransport)
class StudentTransportAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'bus_stop', 'is_active', 'morning_pickup_time', 'evening_dropoff_time')
    list_filter = ('is_active', 'route', 'bus_stop')
    search_fields = ('student__first_name', 'student__last_name', 'route__name', 'bus_stop__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Assignment', {
            'fields': ('student', 'route', 'bus_stop', 'is_active')
        }),
        ('Schedule', {
            'fields': ('morning_pickup_time', 'evening_dropoff_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'trip', 'attendance_type', 'bus_stop', 'is_present', 'actual_time', 'marked_by')
    list_filter = ('attendance_type', 'is_present', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'trip__bus__bus_number')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Attendance Record', {
            'fields': ('trip', 'student', 'bus_stop', 'attendance_type')
        }),
        ('Status & Timing', {
            'fields': ('is_present', 'scheduled_time', 'actual_time')
        }),
        ('Details', {
            'fields': ('marked_by', 'notes')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('bus', 'maintenance_type', 'status', 'scheduled_date', 'completed_date', 'cost')
    list_filter = ('maintenance_type', 'status', 'scheduled_date')
    search_fields = ('bus__bus_number', 'description', 'assigned_mechanic')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('Maintenance Information', {
            'fields': ('bus', 'maintenance_type', 'status', 'description')
        }),
        ('Cost & Mileage', {
            'fields': ('cost', 'mileage')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'completed_date')
        }),
        ('Personnel', {
            'fields': ('assigned_mechanic', 'approved_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'bus_delayed', 'bus_arriving', 'push_notifications', 'arrival_alert_minutes')
    list_filter = ('bus_delayed', 'bus_arriving', 'push_notifications', 'email_notifications')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Notification Types', {
            'fields': ('bus_delayed', 'bus_arriving', 'bus_location', 'attendance_marked', 'route_changes', 'emergency_alerts')
        }),
        ('Delivery Methods', {
            'fields': ('push_notifications', 'email_notifications', 'sms_notifications')
        }),
        ('Timing', {
            'fields': ('arrival_alert_minutes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    list_display = ('trip', 'alert_type', 'severity', 'is_resolved', 'created_by', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_resolved', 'created_at')
    search_fields = ('trip__bus__bus_number', 'description', 'created_by__first_name')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_resolved',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('trip', 'alert_type', 'severity', 'description')
        }),
        ('Location', {
            'fields': ('location_latitude', 'location_longitude')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_notes')
        }),
        ('Created By', {
            'fields': ('created_by',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Inline admins for better UX
class BusStopInline(admin.TabularInline):
    model = BusStop
    extra = 1
    readonly_fields = ('created_at',)
    classes = ['collapse']

class LocationUpdateInline(admin.TabularInline):
    model = LocationUpdate
    extra = 0
    readonly_fields = ('created_at',)
    classes = ['collapse']
    can_delete = False

class AttendanceLogInline(admin.TabularInline):
    model = AttendanceLog
    extra = 0
    readonly_fields = ('created_at', 'marked_by')
    classes = ['collapse']

class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    classes = ['collapse']

# Add inlines to relevant admins
RouteAdmin.inlines = [BusStopInline]
TripAdmin.inlines = [LocationUpdateInline, AttendanceLogInline]
BusAdmin.inlines = [MaintenanceLogInline]