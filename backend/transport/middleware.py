from django.utils import timezone
from .models import GPSDevice

class GPSDeviceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Update GPS device status for relevant requests
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'driver_profile'):
                # This is a driver - update their device status
                device_id = getattr(request.user.driver_profile, 'device_id', None)
                if device_id:
                    try:
                        device = GPSDevice.objects.get(device_id=device_id)
                        device.last_communication = timezone.now()
                        device.save()
                    except GPSDevice.DoesNotExist:
                        pass
        return None