from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/transport/trip/(?P<trip_id>\w+)/$', consumers.BusTrackingConsumer.as_asgi()),
    re_path(r'ws/transport/school/$', consumers.SchoolTrackingConsumer.as_asgi()),
]