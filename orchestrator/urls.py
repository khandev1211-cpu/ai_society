from django.urls import path
from . import views
urlpatterns = [
    path('dm/', views.DirectMessageView.as_view()),
]
