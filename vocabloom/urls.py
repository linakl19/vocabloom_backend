from django.urls import path

from .views import CustomTokenObtainPairView, CustomRefreshTokenView, logout, is_authenticated, register_user, tags_list_create, tag_detail, words_list_create, word_detail, words_by_tag

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', logout), 
    path('authenticated/', is_authenticated),
    path('register_user/', register_user),

    path('tags/', tags_list_create), 
    path('tags/<int:pk>/', tag_detail),
    path('tags/<int:pk>/words', words_by_tag),

    path('words/', words_list_create),
    path('words/<int:pk>/', word_detail),
]