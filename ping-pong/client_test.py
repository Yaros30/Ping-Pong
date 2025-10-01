from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
bg = transform.scale(image.load("ping-pong/pingpongfon.png"), (WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---
def connect_to_server():
     while True:
         try:
             client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
             client.connect(('localhost', 2020)) # ---- Підключення до сервера
             buffer = ""
             game_state = {}
             my_id = int(client.recv(24).decode())
             return my_id, game_state, buffer, client
         except:
             pass
def receive():
     global buffer, game_state, game_over
     while not game_over:
         try:
             data = client.recv(1024).decode()
             buffer += data
             while "\n" in buffer:
                 packet, buffer = buffer.split("\n", 1)
                 if packet.strip():
                     game_state = json.loads(packet)
         except:
             game_state["winner"] = -1
             break

# --- ШРИФТИ ---
font_win = font.Font("ping-pong/Pusia-Bold.otf", 72)
font_main = font.Font("ping-pong/Pusia-Bold.otf", 36)
# --- ЗОБРАЖЕННЯ ----
platform = transform.scale(image.load("ping-pong/platform2.png"), (40, 200))

platform2 = transform.flip(platform, True, False)
rotate_platform = transform.rotate(platform, 90)
ball = transform.scale(image.load("ping-pong/TNT_ball.png"), (20, 20))
# --- ЗВУКИ ---
mixer.init()
hit_sound = mixer.Sound("ping-pong/the-sound-of-hitting-the-ball.mp3")
mixer.init()
whistle_sound = mixer.Sound("ping-pong/whistle-of-a-different-type-at-a-distance.mp3")
# --- ГРА ---
game_state = {
    "paddles": {"0": HEIGHT // 2 - 50, "1": HEIGHT // 2 - 50},
    "ball": {"x": WIDTH // 2, "y": HEIGHT // 2},
    "scores": [0, 0],
    "sound_event": None,
    "winner": None
}
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((27, 3, 163))
        
        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == 0:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "Ти переміг!"
        else:
            text = "Пощастить наступним разом!"

        win_text = font_win.render(text, True, (0, 255, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('К - рестарт', True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)
        keys = key.get_pressed()
        if keys[K_k] and ("winner" in game_state and game_state["winner"] is not None):
            client.send(b"RESTART")

        display.update()
        continue  # Блокує гру після перемоги

    if game_state:
        screen.blit(bg, (0, 0))
        screen.blit(platform, (20, game_state['paddles']['0']))
        screen.blit(platform2, (WIDTH - 40, game_state['paddles']['1']))
        # draw.rect(screen, (255, 7, 58), (20, game_state['paddles']['0'], 350, 40))
        # draw.rect(screen, (255, 7, 58), (WIDTH - 40, game_state['paddles']['1'], 350, 40))
        # draw.circle(screen, (192, 91, 44), (game_state['ball']['x'], game_state['ball']['y']), 10)
        screen.blit(ball, (game_state['ball']['x'], game_state['ball']['y']))
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (192, 91, 44))
        screen.blit(score_text, (WIDTH // 2 -25, 20))

        if game_state['sound_event']:
            if game_state['sound_event'] == 'wall_hit':
                # звук відбиття м'ячика від стін
                hit_sound.play()
            if game_state['sound_event'] == 'platform_hit':
                # звук відбиття м'ячика від платформи
                hit_sound.play()
            if game_state['sound_event'] == 'goal':
                # звук відбиття м'ячика від платформи
                whistle_sound.play()

    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        screen.blit(wating_text, (WIDTH // 2 - 25, 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        # game_state['paddles']['0'] -= 1
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")


