from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('predict/', views.predict, name = 'predict'),
    path('metrics/', views.evaluate_metrics, name = 'metrics'),
]