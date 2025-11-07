import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Trip, LocationUpdate
from django.contrib.auth import get_user_model

User = get_user_model()

class BusTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        self.trip_group_name = f'trip_{self.trip_id}'
        
        # Verify user has permission to access this trip
        if await self.verify_access():
            # Join trip group
            await self.channel_layer.group_add(
                self.trip_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Send current trip status
            trip_data = await self.get_trip_data()
            await self.send(text_data=json.dumps({
                'type': 'trip_status',
                'data': trip_data
            }))
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        # Leave trip group
        await self.channel_layer.group_discard(
            self.trip_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # Receive message from WebSocket (for driver updates)
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'location_update':
                # Handle real-time location update from driver
                await self.handle_location_update(data['data'])
            elif message_type == 'trip_status':
                # Broadcast trip status change
                await self.channel_layer.group_send(
                    self.trip_group_name,
                    {
                        'type': 'trip_status_update',
                        'data': data['data']
                    }
                )
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def handle_location_update(self, location_data):
        # Process and broadcast location update
        # Save to database
        location_update = await self.save_location_update(location_data)
        
        if location_update:
            # Broadcast to all connected clients
            await self.channel_layer.group_send(
                self.trip_group_name,
                {
                    'type': 'location_update',
                    'data': {
                        'latitude': float(location_data['latitude']),
                        'longitude': float(location_data['longitude']),
                        'speed': float(location_data.get('speed', 0)),
                        'heading': float(location_data.get('heading', 0)),
                        'accuracy': float(location_data.get('accuracy', 0)),
                        'timestamp': location_update.created_at.isoformat()
                    }
                }
            )
    
    async def location_update(self, event):
        # Receive location update from group
        await self.send(text_data=json.dumps({
            'type': 'location_update',
            'data': event['data']
        }))
    
    async def trip_status_update(self, event):
        # Receive trip status update from group
        await self.send(text_data=json.dumps({
            'type': 'trip_status',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def verify_access(self):
        # Verify user has permission to access this trip
        user = self.scope['user']
        if not user.is_authenticated:
            return False
        
        try:
            trip = Trip.objects.get(id=self.trip_id)
            
            # Admin and School admin can access any trip
            if user.role in ['ADMIN', 'SCHOOL_ADMIN']:
                return True
            
            # Driver can access their own trips
            if hasattr(user, 'driver_profile') and trip.driver == user.driver_profile:
                return True
            
            # Parents and Students can access trips for their assigned routes
            from .models import StudentTransport
            if user.role in ['STUDENT', 'PARENT']:
                if user.role == 'STUDENT':
                    assignments = StudentTransport.objects.filter(student=user, is_active=True)
                else:  # PARENT
                    # Get children's assignments
                    children = User.objects.filter(profile__parent_email=user.email)
                    assignments = StudentTransport.objects.filter(student__in=children, is_active=True)
                
                return assignments.filter(route=trip.route).exists()
            
            return False
            
        except Trip.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_trip_data(self):
        # Get current trip data
        try:
            trip = Trip.objects.select_related('bus', 'route', 'driver__user').get(id=self.trip_id)
            
            # Get recent location updates
            recent_updates = LocationUpdate.objects.filter(
                trip=trip
            ).order_by('-created_at')[:10]
            
            location_history = [
                {
                    'latitude': float(update.latitude),
                    'longitude': float(update.longitude),
                    'timestamp': update.created_at.isoformat()
                }
                for update in recent_updates
            ]
            
            return {
                'trip_id': trip.id,
                'bus_number': trip.bus.bus_number,
                'route_name': trip.route.name,
                'status': trip.status,
                'driver_name': trip.driver.user.get_display_name(),
                'current_location': {
                    'latitude': float(trip.current_latitude) if trip.current_latitude else None,
                    'longitude': float(trip.current_longitude) if trip.current_longitude else None,
                    'last_update': trip.last_location_update.isoformat() if trip.last_location_update else None
                },
                'location_history': location_history,
                'students_onboard': trip.students_onboard,
                'average_speed': float(trip.average_speed)
            }
        except Trip.DoesNotExist:
            return None
    
    @database_sync_to_async
    def save_location_update(self, location_data):
        # Save location update to database
        try:
            trip = Trip.objects.get(id=self.trip_id)
            
            # Create location update
            location_update = LocationUpdate.objects.create(
                trip=trip,
                latitude=location_data['latitude'],
                longitude=location_data['longitude'],
                speed=location_data.get('speed'),
                heading=location_data.get('heading'),
                accuracy=location_data.get('accuracy'),
                altitude=location_data.get('altitude'),
                device_id=location_data.get('device_id', '')
            )
            
            # Update trip's current location
            trip.current_latitude = location_data['latitude']
            trip.current_longitude = location_data['longitude']
            trip.last_location_update = location_update.created_at
            
            if location_data.get('speed'):
                trip.average_speed = location_data['speed']
                trip.max_speed = max(trip.max_speed or 0, location_data['speed'])
            
            trip.save()
            
            return location_update
            
        except Trip.DoesNotExist:
            return None

class SchoolTrackingConsumer(AsyncWebsocketConsumer):
    # WebSocket for school-wide bus tracking 
    async def connect(self):
        self.school_id = self.scope['user'].school_id
        self.school_group_name = f'school_{self.school_id}'
        
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.school_group_name,
                self.channel_name
            )
            await self.accept()
            
            # Send initial bus locations
            bus_locations = await self.get_active_bus_locations()
            await self.send(text_data=json.dumps({
                'type': 'initial_locations',
                'data': bus_locations
            }))
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.school_group_name,
            self.channel_name
        )
    
    async def bus_location_update(self, event):
        # Receive bus location update for school
        await self.send(text_data=json.dumps({
            'type': 'bus_location',
            'data': event['data']
        }))
    
    async def trip_status_change(self, event):
        # Receive trip status change
        await self.send(text_data=json.dumps({
            'type': 'trip_status',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_active_bus_locations(self):
        # Get locations of all active buses in school
        from .models import Trip, Bus
        
        active_trips = Trip.objects.filter(
            bus__school_id=self.school_id,
            status=Trip.TripStatus.IN_PROGRESS,
            last_location_update__isnull=False
        ).select_related('bus', 'route', 'driver__user')
        
        bus_locations = []
        for trip in active_trips:
            bus_locations.append({
                'trip_id': trip.id,
                'bus_number': trip.bus.bus_number,
                'route_name': trip.route.name,
                'latitude': float(trip.current_latitude),
                'longitude': float(trip.current_longitude),
                'speed': float(trip.average_speed),
                'students_onboard': trip.students_onboard,
                'last_update': trip.last_location_update.isoformat(),
                'driver_name': trip.driver.user.get_display_name()
            })
        
        return bus_locations