from django.urls import path
from . import views
urlpatterns = [
    path('', views.AppView.as_view(), name='app'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/session/', views.SessionView.as_view(), name='session'),
    path('api/history/<slug:slug>/', views.RoomHistoryView.as_view(), name='history'),
]
