from django.contrib import admin
from .models import GameSession, Player, PlayerStatistics

admin.site.register(GameSession)
admin.site.register(Player)
admin.site.register(PlayerStatistics)
