from django.urls import path
from .views import RegisterView, LoginView, UserTopicsView
from rest_framework_simplejwt.views import TokenRefreshView
 
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('topics/', UserTopicsView.as_view(), name='user-topics'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 