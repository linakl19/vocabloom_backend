from django.contrib.auth.models import User
from rest_framework import views, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from ..serializers import (
    UserRegistrationSerializer,
    SimpleSuccessSerializer,
    SimpleRefreshedSerializer,
    SimpleAuthenticatedSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @extend_schema(responses=SimpleSuccessSerializer, tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        # Call parent method to get tokens
        response = super().post(request, *args, **kwargs)

        # If authentication failed, return the error response as-is
        if response.status_code != 200:
            return response

        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")

        # Return tokens in response body
        return Response(
            {"access": access_token, "refresh": refresh_token, "success": True}
        )


class CustomRefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

    @extend_schema(responses=SimpleRefreshedSerializer, tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        # Standard token refresh - expects refresh token in request body
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            return Response(
                {
                    "access": response.data.get("access"),
                    "refresh": response.data.get(
                        "refresh", request.data.get("refresh")
                    ),
                    "refreshed": True,
                }
            )

        return Response({"refreshed": False}, status=response.status_code)


@extend_schema(responses=SimpleSuccessSerializer, tags=["Authentication"])
class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleSuccessSerializer

    def post(self, request):
        # With token-only auth, logout is handled on frontend
        # Backend just confirms the request was authenticated
        return Response({"success": True})


@extend_schema(responses=SimpleAuthenticatedSerializer, tags=["Authentication"])
class IsAuthenticatedView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleAuthenticatedSerializer

    def get(self, request):
        return Response({"authenticated": True})

    def post(self, request):
        return Response({"authenticated": True})


@extend_schema(
    request=UserRegistrationSerializer,
    responses=UserRegistrationSerializer,
    tags=["Authentication"],
)
class RegisterUserView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)