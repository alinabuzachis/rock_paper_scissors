from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status, generics

from .models import Player
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    StatisticsSerializer,
    GameSessionSerializer
)
from .models import GameSession, PlayerStatistics

import random


class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        user = serializer.save()

        # Create a Player instance for the registered user
        Player.objects.create(user=user)
        #player.save()
        return Response(status=status.HTTP_200_OK)


class UserLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
        }, status=status.HTTP_200_OK)


class UserScoresAPIView(APIView):
    def get(self, request):
        # Get the scores of all users and order them by wins
        queryset = PlayerStatistics.objects.all().order_by('-wins')
        serializer = StatisticsSerializer(queryset, many=True)
        return Response(serializer.data)


class GameSessionListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GameSessionSerializer

    def get(self, request):
        # Get the authenticated user
        player = request.user.player

        # Get all game sessions where the user is either player 1 or player 2
        queryset = GameSession.objects.filter(Q(creator=player) | Q(opponent=player))
        serializer = GameSessionSerializer(queryset, many=True)
        return Response(serializer.data)


class PlayGameWithBotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        choices = ['rock', 'paper', 'scissors']
        user_choice = request.data.get('choice')

        if not user_choice:
            return Response({'error': 'Please provide a choice parameter.'}, status=status.HTTP_404_NOT_FOUND)

        if user_choice not in choices:
            return Response({'error': 'Invalid choice. Choose between rock, paper, or scissors.'}, status=status.HTTP_404_NOT_FOUND)

        bot_choice = random.choice(choices)

        if user_choice == bot_choice:
            result = 'It\'s a tie!'
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
                (user_choice == 'paper' and bot_choice == 'rock') or \
                (user_choice == 'scissors' and bot_choice == 'paper'):
            result = 'You win!'
        else:
            result = 'Bot wins!'
        return Response({'user_choice': user_choice, 'bot_choice': bot_choice, 'result': result})


class PlayGameView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def create_game_session(creator, opponent, creator_choice):
        game_session = GameSession.objects.create(creator=creator, opponent=opponent)
        game_session.creator_choice = creator_choice
        game_session.save()
        return game_session

    def post(self, request, opponent=None):
        message = ''
        player_choice = request.data.get('choice')

        if opponent:
            opponent_id = get_object_or_404(User, username=opponent)
            opponent_player = get_object_or_404(Player, user=opponent_id)
            # Create game session with specific opponent
            game_session = self.create_game_session(request.user.player, opponent_player, player_choice)

            game_session.play_game()

            # Save the game session
            game_session.save()

            # Return the response
            message = "Waiting for the opponent to make their choice."

        else:
            # Find an existing game session where the player2 is not set
            game_session = GameSession.objects.filter(opponent=None).exclude(creator=request.user.player).first()

            if game_session:
                # Assign the current user as opponent
                game_session.opponent = request.user.player
                game_session.opponent_choice = player_choice
                game_session.play_game()
                # Save the game session
                game_session.save()
            else:
                # Create a new game session with the current user as creator
                game_session = GameSession.objects.create(creator=request.user.player, creator_choice=player_choice)

                game_session.play_game()
                 # Save  game session
                game_session.save()
                message = 'No other players available to play with. Create a new session and wait until someone will join.'

        # Serialize the game session
        serializer = GameSessionSerializer(game_session)
        response = {
           "message": message,
           "code": 200,
           "results": serializer.data
        }

        return Response(response, status=status.HTTP_200_OK)


class JoinGameSessionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, game_session_id):
        message = ''
        response = {
           "message": message,
           "code": 200,
           "results": {}
        }
        # Get the authenticated user
        user = request.user.player

        # Get user's choice
        user_choice = request.data.get('choice')

        # Retrieve the game session by its identifier
        game_session = get_object_or_404(GameSession, id=game_session_id)
        serializer= GameSessionSerializer(game_session)
        response['results'] = serializer.data
        # Check if the game session already has a second player
        if game_session.opponent is not None and game_session.opponent != user:
            response['message'] = 'Game session is already full.'
            response['status'] = 400
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if game_session.opponent_choice is not None:
            response['message'] = 'Game session already concluded.'
            response['status'] = 400
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # Assign the current user as player2
        game_session.opponent = user
        game_session.opponent_choice = user_choice
        game_session.play_game()
        game_session.save()
        serializer = GameSessionSerializer(game_session)
        response['results'] = serializer.data
        response['message'] = 'Successfully joined the game session.'

        return Response(response, status=status.HTTP_200_OK)