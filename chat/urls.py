from django.urls import path
from . import views
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:room_name>/', consumers.ChatRoomConsumer.as_asgi()),
]

urlpatterns = [
    path('', views.room_enroll, name='room-enroll'),
    path('chat/<int:friend_id>/', views.room_choice, name='room-choice'),
    path('room/<int:room_name>-<int:friend_id>/', views.room, name='room'),

]
