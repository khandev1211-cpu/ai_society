from django.urls import path
from . import views
urlpatterns = [
    path('shared/', views.SharedMemoryView.as_view()),
    path('private/<str:model_id>/', views.PrivateMemoryView.as_view()),
]
