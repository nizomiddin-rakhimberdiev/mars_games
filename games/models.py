from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    game_file = models.FileField(upload_to='games/')  # Pygame o'yin fayllari yoki URL bo'lishi mumkin
    game_image = models.ImageField(upload_to='images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
