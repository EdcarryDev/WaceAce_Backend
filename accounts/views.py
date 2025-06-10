from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import UserProfile
from quiz.models import Subject, Topic

# Create your views here.

class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        return Response({
            "user": user_serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "is_user_topics_selected": user.profile.is_user_topics_selected,
            "school_name": user.profile.school_name,
            "exam_year": user.profile.exam_year
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": user_serializer.data,
                "is_user_topics_selected": user.profile.is_user_topics_selected
            }, status=status.HTTP_200_OK)
        
        return Response({
            "error": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)

class UserTopicsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the user's profile
            profile = request.user.profile
            
            # Get the selected topics data
            selected_topics_data = request.data.get('selected_topics', {})
            
            # Store the data directly since it's already in the correct format
            profile.selected_topics = selected_topics_data
            profile.is_user_topics_selected = True
            profile.save()

            return Response({
                "message": "Topics updated successfully",
                "selected_topics": profile.selected_topics,
                "is_user_topics_selected": profile.is_user_topics_selected
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            # Get the user's profile
            profile = request.user.profile
            
            return Response({
                "selected_topics": profile.selected_topics,
                "is_user_topics_selected": profile.is_user_topics_selected
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
