from django.urls import path

from .views import (
    CustomTokenObtainPairView,
    CustomRefreshTokenView,
    IsAuthenticatedView,
    LogoutView,
    RegisterUserView,
    TagListCreateView,
    TagDetailView,
    WordsByTagView,
    WordListCreateView,
    WordDetailView
)

urlpatterns = [
    # Authentication Endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomRefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'), 
    path('authenticated/', IsAuthenticatedView.as_view(), name='is_authenticated'),
    path('register_user/', RegisterUserView.as_view(), name='register_user'),

    # Tag endpoints
    path('tags/', TagListCreateView.as_view(), name='tags_list_create'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag_detail'),

    #  Word endpoints
    path('words/', WordListCreateView.as_view(), name='words_list_create'),
    path('words/<int:pk>/', WordDetailView.as_view(), name='word_detail'),
    path('tags/<int:pk>/words/', WordsByTagView.as_view(), name='words_by_tag'),
]