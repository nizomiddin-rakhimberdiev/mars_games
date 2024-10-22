from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# O‘yin muhiti
ground = Entity(model='plane', texture='grass', scale=100, collider='box')
sky = Sky()

# O‘yinchi va kursor
player = FirstPersonController()
player.cursor = Entity(model='quad', color=color.black, scale=0.02)

# O‘yin parametrlari
ammo = 30  # O‘q miqdori
max_ammo = 30
reloading = False
round_number = 1
health = 3  # O‘yinchi joni

# Matnli interfeys elementlari
ammo_text = Text(text=f"Ammo: {ammo}/{max_ammo}", position=(-0.85, 0.45), scale=2)
round_text = Text(text=f"Round: {round_number}", position=(-0.85, 0.4), scale=2)
health_text = Text(text=f"Health: {health}", position=(-0.85, 0.35), scale=2)

# Ovozlar
shoot_sound = Audio('shoot.wav', autoplay=False)
reload_sound = Audio('reload.wav', autoplay=False)

# Nishonlar ro‘yxati
targets = []

def create_target(position):
    """Nishon yaratish, rasmdan foydalanish."""
    target = Entity(
        model='quad',  # Nishon sifatida kvadrat (rasm uchun)
        texture='../images/target.png',  # Tasvirni yuklang
        scale=(5, 5, 3),  # Katta o'lcham
        position=position,
        collider='box',
        double_sided=True  # Orqa tomoni ko'rinadigan qilib belgilash
    )
    return target

def spawn_targets(num_targets):
    """Nishonlarni yaratish."""
    global targets
    targets = [create_target((random.randint(-10, 10), 1, random.randint(5, 20))) for _ in range(num_targets)]

# Birinchi raund uchun nishonlar
spawn_targets(3)

def move_targets():
    """Nishonlarni o‘yinchiga qarab harakatlantirish."""
    for target in targets:
        direction = (player.position - target.position).normalized()
        target.position += direction * time.dt * 4  # Tez harakat

        # Agar nishon o‘yinchiga juda yaqinlashsa
        if distance(target.position, player.position) < 1:  # Masofa orqali tekshirish
            destroy(target)
            targets.remove(target)
            take_damage()  # O‘yinchidan jon ayirish

def show_bullet_trace(start, end):
    """O‘qning uchishini ko‘rsatish."""
    bullet = Entity(model='cube', color=color.yellow, scale=(0.1, 0.1, 0.1), position=start)
    bullet.animate_position(end, duration=0.3)  # O‘qning uchish tezligi
    destroy(bullet, delay=0.3)

def shoot():
    """O‘q otish."""
    global ammo
    if ammo > 0 and not reloading:
        ammo -= 1
        ammo_text.text = f"Ammo: {ammo}/{max_ammo}"
        shoot_sound.play()

        hit_info = raycast(player.position, player.forward, distance=50, ignore=[player])
        if hit_info.hit:
            show_bullet_trace(player.position, hit_info.point)

            if hit_info.entity in targets:
                destroy(hit_info.entity)
                targets.remove(hit_info.entity)

                if not targets:
                    next_round()

def reload():
    """Qayta o‘qlash."""
    global reloading
    if ammo < max_ammo and not reloading:
        reloading = True
        reload_sound.play()
        invoke(reload_ammo, delay=2)

def reload_ammo():
    """O‘qlarni to‘ldirish."""
    global ammo, reloading
    ammo = max_ammo
    ammo_text.text = f"Ammo: {ammo}/{max_ammo}"
    reloading = False

def take_damage():
    """Jonni kamaytirish."""
    global health
    health -= 1
    health_text.text = f"Health: {health}"

    if health <= 0:
        lose_game()  # Agar jon 0 ga teng bo'lsa, o'yin tugaydi

def next_round():
    """Keyingi raundga o'tish."""
    global round_number
    round_number += 1
    round_text.text = f"Round: {round_number}"

    if round_number > 15:
        end_game()
    else:
        spawn_targets(round_number + 2)  # Har bir raundda nishonlar soni oshadi

def end_game():
    """O‘yin tugadi - yutdingiz."""
    message = Text(text="Siz yutdingiz!", position=(0, 0), scale=4, color=color.green)
    destroy(message, delay=2)
    invoke(application.quit, delay=3)

def lose_game():
    """O‘yin tugadi - yutqazdingiz."""
    message = Text(text="Siz yutqazdingiz!", position=(0, 0), scale=4, color=color.red)
    destroy(message, delay=2)
    invoke(application.quit, delay=3)

def input(key):
    """Kirish boshqaruvi."""
    if key == 'left mouse down':
        shoot()
    elif key == 'r':
        reload()

def update():
    """Har freymda chaqiriladi."""
    move_targets()

# O'yin boshlanishi
app.run()