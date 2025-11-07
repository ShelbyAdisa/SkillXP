from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import (
    Bus, Driver, Route, BusStop, Trip, LocationUpdate,
    StudentTransport, AttendanceLog, MaintenanceLog,
    NotificationPreference, EmergencyAlert, GPSDevice
)
from .serializers import (
    BusSerializer, DriverSerializer, RouteSerializer, BusStopSerializer,
    TripSerializer, LocationUpdateSerializer, StudentTransportSerializer,
    AttendanceLogSerializer, MaintenanceLogSerializer, NotificationPreferenceSerializer,
    EmergencyAlertSerializer, LiveLocationSerializer, TripStartSerializer, TripEndSerializer,
    TransportDashboardSerializer, BusLocationSerializer, GPSDeviceSerializer
)
from .permissions import (
    IsSchoolMember, CanManageTransport, IsDriver, IsParentOrStudent,
    CanViewStudentTransport, CanUpdateLocation, CanMarkAttendance,
    IsOwnerOrAdmin, CanViewLiveTracking, CanCreateEmergencyAlert
)
from .services import OpenStreetMapService, RealTimeTrackingService, GPSService

User = get_user_model()

# GPS Enhanced Views
class GPSLocationUpdateView(APIView):
    # Enhanced GPS location update endpoint with validation
    permission_classes = [permissions.IsAuthenticated, CanUpdateLocation]
    
    def post(self, request, trip_id):
        try:
            trip = Trip.objects.get(id=trip_id, driver=request.user.driver_profile)
            
            serializer = LiveLocationSerializer(data=request.data)
            if serializer.is_valid():
                location_data = serializer.validated_data
                
                # Validate GPS coordinates
                is_valid, message = GPSService.validate_coordinates(
                    location_data['latitude'], 
                    location_data['longitude']
                )
                
                if not is_valid:
                    return Response(
                        {'error': f'Invalid GPS coordinates: {message}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check GPS accuracy
                if (location_data.get('accuracy') and 
                    location_data['accuracy'] > getattr(settings, 'MIN_GPS_ACCURACY', 50)):
                    return Response(
                        {'error': f'GPS accuracy too low: {location_data["accuracy"]}m'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Add device info
                location_data['device_id'] = getattr(request.user.driver_profile, 'device_id', 'mobile_app')
                
                # Create location update
                location_update = LocationUpdate.objects.create(
                    trip=trip,
                    **location_data
                )
                
                # Update trip current location
                trip.current_latitude = location_data['latitude']
                trip.current_longitude = location_data['longitude']
                trip.last_location_update = timezone.now()
                trip.location_accuracy = location_data.get('accuracy')
                trip.location_heading = location_data.get('heading')
                trip.location_altitude = location_data.get('altitude')
                
                if location_data.get('speed'):
                    trip.average_speed = location_data['speed']
                    trip.max_speed = max(trip.max_speed or 0, location_data['speed'])
                
                # Calculate distance traveled (simplified)
                if trip.current_latitude and trip.current_longitude:
                    last_update = LocationUpdate.objects.filter(
                        trip=trip
                    ).exclude(id=location_update.id).order_by('-created_at').first()
                    
                    if last_update:
                        distance = GPSService.calculate_distance(
                            float(last_update.latitude), float(last_update.longitude),
                            float(location_data['latitude']), float(location_data['longitude'])
                        )
                        trip.distance_traveled = (trip.distance_traveled or 0) + distance
                
                trip.save()
                
                # Check for arrival notifications
                RealTimeTrackingService.should_send_arrival_notification(trip, None, 0)
                
                # Calculate ETAs
                self.update_etas(trip)
                
                return Response({
                    'message': 'Location updated successfully',
                    'update_id': str(location_update.id),
                    'timestamp': location_update.created_at.isoformat()
                })
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Trip.DoesNotExist:
            return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def update_etas(self, trip):
        # Update ETAs for next stop and school
        if not (trip.current_latitude and trip.current_longitude):
            return
        
        # Calculate ETA to next stop
        next_stop, distance = RealTimeTrackingService.calculate_next_stop(
            trip, float(trip.current_latitude), float(trip.current_longitude)
        )
        
        if next_stop:
            eta_minutes = GPSService.calculate_eta(
                float(trip.current_latitude), float(trip.current_longitude),
                float(next_stop.latitude), float(next_stop.longitude),
                float(trip.average_speed or 30)
            )
            trip.next_stop_eta = timezone.now() + timedelta(minutes=eta_minutes)
        
        # Calculate ETA to school (last stop)
        school_stop = trip.route.stops.order_by('-sequence').first()
        if school_stop:
            eta_minutes = GPSService.calculate_eta(
                float(trip.current_latitude), float(trip.current_longitude),
                float(school_stop.latitude), float(school_stop.longitude),
                float(trip.average_speed or 30)
            )
            trip.school_eta = timezone.now() + timedelta(minutes=eta_minutes)
        
        trip.save()

class RouteOptimizationView(APIView):
    # Optimize bus routes using OpenStreetMap API
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def post(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id, school=request.user.school)
            stops = route.stops.order_by('sequence')
            
            if stops.count() < 2:
                return Response({'error': 'Route needs at least 2 stops'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use OpenStreetMap to optimize route
            osm_service = OpenStreetMapService()  
            
            # Calculate route from first to last stop
            first_stop = stops.first()
            last_stop = stops.last()
            
            route_data = osm_service.get_route_with_eta(  
                float(first_stop.latitude), float(first_stop.longitude), 
                float(last_stop.latitude), float(last_stop.longitude)
            )
            
            if not route_data:
                return Response({'error': 'Could not calculate optimized route'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update route with optimized data
            route.total_distance = route_data['distance_meters'] / 1000 
            route.estimated_duration = route_data['duration_seconds'] // 60  
            route.save()
            
            return Response({
                'message': 'Route optimized successfully',
                'optimized_route': {
                    'distance': route_data['distance_text'],
                    'duration': route_data['duration_text'],
                    'eta': route_data['eta'].isoformat()
                }
            })
            
        except Route.DoesNotExist:
            return Response({'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)
class GeocodingView(APIView):
    # Geocoding service for address to coordinates conversion
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def post(self, request):
        address = request.data.get('address')
        if not address:
            return Response({'error': 'Address is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        osm_service = OpenStreetMapService() 
        result = osm_service.geocode_address(address)  
        
        if result:
            return Response({
                'address': address,
                'coordinates': {
                    'latitude': result['latitude'],
                    'longitude': result['longitude']
                },
                'formatted_address': result['formatted_address']
            })
        else:
            return Response({'error': 'Could not geocode address'}, status=status.HTTP_400_BAD_REQUEST)
class LiveMapView(APIView):
    # Generate live map with bus locations
    permission_classes = [permissions.IsAuthenticated, CanViewLiveTracking]
    
    def get(self, request):
        school = request.user.school
        
        # Get active trips with locations
        active_trips = Trip.objects.filter(
            bus__school=school,
            status=Trip.TripStatus.IN_PROGRESS,
            last_location_update__gte=timezone.now() - timedelta(minutes=5)
        ).select_related('bus', 'route', 'driver__user')
        
        # Prepare locations for map
        locations = []
        for trip in active_trips:
            if trip.current_latitude and trip.current_longitude:
                locations.append({
                    'bus_number': trip.bus.bus_number,
                    'route_name': trip.route.name,
                    'latitude': float(trip.current_latitude),
                    'longitude': float(trip.current_longitude),
                    'speed': float(trip.average_speed or 0),
                    'students_onboard': trip.students_onboard,
                    'driver': trip.driver.user.get_display_name(),
                    'last_update': trip.last_location_update.isoformat() if trip.last_location_update else None
                })
        
        # Generate static map using OpenStreetMap
        static_map_url = None
        if locations:
            # Use the first location for static map center
            first_location = locations[0]
            static_map_url = OpenStreetMapService.get_static_map(  
                first_location['latitude'], 
                first_location['longitude']
            )
        
        return Response({
            'active_buses': len(locations),
            'bus_locations': locations,
            'static_map_url': static_map_url,
            'last_updated': timezone.now().isoformat()
        })
# Enhanced Trip Views with GPS
class TripDetailWithGPSView(generics.RetrieveAPIView):
    # Enhanced trip detail with GPS data and route information
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewLiveTracking]
    queryset = Trip.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Add GPS and route data
        response_data = serializer.data
        
        # Get location history
        location_updates = LocationUpdate.objects.filter(
            trip=instance
        ).order_by('-created_at')[:50]  
        
        response_data['location_history'] = LocationUpdateSerializer(
            location_updates, many=True
        ).data
        
        # Get route stops with ETAs
        stops = instance.route.stops.order_by('sequence')
        stop_data = []
        
        for stop in stops:
            if instance.current_latitude and instance.current_longitude:
                eta_minutes = GPSService.calculate_eta(
                    float(instance.current_latitude), float(instance.current_longitude),
                    float(stop.latitude), float(stop.longitude),
                    float(instance.average_speed or 30)
                )
            else:
                eta_minutes = None
            
            stop_data.append({
                'id': stop.id,
                'name': stop.name,
                'sequence': stop.sequence,
                'latitude': float(stop.latitude),
                'longitude': float(stop.longitude),
                'address': stop.address,
                'eta_minutes': eta_minutes,
                'is_pickup_point': stop.is_pickup_point,
                'is_dropoff_point': stop.is_dropoff_point
            })
        
        response_data['route_stops'] = stop_data
        
        # Calculate overall trip progress
        if instance.distance_traveled and instance.route.total_distance:
            progress_percentage = (float(instance.distance_traveled) / float(instance.route.total_distance)) * 100
            response_data['progress_percentage'] = min(100, float(progress_percentage))
        else:
            response_data['progress_percentage'] = 0
        
        return Response(response_data)

# GPS Device Management
class GPSDeviceListCreateView(generics.ListCreateAPIView):
    serializer_class = GPSDeviceSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        return GPSDevice.objects.filter(bus__school=self.request.user.school).select_related('bus')
    
    def perform_create(self, serializer):
        serializer.save()

class GPSDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GPSDeviceSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = GPSDevice.objects.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageTransport])
def sync_gps_devices(request):
    # Sync GPS devices status and update bus locations
    from .tasks import sync_gps_devices_status
    
    # Trigger background task
    sync_gps_devices_status.delay(request.user.school.id)
    
    return Response({'message': 'GPS devices sync initiated'})

# Bus Management Views
class BusListCreateView(generics.ListCreateAPIView):
    serializer_class = BusSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        return Bus.objects.filter(school=self.request.user.school).select_related(
            'current_driver', 'current_route'
        )
    
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class BusDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = Bus.objects.all()

# Driver Management Views
class DriverListCreateView(generics.ListCreateAPIView):
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        return Driver.objects.filter(
            user__school=self.request.user.school
        ).select_related('user', 'assigned_bus')

class DriverDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = Driver.objects.all()

# Route Management Views
class RouteListCreateView(generics.ListCreateAPIView):
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        return Route.objects.filter(school=self.request.user.school).prefetch_related('stops')
    
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

class RouteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = Route.objects.all()

# Bus Stop Views
class BusStopListCreateView(generics.ListCreateAPIView):
    serializer_class = BusStopSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        route_id = self.request.query_params.get('route_id')
        if route_id:
            return BusStop.objects.filter(route_id=route_id)
        return BusStop.objects.filter(route__school=self.request.user.school)

class BusStopDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BusStopSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = BusStop.objects.all()

# Trip Management Views
class TripListCreateView(generics.ListCreateAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        queryset = Trip.objects.filter(
            bus__school=self.request.user.school
        ).select_related('bus', 'route', 'driver__user')
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date if provided
        date_filter = self.request.query_params.get('date')
        if date_filter:
            target_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            queryset = queryset.filter(scheduled_start__date=target_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()

class TripDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = Trip.objects.all()

# Real-time Tracking Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanUpdateLocation])
def start_trip(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user.driver_profile)
        
        serializer = TripStartSerializer(data=request.data)
        if serializer.is_valid():
            if trip.status != Trip.TripStatus.SCHEDULED:
                return Response(
                    {'error': 'Trip can only be started from scheduled status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            trip.status = Trip.TripStatus.IN_PROGRESS
            trip.actual_start = timezone.now()
            trip.current_latitude = serializer.validated_data['start_location_lat']
            trip.current_longitude = serializer.validated_data['start_location_lng']
            trip.save()
            
            # Create initial location update
            LocationUpdate.objects.create(
                trip=trip,
                latitude=serializer.validated_data['start_location_lat'],
                longitude=serializer.validated_data['start_location_lng']
            )
            
            return Response({'message': 'Trip started successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanUpdateLocation])
def end_trip(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, driver=request.user.driver_profile)
        
        serializer = TripEndSerializer(data=request.data)
        if serializer.is_valid():
            if trip.status != Trip.TripStatus.IN_PROGRESS:
                return Response(
                    {'error': 'Only trips in progress can be ended'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            trip.status = Trip.TripStatus.COMPLETED
            trip.actual_end = timezone.now()
            
            if 'end_location_lat' in serializer.validated_data:
                trip.current_latitude = serializer.validated_data['end_location_lat']
                trip.current_longitude = serializer.validated_data['end_location_lng']
            
            trip.save()
            
            # Create final location update
            LocationUpdate.objects.create(
                trip=trip,
                latitude=trip.current_latitude or 0,
                longitude=trip.current_longitude or 0
            )
            
            return Response({'message': 'Trip ended successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

# Student Transport Assignment Views
class StudentTransportListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentTransportSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        return StudentTransport.objects.filter(
            student__school=self.request.user.school
        ).select_related('student', 'route', 'bus_stop')

class StudentTransportDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentTransportSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = StudentTransport.objects.all()

class MyStudentTransportView(generics.ListAPIView):
    serializer_class = StudentTransportSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewStudentTransport]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Role.STUDENT:
            return StudentTransport.objects.filter(student=user, is_active=True)
        elif user.role == User.Role.PARENT:
            from users.models import UserProfile
            child_users = User.objects.filter(
                profile__parent_email=user.email,
                role=User.Role.STUDENT
            )
            return StudentTransport.objects.filter(student__in=child_users, is_active=True)
        
        return StudentTransport.objects.none()

# Attendance Views
class AttendanceLogListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceLogSerializer
    permission_classes = [permissions.IsAuthenticated, CanMarkAttendance]
    
    def get_queryset(self):
        return AttendanceLog.objects.filter(
            trip__bus__school=self.request.user.school
        ).select_related('trip', 'student', 'bus_stop', 'marked_by')
    
    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanMarkAttendance])
def bulk_mark_attendance(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        
        attendance_data = request.data.get('attendance', [])
        bus_stop_id = request.data.get('bus_stop_id')
        attendance_type = request.data.get('attendance_type')
        
        if not bus_stop_id or not attendance_type:
            return Response(
                {'error': 'bus_stop_id and attendance_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            bus_stop = BusStop.objects.get(id=bus_stop_id, route=trip.route)
        except BusStop.DoesNotExist:
            return Response({'error': 'Invalid bus stop'}, status=status.HTTP_400_BAD_REQUEST)
        
        created_count = 0
        for student_attendance in attendance_data:
            student_id = student_attendance.get('student_id')
            is_present = student_attendance.get('is_present', False)
            notes = student_attendance.get('notes', '')
            
            try:
                student = User.objects.get(id=student_id, role=User.Role.STUDENT)
                
                AttendanceLog.objects.create(
                    trip=trip,
                    student=student,
                    bus_stop=bus_stop,
                    attendance_type=attendance_type,
                    scheduled_time=timezone.now(),
                    actual_time=timezone.now() if is_present else None,
                    is_present=is_present,
                    marked_by=request.user,
                    notes=notes
                )
                created_count += 1
                
                # Update students onboard count
                if is_present and attendance_type == 'PICKUP':
                    trip.students_onboard = F('students_onboard') + 1
                elif is_present and attendance_type == 'DROPOFF':
                    trip.students_onboard = F('students_onboard') - 1
                
            except User.DoesNotExist:
                continue
        
        trip.save()
        
        return Response({
            'message': f'Attendance marked for {created_count} students',
            'created_count': created_count
        })
        
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)

# Maintenance Views
class MaintenanceLogListCreateView(generics.ListCreateAPIView):
    serializer_class = MaintenanceLogSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get_queryset(self):
        return MaintenanceLog.objects.filter(
            bus__school=self.request.user.school
        ).select_related('bus', 'approved_by')
    
    def perform_create(self, serializer):
        serializer.save()

class MaintenanceLogDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MaintenanceLogSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    queryset = MaintenanceLog.objects.all()

# Notification Preferences
class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

# Emergency Alerts
class EmergencyAlertListCreateView(generics.ListCreateAPIView):
    serializer_class = EmergencyAlertSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateEmergencyAlert]
    
    def get_queryset(self):
        return EmergencyAlert.objects.filter(
            trip__bus__school=self.request.user.school
        ).select_related('trip', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Live Tracking Views
class LiveTrackingView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewLiveTracking]
    
    def get(self, request):
        school = request.user.school
        
        # Get active trips with their latest locations
        active_trips = Trip.objects.filter(
            bus__school=school,
            status=Trip.TripStatus.IN_PROGRESS,
            last_location_update__gte=timezone.now() - timedelta(minutes=5)
        ).select_related('bus', 'route')
        
        bus_locations = []
        for trip in active_trips:
            if trip.current_latitude and trip.current_longitude:
                bus_locations.append({
                    'bus_id': trip.bus.id,
                    'bus_number': trip.bus.bus_number,
                    'latitude': float(trip.current_latitude),
                    'longitude': float(trip.current_longitude),
                    'status': trip.status,
                    'route_name': trip.route.name,
                    'students_onboard': trip.students_onboard,
                    'last_update': trip.last_location_update.isoformat() if trip.last_location_update else None,
                    'speed': float(trip.average_speed) if trip.average_speed else 0
                })
        
        return Response(bus_locations)

class StudentBusTrackingView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanViewStudentTransport]
    
    def get(self, request, student_id=None):
        user = request.user
        
        # Determine which student to track
        if student_id and user.role == User.Role.PARENT:
            # Parent tracking specific child
            try:
                student = User.objects.get(
                    id=student_id,
                    role=User.Role.STUDENT,
                    profile__parent_email=user.email
                )
            except User.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        elif user.role == User.Role.STUDENT:
            student = user
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get student's transport assignment
        try:
            transport = StudentTransport.objects.get(student=student, is_active=True)
        except StudentTransport.DoesNotExist:
            return Response({'error': 'No transport assignment found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Find active trip for student's route
        current_time = timezone.now()
        active_trip = Trip.objects.filter(
            route=transport.route,
            status=Trip.TripStatus.IN_PROGRESS,
            scheduled_start__date=current_time.date()
        ).first()
        
        if not active_trip:
            return Response({'error': 'No active trip found'})
        
        # Calculate ETA to student's bus stop
        if active_trip.current_latitude and active_trip.current_longitude:
            eta_minutes = GPSService.calculate_eta(
                float(active_trip.current_latitude), float(active_trip.current_longitude),
                float(transport.bus_stop.latitude), float(transport.bus_stop.longitude),
                float(active_trip.average_speed or 30)
            )
        else:
            eta_minutes = None
        
        tracking_data = {
            'student_name': student.get_display_name(),
            'bus_number': active_trip.bus.bus_number,
            'route_name': active_trip.route.name,
            'bus_stop': transport.bus_stop.name,
            'current_location': {
                'latitude': float(active_trip.current_latitude) if active_trip.current_latitude else None,
                'longitude': float(active_trip.current_longitude) if active_trip.current_longitude else None,
                'last_update': active_trip.last_location_update.isoformat() if active_trip.last_location_update else None
            },
            'eta_minutes': eta_minutes,
            'students_onboard': active_trip.students_onboard,
            'driver_name': active_trip.driver.user.get_display_name()
        }
        
        return Response(tracking_data)

# Dashboard Views
class TransportDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanManageTransport]
    
    def get(self, request):
        school = request.user.school
        
        # Calculate dashboard metrics
        active_trips = Trip.objects.filter(
            bus__school=school,
            status=Trip.TripStatus.IN_PROGRESS
        ).count()
        
        active_buses = Bus.objects.filter(
            school=school,
            status=Bus.BusStatus.ACTIVE
        ).count()
        
        total_students_transported = StudentTransport.objects.filter(
            student__school=school,
            is_active=True
        ).count()
        
        # Calculate on-time performance 
        today = timezone.now().date()
        completed_trips_today = Trip.objects.filter(
            bus__school=school,
            status=Trip.TripStatus.COMPLETED,
            scheduled_start__date=today
        )
        
        on_time_trips = completed_trips_today.filter(
            actual_start__lte=F('scheduled_start') + timedelta(minutes=10)
        ).count()
        
        total_completed_trips = completed_trips_today.count()
        on_time_performance = (on_time_trips / total_completed_trips * 100) if total_completed_trips > 0 else 0
        
        maintenance_alerts = MaintenanceLog.objects.filter(
            bus__school=school,
            status=MaintenanceLog.Status.SCHEDULED,
            scheduled_date__lte=timezone.now().date() + timedelta(days=7)
        ).count()
        
        dashboard_data = TransportDashboardSerializer({
            'active_trips': active_trips,
            'active_buses': active_buses,
            'total_students_transported': total_students_transported,
            'on_time_performance': on_time_performance,
            'maintenance_alerts': maintenance_alerts
        }).data
        
        return Response(dashboard_data)

# Driver-specific Views
class DriverTripsView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated, IsDriver]
    
    def get_queryset(self):
        driver = self.request.user.driver_profile
        today = timezone.now().date()
        
        return Trip.objects.filter(
            driver=driver,
            scheduled_start__date=today
        ).select_related('bus', 'route').order_by('scheduled_start')

class DriverCurrentTripView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDriver]
    
    def get(self, request):
        driver = request.user.driver_profile
        
        current_trip = Trip.objects.filter(
            driver=driver,
            status=Trip.TripStatus.IN_PROGRESS
        ).select_related('bus', 'route').first()
        
        if not current_trip:
            return Response({'message': 'No active trip'})
        
        serializer = TripSerializer(current_trip, context={'request': request})
        return Response(serializer.data)