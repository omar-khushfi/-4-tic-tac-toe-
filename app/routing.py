from django.urls import path 
from . import consumers

websocket_urlpatterns = [
 path('ws/game/<str:room_name>/', consumers.GameConsumer.as_asgi()),
 ]
