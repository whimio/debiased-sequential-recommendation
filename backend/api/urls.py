from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import PredictView, EvaluateView

urlpatterns = [
    path("recommend/", PredictView.as_view(), name="api-recommend"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("evaluate/", EvaluateView.as_view(), name="api-evaluate"),
]