import subprocess

from django.shortcuts import render, get_object_or_404
from .models import Game

def game_list(request):
    games = Game.objects.all()
    return render(request, 'game_list.html', {'games': games})


def game_detail(request, game_id):
    game = Game.objects.get(id=game_id)
    return render(request, 'game_detail.html', {'game': game})


def start_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    game_path = game.game_file.path  # Fayl yo'lini olish

    # Subprocess orqali o'yinni ishga tushirish
    subprocess.Popen(['python', game_path])  # Pygame o'yini "python" bilan ishlaydi

    return render(request, 'game_started.html', {'game': game})