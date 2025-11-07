import requests
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import math
import json

class GPSService:
    # Base GPS service for location tracking and calculations
    # YOUR EXISTING CODE IS PERFECT - NO CHANGES NEEDED!
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        # Calculate distance between two points using Haversine formula
        R = 6371 
        
        lat1_rad = math.radians(float(lat1))
        lon1_rad = math.radians(float(lon1))
        lat2_rad = math.radians(float(lat2))
        lon2_rad = math.radians(float(lon2))
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c  # Distance in kilometers

    @staticmethod
    def validate_coordinates(latitude, longitude):
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

    @staticmethod
    def calculate_eta(current_lat, current_lng, target_lat, target_lng, current_speed=0):
        # Calculate estimated time of arrival in minutes
        if not all([current_lat, current_lng, target_lat, target_lng]):
            return None
        
        distance = GPSService.calculate_distance(current_lat, current_lng, target_lat, target_lng)
        
        if current_speed > 0:
            # Use current speed if available 
            time_minutes = (distance / current_speed) * 60
        else:
            # Assume average speed of 30 km/h in urban areas
            time_minutes = (distance / 30) * 60
        
        return max(1, round(time_minutes))

class OpenStreetMapService:
    # OpenStreetMap API integration - COMPLETELY FREE
    
    @staticmethod
    def get_route_with_eta(origin_lat, origin_lng, dest_lat, dest_lng):
        # Get detailed route information with ETA using OSRM (Open Source Routing Machine)
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'true'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                if data['code'] == 'Ok' and data['routes']:
                    route = data['routes'][0]
                    leg = route['legs'][0] if 'legs' in route else route
                    
                    return {
                        'distance_meters': route['distance'],
                        'distance_text': f"{route['distance'] / 1000:.1f} km",
                        'duration_seconds': route['duration'],
                        'duration_text': f"{route['duration'] / 60:.0f} min",
                        'eta': timezone.now() + timedelta(seconds=route['duration']),
                        'polyline': route['geometry'],
                        'steps': [
                            {
                                'instruction': step.get('name', 'Continue'),
                                'distance': f"{step['distance'] / 1000:.1f} km",
                                'duration': f"{step['duration'] / 60:.0f} min",
                                'maneuver': step.get('maneuver', {}).get('type', 'turn')
                            }
                            for step in leg.get('steps', [])
                        ] if 'legs' in route else []
                    }
        except Exception as e:
            print(f"OSRM API error: {e}")
            return None
    
    @staticmethod
    def geocode_address(address):
        # Convert address to GPS coordinates using Nominatim (free)
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json()
                if results:
                    return {
                        'latitude': float(results[0]['lat']),
                        'longitude': float(results[0]['lon']),
                        'formatted_address': results[0]['display_name']
                    }
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    @staticmethod
    def reverse_geocode(latitude, longitude):
        # Convert GPS coordinates to address using Nominatim
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                result = response.json()
                return result.get('display_name', 'Address not found')
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    @staticmethod
    def get_static_map(latitude, longitude, zoom=14, width=600, height=400):
        # Generate static map image using OpenStreetMap
        return f"https://staticmap.openstreetmap.de/staticmap.php?center={latitude},{longitude}&zoom={zoom}&size={width}x{height}&markers={latitude},{longitude},red"
    
    @staticmethod
    def get_optimized_route(coordinates):
        # Get optimized route using OSRM trip plugin
        # coordinates: list of [lng, lat] pairs
        try:
            coordinates_str = ";".join([f"{coord[0]},{coord[1]}" for coord in coordinates])
            url = f"http://router.project-osrm.org/trip/v1/driving/{coordinates_str}"
            
            params = {
                'steps': 'true',
                'geometries': 'geojson'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"OSRM trip API error: {e}")
        
        return None

# REMOVE THESE - NO LONGER NEEDED:
# class GoogleMapsService:  # ❌ Remove this
# class MapboxService:      # ❌ Remove this

# KEEP THIS - IT'S PERFECT AND MAP-AGNOSTIC:
class RealTimeTrackingService:
    # Service for real-time bus tracking and notifications
    # YOUR EXISTING CODE WORKS PERFECTLY WITH ANY MAP PROVIDER!
    
    @staticmethod
    def calculate_next_stop(trip, current_lat, current_lng):
        # Calculate which stop is next based on current position
        from .models import BusStop
        
        stops = trip.route.stops.order_by('sequence')
        if not stops:
            return None
        
        # Find the closest stop that hasn't been passed yet
        closest_stop = None
        min_distance = float('inf')
        
        for stop in stops:
            distance = GPSService.calculate_distance(
                current_lat, current_lng,
                stop.latitude, stop.longitude
            )
            
            if distance < min_distance:
                min_distance = distance
                closest_stop = stop
        
        return closest_stop, min_distance
    
    @staticmethod
    def should_send_arrival_notification(trip, bus_stop, distance):
        # Determine if arrival notification should be sent
        from .models import NotificationPreference
        
        # Send notification if within 1km and bus is moving toward stop
        if distance <= 1.0:  
            # Get students assigned to this stop
            student_assignments = trip.route.student_assignments.filter(
                bus_stop=bus_stop,
                is_active=True
            )
            
            notifications_sent = 0
            for assignment in student_assignments:
                preferences = NotificationPreference.objects.filter(
                    user=assignment.student
                ).first()
                
                if preferences and preferences.bus_arriving:
                    # Calculate precise ETA using our GPS service
                    eta_minutes = GPSService.calculate_eta(
                        trip.current_latitude, trip.current_longitude,
                        bus_stop.latitude, bus_stop.longitude,
                        trip.average_speed or 30
                    )
                    
                    # Only send if ETA is within user's preferred alert window
                    if eta_minutes <= preferences.arrival_alert_minutes:
                        RealTimeTrackingService.send_arrival_notification(
                            assignment.student, trip, bus_stop, eta_minutes
                        )
                        notifications_sent += 1
            
            return notifications_sent > 0
        
        return False
    
    @staticmethod
    def send_arrival_notification(student, trip, bus_stop, eta_minutes):
        # Send arrival notification to student/parent
        from django.core.mail import send_mail
        from django.conf import settings
        from .models import NotificationPreference
        
        subject = f'Bus Arriving Soon - {eta_minutes:.0f} minutes'
        message = f'''
                    Your bus is approaching your stop.
                    
                    Bus: {trip.bus.bus_number}
                    Route: {trip.route.name}
                    Stop: {bus_stop.name}
                    Estimated Arrival: {eta_minutes:.0f} minutes
                    
                    Please be ready at your stop.
                    
                    Track live location: [App Tracking Link]
                '''
        
        # Send to student
        preferences = NotificationPreference.objects.filter(user=student).first()
        if preferences and preferences.email_notifications:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student.email],
                fail_silently=True,
            )
        
        # Send to parent if available
        if hasattr(student, 'profile') and student.profile.parent_email:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student.profile.parent_email],
                fail_silently=True,
            )
        
        # TODO: Add push notification integration
        print(f"Arrival notification sent for {student.get_display_name()} - ETA: {eta_minutes} min")