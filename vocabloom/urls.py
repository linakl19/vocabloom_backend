from django.urls import path

from .views import get_tags, CustomTokenObtainPairView, CustomRefreshTokenView, logout

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('tags/', get_tags), 
    path('logout/', logout)
]