from django.urls import path
from . import views
urlpatterns = [
    path('', views.ModelListView.as_view()),
    path('sync/', views.SyncModelsView.as_view()),
]
