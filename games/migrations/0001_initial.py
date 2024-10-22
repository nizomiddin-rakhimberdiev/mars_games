# Generated by Django 5.1.2 on 2024-10-19 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='images/')),
                ('game_file', models.FileField(upload_to='games/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
