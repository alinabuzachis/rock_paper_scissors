from django.db import models
from django.db import transaction
from django.db.models import F
from django.contrib.auth.models import User


CHOICES = (
    ('1', 'paper'),
    ('2', 'rock'),
    ('3', 'scissors'),
)

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.username


class GameSession(models.Model):
    creator = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_sessions_as_creator')
    opponent = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='game_sessions_as_opponent', null=True, blank=True)
    creator_choice = models.CharField(max_length=20, null=True, blank=True, choices=CHOICES)
    opponent_choice = models.CharField(max_length=20, null=True, blank=True, choices=CHOICES)
    # rounds = models.PositiveIntegerField(choices=[(1, 'Single'), (3, '3 Rounds')])
    result = models.CharField(max_length=20, null=True, blank=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return f"Game Session: {self.id}"

    def play_game(self):
        # Check for a tie
        if self.creator_choice is not None and self.opponent_choice is not None:
            if self.creator_choice == self.opponent_choice:
                self.result = "tie"

            # Define the winning combinations
            winning_combinations = {
                'rock': 'scissors',
                'paper': 'rock',
                'scissors': 'paper'
            }

            # Check if player1 wins
            if self.creator_choice == winning_combinations[self.opponent_choice]:
                self.result = "win"
            else:
                self.result = "loss"

        else:
            self.result = "Choice saved! Waiting for the opponent to make their choice."

        # Update players statistics
        self.update_player_statistics()

        # Save the game session
        self.save()

    def update_player_statistics(self):
        creator_score = PlayerStatistics.objects.get_or_create(player=self.creator)[0]
        opponent_score = PlayerStatistics.objects.get_or_create(player=self.opponent)[0]

        if self.result == "win":
            creator_score.wins = F('wins') + 1
            opponent_score.losses = F('losses') + 1
        elif self.result == "loss":
            creator_score.losses = F('losses') + 1
            opponent_score.wins = F('wins') + 1
        elif self.result == "tie":
            creator_score.ties = F('ties') + 1
            opponent_score.ties = F('ties') + 1

        scores_to_update = [creator_score, opponent_score]

        with transaction.atomic():
            PlayerStatistics.objects.bulk_update(scores_to_update, ['wins', 'losses', 'ties'])


class PlayerStatistics(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, primary_key=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    ties = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Statistics for {self.player.username}"

    @property
    def username(self):
        return self.player.username
