from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Tag, Word
from .serializers import TagSerializer, UserRegistrationSerializer, WordSerializer, WordBasicSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):

        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']

            res = Response()

            res.data = {'success': True}

            res.set_cookie(
                key="access_token", 
                value=access_token,
                httponly=True, 
                secure=True,
                samesite='None', 
                path='/'
            )

            res.set_cookie(
                key="refresh_token", 
                value=refresh_token,
                httponly=True, 
                secure=True,
                samesite='None', 
                path='/'
            )

            return res
        
        except: 
            return Response({'success': False})


class CustomRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)
            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data= {'refreshed': True}

            res.set_cookie(
                key="access_token", 
                value=access_token,
                httponly=True, 
                secure=True,
                samesite='None', 
                path='/'
            )

            return res
        
        except:
            return Response({'refreshed': False})


@api_view(['POST'])
def logout(request):
    try:
        res = Response()
        res.data = {'success': True}
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res
    except:
        return Response({'refreshed': False})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def is_authenticated(request):
    return Response({'authenticated': True})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def tags_list_create(request):
    if request.method == 'GET':
        user = request.user
        tags = Tag.objects.filter(user=user)
        serializer = TagSerializer(tags, many=True)

        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def tag_detail(request, pk):
    try:
        tag = Tag.objects.get(id=pk, user=request.user)
    except Tag.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def words_by_tag(request, pk):
    try:
        tag = Tag.objects.get(id=pk, user=request.user)
    except Tag.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    words = Word.objects.filter(tag=tag, user=request.user)
    serializer = WordBasicSerializer(words, many=True)
    return Response(serializer.data)



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def words_list_create(request):
    if request.method == 'GET':
        user = request.user
        words = Word.objects.filter(user=user)
        serializer = WordBasicSerializer(words, many=True)

        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = WordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def word_detail(request, pk):
    try:
        word = Word.objects.get(pk=pk, user=request.user)
    except Word.DoesNotExist:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WordSerializer(word)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        if 'note' not in request.data:
            return Response({'detail': 'Only "note" field can be updated.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WordSerializer(word, data={'note': request.data['note']}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        word.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)
