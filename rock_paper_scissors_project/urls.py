"""
URL configuration for rock_paper_scissors_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rock_paper_scissors.views import UserRegistrationView, UserLoginView, UserScoresAPIView, GameSessionListAPIView, PlayGameWithBotView, PlayGameView, JoinGameSessionView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('stats/', UserScoresAPIView.as_view(), name='user-stats'),
    path('game-sessions/', GameSessionListAPIView.as_view(), name='game-sessions'),
    path('play-with-bot/', PlayGameWithBotView.as_view(), name='play'),
    path('play/', PlayGameView.as_view(), name='play-game'),
    path('play/<str:opponent>/', PlayGameView.as_view(), name='play-game-with-opponent'),
    path('game-session/join/<str:game_session_id>/', JoinGameSessionView.as_view(), name='join-game-session'),

]
