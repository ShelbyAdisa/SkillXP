from django.urls import path, include
from . import views

app_name = 'transport'

urlpatterns = [
    # Bus Management
    path('buses/', views.BusListCreateView.as_view(), name='bus-list'),
    path('buses/<int:pk>/', views.BusDetailView.as_view(), name='bus-detail'),
    
    # Driver Management
    path('drivers/', views.DriverListCreateView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', views.DriverDetailView.as_view(), name='driver-detail'),
    
    # Route Management
    path('routes/', views.RouteListCreateView.as_view(), name='route-list'),
    path('routes/<int:pk>/', views.RouteDetailView.as_view(), name='route-detail'),
    path('routes/<int:route_id>/optimize/', views.RouteOptimizationView.as_view(), name='route-optimize'),
    
    # Bus Stops
    path('stops/', views.BusStopListCreateView.as_view(), name='stop-list'),
    path('stops/<int:pk>/', views.BusStopDetailView.as_view(), name='stop-detail'),
    
    # Trip Management
    path('trips/', views.TripListCreateView.as_view(), name='trip-list'),
    path('trips/<int:pk>/', views.TripDetailView.as_view(), name='trip-detail'),
    path('trips/<int:pk>/gps/', views.TripDetailWithGPSView.as_view(), name='trip-detail-gps'),
    
    # Real-time Tracking & GPS
    path('trips/<int:trip_id>/start/', views.start_trip, name='start-trip'),
    path('trips/<int:trip_id>/end/', views.end_trip, name='end-trip'),
    path('trips/<int:trip_id>/gps-location/', views.GPSLocationUpdateView.as_view(), name='gps-location-update'),
    
    # Student Transport Assignments
    path('student-transport/', views.StudentTransportListCreateView.as_view(), name='student-transport-list'),
    path('student-transport/<int:pk>/', views.StudentTransportDetailView.as_view(), name='student-transport-detail'),
    path('my-transport/', views.MyStudentTransportView.as_view(), name='my-transport'),
    
    # Attendance
    path('attendance/', views.AttendanceLogListCreateView.as_view(), name='attendance-list'),
    path('trips/<int:trip_id>/bulk-attendance/', views.bulk_mark_attendance, name='bulk-attendance'),
    
    # Maintenance
    path('maintenance/', views.MaintenanceLogListCreateView.as_view(), name='maintenance-list'),
    path('maintenance/<int:pk>/', views.MaintenanceLogDetailView.as_view(), name='maintenance-detail'),
    
    # GPS Devices
    path('gps-devices/', views.GPSDeviceListCreateView.as_view(), name='gps-device-list'),
    path('gps-devices/<int:pk>/', views.GPSDeviceDetailView.as_view(), name='gps-device-detail'),
    path('gps-devices/sync/', views.sync_gps_devices, name='sync-gps-devices'),
    
    # Notifications
    path('notification-preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    
    # Emergency Alerts
    path('emergency-alerts/', views.EmergencyAlertListCreateView.as_view(), name='emergency-alert-list'),
    
    # Live Tracking & Maps
    path('live-tracking/', views.LiveTrackingView.as_view(), name='live-tracking'),
    path('live-map/', views.LiveMapView.as_view(), name='live-map'),
    path('track-student/', views.StudentBusTrackingView.as_view(), name='track-student'),
    path('track-student/<int:student_id>/', views.StudentBusTrackingView.as_view(), name='track-specific-student'),
    
    # Geocoding
    path('geocoding/', views.GeocodingView.as_view(), name='geocoding'),
    
    # Dashboard
    path('dashboard/', views.TransportDashboardView.as_view(), name='dashboard'),
    
    # Driver-specific
    path('driver/trips/', views.DriverTripsView.as_view(), name='driver-trips'),
    path('driver/current-trip/', views.DriverCurrentTripView.as_view(), name='driver-current-trip'),
]