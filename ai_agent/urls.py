from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_interface, name='agent_interface'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/voice/', views.voice_api, name='voice_api'),
]