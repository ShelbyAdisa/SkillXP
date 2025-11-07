from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import math
from django.db.models import F, Avg

def calculate_distance(lat1, lng1, lat2, lng2):
    # Calculate distance between two GPS coordinates in kilometers using Haversine formula
    R = 6371  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_eta(current_lat, current_lng, target_lat, target_lng, current_speed=0):
    # Calculate estimated time of arrival
    if not all([current_lat, current_lng, target_lat, target_lng]):
        return None
    
    # Calculate distance
    distance = calculate_distance(current_lat, current_lng, target_lat, target_lng)
    
    # Estimate time (considering traffic, stops, etc.)
    if current_speed > 0:
        # Use current speed if available
        time_hours = distance / current_speed
    else:
        # Assume average speed of 30 km/h in urban areas
        time_hours = distance / 30
    
    return max(1, round(time_hours * 60))  

def get_bus_occupancy(bus_id):
    # Get current occupancy for a bus
    cache_key = f"bus_occupancy_{bus_id}"
    occupancy = cache.get(cache_key)
    
    if not occupancy:
        from .models import Trip
        try:
            current_trip = Trip.objects.filter(
                bus_id=bus_id,
                status=Trip.TripStatus.IN_PROGRESS
            ).first()
            
            if current_trip:
                occupancy = {
                    'current': current_trip.students_onboard,
                    'capacity': current_trip.bus.capacity,
                    'percentage': (current_trip.students_onboard / current_trip.bus.capacity) * 100
                }
            else:
                occupancy = {'current': 0, 'capacity': 0, 'percentage': 0}
            
            cache.set(cache_key, occupancy, 300) 
        except:
            occupancy = {'current': 0, 'capacity': 0, 'percentage': 0}
    
    return occupancy

def get_route_efficiency(route_id):
    # Calculate route efficiency metrics
    from .models import Trip, Route
    try:
        route = Route.objects.get(id=route_id)
        
        # Get recent trips
        recent_trips = Trip.objects.filter(
            route=route,
            status=Trip.TripStatus.COMPLETED,
            scheduled_start__gte=timezone.now() - timedelta(days=30)
        )
        
        total_trips = recent_trips.count()
        if total_trips == 0:
            return {'efficiency': 0, 'on_time_rate': 0, 'avg_duration': 0}
        
        # Calculate on-time performance
        on_time_trips = recent_trips.filter(
            actual_start__lte=F('scheduled_start') + timedelta(minutes=10)
        ).count()
        on_time_rate = (on_time_trips / total_trips) * 100
        
        # Calculate average duration
        avg_duration = recent_trips.aggregate(
            avg_duration=Avg(F('actual_end') - F('actual_start'))
        )['avg_duration']
        avg_duration_minutes = avg_duration.total_seconds() / 60 if avg_duration else 0
        
        # Calculate efficiency (combination of metrics)
        efficiency = (on_time_rate * 0.6) + (max(0, 100 - (avg_duration_minutes - route.estimated_duration)) * 0.4)
        
        return {
            'efficiency': min(100, efficiency),
            'on_time_rate': on_time_rate,
            'avg_duration': avg_duration_minutes,
            'estimated_duration': route.estimated_duration
        }
        
    except Route.DoesNotExist:
        return {'efficiency': 0, 'on_time_rate': 0, 'avg_duration': 0}

def optimize_route_stops(route_id):
    # Optimize stop sequence for a route (simplified
    from .models import BusStop
    stops = BusStop.objects.filter(route_id=route_id).order_by('sequence')
    optimized_stops = list(stops)
    return optimized_stops

def validate_gps_coordinates(latitude, longitude):
    # Validate GPS coordinates
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lng <= 180:
            return True, "Valid coordinates"
        else:
            return False, "Coordinates out of range"
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"

def get_nearby_stops(latitude, longitude, radius_km=1):
    # Find bus stops within a radius
    from .models import BusStop
    from django.db.models import F, Func
    
    class EarthDistance(Func):
        function = 'earth_distance'
        template = "%(function)s(ll_to_earth(%(expressions)s), ll_to_earth(%(latitude)s, %(longitude)s))"
        
        def __init__(self, *expressions, **extra):
            extra['latitude'] = latitude
            extra['longitude'] = longitude
            super().__init__(*expressions, **extra)
    
    nearby_stops = BusStop.objects.annotate(
        distance=EarthDistance(F('latitude'), F('longitude'))
    ).filter(distance__lte=radius_km * 1000)  
    
    return nearby_stops

def format_duration(minutes):
    # Format duration in minutes to human-readable string
    if minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = minutes // 60
        mins = minutes % 60
        if mins == 0:
            return f"{int(hours)} hr"
        else:
            return f"{int(hours)} hr {int(mins)} min"

def get_transport_stats(school, days=7):
    # Get transportation statistics for a school
    since_date = timezone.now() - timedelta(days=days)
    
    from .models import Trip, AttendanceLog, MaintenanceLog, Bus
    
    stats = {
        'total_trips': Trip.objects.filter(
            bus__school=school,
            scheduled_start__gte=since_date
        ).count(),
        'completed_trips': Trip.objects.filter(
            bus__school=school,
            status=Trip.TripStatus.COMPLETED,
            scheduled_start__gte=since_date
        ).count(),
        'students_transported': AttendanceLog.objects.filter(
            trip__bus__school=school,
            is_present=True,
            created_at__gte=since_date
        ).count(),
        'active_buses': Bus.objects.filter(
            school=school,
            status=Bus.BusStatus.ACTIVE
        ).count(),
        'maintenance_alerts': MaintenanceLog.objects.filter(
            bus__school=school,
            status=MaintenanceLog.Status.SCHEDULED,
            scheduled_date__lte=timezone.now().date() + timedelta(days=7)
        ).count()
    }
    
    return stats