import pygame
import random
import sys
import os
from pygame import mixer

# Инициализция
pygame.init()
mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 7
ENEMY_SPEED = 2
BULLET_SPEED = 10
STAR_COUNT = 100

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(resource_path(os.path.join('assets', 'player.png'))).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 40))
        except:
            self.image = pygame.Surface((50, 40))
            self.image.fill(GREEN)

        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = PLAYER_SPEED
        self.health = 100
        self.max_health = 100
        self.shoot_delay = 250  # миллисекунды
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            shoot_sound.play()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load(resource_path(os.path.join('assets', 'enemy.png'))).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill(RED)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.randint(1, 3)
        self.health = 30

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load(resource_path(os.path.join('assets', 'bullet.png'))).convert_alpha()
            self.image = pygame.transform.scale(self.image, (10, 15))
        except:
            self.image = pygame.Surface((5, 15))
            self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.randint(1, 3)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)


class EnemyWave:
    def __init__(self):
        self.wave_number = 0
        self.enemies_in_wave = 5
        self.enemies_spawned = 0
        self.spawn_delay = 1000  # миллисекунды между спавнами
        self.last_spawn = 0
        self.wave_complete = False

    def start_new_wave(self):
        self.wave_number += 1
        # Постпенное увеличение количества врагов (максимум - 15)
        self.enemies_in_wave = min(5 + self.wave_number, 15)
        self.enemies_spawned = 0
        self.spawn_delay = max(300, 1000 - (self.wave_number * 50))  # В каждой волной враги появляются быстрее
        self.wave_complete = False

    def update(self):
        now = pygame.time.get_ticks()
        if (self.enemies_spawned < self.enemies_in_wave and
                now - self.last_spawn > self.spawn_delay):
            self.last_spawn = now
            self.spawn_enemy()
            self.enemies_spawned += 1
            if self.enemies_spawned >= self.enemies_in_wave:
                self.wave_complete = True

    def spawn_enemy(self):
        # Создание врагов с разными схемами появления
        if self.wave_number % 3 == 0:
            # V формация врагов
            cols = min(5, self.enemies_in_wave)
            spacing = WIDTH // (cols + 1)
            x = spacing * ((self.enemies_spawned % cols) + 1)
            y = -40 - (20 * (self.enemies_spawned // cols))
        else:
            # Случайное распределние врагов по ширине экрана
            x = random.randint(50, WIDTH - 50)
            y = -40

        enemy = Enemy(x, y)
        all_sprites.add(enemy)
        enemies.add(enemy)


def draw_health_bar(surface, x, y, health, max_health):
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (health / max_health) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


def show_start_screen():
    screen.fill(BLACK)
    if background:
        screen.blit(background, (0, 0))
    else:
        for star in stars:
            star.draw(screen)

    title = big_font.render("SPACE SHOOTER", True, WHITE)
    start = font.render("Press any key to begin", True, WHITE)
    controls = font.render("Arrow keys to move, SPACE to shoot", True, WHITE)

    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, HEIGHT // 2))
    screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT * 3 // 4))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                waiting = False


def show_game_over_screen():
    screen.fill(BLACK)
    if background:
        screen.blit(background, (0, 0))
    else:
        for star in stars:
            star.draw(screen)

    game_over = big_font.render("GAME OVER", True, RED)
    final_score = font.render(f"Final Score: {score}", True, WHITE)
    restart = font.render("Press R to restart or ESC to quit", True, WHITE)

    screen.blit(game_over, (WIDTH // 2 - game_over.get_width() // 2, HEIGHT // 3))
    screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
    screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT * 2 // 3))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    return True  # Restart
                elif event.key == pygame.K_ESCAPE:
                    return False  # Quit


if __name__ == "__main__":
    # Игровое окно
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter")
    clock = pygame.time.Clock()

    try:
        background = pygame.image.load(resource_path(os.path.join('assets', ''))).convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    except:
        background = None

    # Создание спрайт групп
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    # Создание персонажа
    player = Player()
    all_sprites.add(player)

    # Звезды к фону
    stars = [Star() for _ in range(STAR_COUNT)] if background is None else []

    # Создание контроллера волн врагов
    wave_controller = EnemyWave()
    wave_controller.start_new_wave()

    # Звуки
    try:
        shoot_sound = mixer.Sound(resource_path(os.path.join('assets', 'shoot.wav')))
        explosion_sound = mixer.Sound(resource_path(os.path.join('assets', 'explosion.wav')))
        mixer.music.load(os.path.join(resource_path('assets', 'background.mp3')))
        mixer.music.set_volume(0.5)
        mixer.music.play(loops=-1)
    except:
        print("Sound files not found - continuing without sound")
        shoot_sound = mixer.Sound(buffer=bytearray(44))
        explosion_sound = mixer.Sound(buffer=bytearray(44))

    # Игровые переменные (счет, пауза, состояние игры)
    score = 0
    game_over = False
    paused = False
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 72)

    # Игровой цикл
    running = True
    show_start_screen()

    while running:
        # Ограничение чистоты кадров
        clock.tick(FPS)

        # Обработка ввода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over and not paused:
                    player.shoot()
                elif event.key == pygame.K_p and not game_over:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if not game_over and not paused:
            # Обновления
            # Обновление логики волн врагов
            wave_controller.update()

            # Начало новой волны если одна закночилась
            if wave_controller.wave_complete and len(enemies) == 0:
                wave_controller.start_new_wave()

            # Обновление всех спрайтов
            all_sprites.update()

            # Обновление звезд на фоне
            if background is None:
                for star in stars:
                    star.update()

            # Проверка столкновении пуль с врагами
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for hit in hits:
                explosion_sound.play()
                score += 50 - hit.speed * 10  # Более быстрые враги дают меньше очков

            # Проверка столкновении
            hits = pygame.sprite.spritecollide(player, enemies, True)
            for hit in hits:
                explosion_sound.play()
                player.health -= 20
                if player.health <= 0:
                    game_over = True

        # Отрисовка кадра
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)
            for star in stars:
                star.draw(screen)

        # Отрисовка всех спрайтов
        all_sprites.draw(screen)

        # Отрисовка UI
        draw_health_bar(screen, 5, 5, player.health, player.max_health)
        score_text = font.render(f"Score: {score}", True, WHITE)
        wave_text = font.render(f"Wave: {wave_controller.wave_number}", True, WHITE)
        screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        screen.blit(wave_text, (WIDTH - wave_text.get_width() - 10, 50))

        if paused:
            pause_text = big_font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))

        if game_over:
            if show_game_over_screen():
                # Перезапуск / сброс
                game_over = False
                score = 0
                player.health = player.max_health

                # Очистка всех спрайтов
                for sprite in all_sprites:
                    sprite.kill()

                # Создание нового игрока
                player = Player()
                all_sprites.add(player)

                # Сброс системы волн врагов
                wave_controller = EnemyWave()
                wave_controller.start_new_wave()
            else:
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()