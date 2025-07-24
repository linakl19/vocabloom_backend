from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Tag
from .serializers import TagSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tags(request):
    user = request.user
    tags = Tag.objects.filter(user=user)
    serializer = TagSerializer(tags, many=True)

    return Response(serializer.data)