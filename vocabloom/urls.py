from django.urls import path

from .views import CustomTokenObtainPairView, CustomRefreshTokenView, logout, is_authenticated, register_user, tags_list_create, tag_detail

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', logout), 
    path('authenticated/', is_authenticated),
    path('register_user/', register_user),

    path('tags/', tags_list_create), 
    path('tags/<int:pk>/', tag_detail), 
]