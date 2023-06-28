from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import PlayerStatistics, GameSession, Player


class StatisticsSerializer(serializers.ModelSerializer):

    class Meta:
        model= PlayerStatistics
        fields = ['player', 'username', 'wins', 'losses', 'ties']


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model=Player
        fields = ['id', 'username', 'last_active']


class GameSessionSerializer(serializers.ModelSerializer):
    creator = PlayerSerializer()
    opponent = PlayerSerializer()

    class Meta:
        model= GameSession
        fields = ['id', 'creator', 'opponent', 'creator_choice', 'opponent_choice', 'result', 'created']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        #player, created = Player.objects.get_or_create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                data['user'] = user
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Username and password are required.')

        return data
