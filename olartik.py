import pygame
pygame.init()
import random

# Müzikleri yükleme
pygame.mixer.init()
main_music = "assets/anamuzik.mp3"
death_music = "assets/death.mp3"
click_music = "assets/clickmusic.mp3"

# Ana müziği başlatma
pygame.mixer.music.load(main_music)
pygame.mixer.music.play(-1)  # (-1 sonsuz, 0 tek sefer)

# Ses efektlerini yükleme
death_sound = pygame.mixer.Sound(death_music)
click_sound = pygame.mixer.Sound(click_music)
click_sound.set_volume(0.3)  # Tıklama sesi yüksekliğini azalt

# Ekran boyutları
screen_width = 800
screen_height = 600

# Font tanımlaması
font = pygame.font.SysFont('Verneer', 50)
white = (240, 130, 60)
text_col = white

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battı Balık')

# Görseli yükle ve boyutlandır
uw = pygame.image.load("assets/uw.png").convert()
uw = pygame.transform.scale(uw, (screen_width, screen_height))
button_img = pygame.image.load("assets/yeni-Photoroom.png")
start_screen_img = pygame.image.load("assets/yeter.png")
start_screen_img = pygame.transform.scale(start_screen_img, (screen_width, screen_height))

def draw_text(text, font, white, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    global scroll_speed, game_over, flying, pass_pipe
    pipe_group.empty()
    batti.rect.x = 100
    batti.rect.y = int(screen_height / 2)
    batti.vel = 0  # Kuşun hızını sıfırla
    batti.image = pygame.transform.rotate(batti.images[batti.index], 0)  # Rotasyonu sıfırla
    scroll_speed = 2  # Kaydırma hızını sıfırla
    game_over = False
    flying = False
    pass_pipe = False
    score = 0
    return score

# Global değişkenler
pipe_frequency = random.randint(2000, 7000)  # Başlangıç boru sıklığı
pipe_gap = random.randint(100, 180)         # Başlangıç boru genişliği

# Arka planın x koordinatları
bg_x1 = 0
bg_x2 = screen_width

# Kaydırma hızı
scroll_speed = 2
flying = False
game_over = False
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
best_score = 0  # En yüksek skoru burada başlatıyoruz

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.image = pygame.transform.scale(self.image, (300, 300))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/boz.png')
        self.image = pygame.transform.scale(self.image, (90, 400))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 3):  # kaplus1, kaplus2
            img = pygame.image.load(f'assets/emir.png').convert_alpha()
            img = pygame.transform.scale(img, (45, 45))  # Görüntü boyutlandırma
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        self.mask = pygame.mask.from_surface(self.image)  # çarpışma maskesi

    def update(self):
        global flying, game_over, last_pipe, pipe_frequency, pipe_gap  # Global değişkenlere eriş

        if flying and not game_over:
            # Gravity
            self.vel += 0.6
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < screen_height:
                self.rect.y += int(self.vel)

            # Jump
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -8
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Animasyonun hızını kontrol et
            self.counter += 1
            flap_cooldown = 25
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0

            self.image = self.images[self.index]
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -1)

            # Rastgele boru oluşturma
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_frequency = random.randint(2000, 7000)  # Yeni boru sıklığı
                pipe_gap = random.randint(100, 180)         # Yeni boru genişliği
                pipe_height = random.randint(-100, 100)
                random_pipe_y = screen_height / 2 + random.randint(-100, 100)
                btm_pipe = Pipe(screen_width, random_pipe_y, -1)
                top_pipe = Pipe(screen_width, random_pipe_y, 1)
                pipe_group.add(btm_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

# Bird grubunu oluştur
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
batti = Bird(100, int(screen_height / 2))
bird_group.add(batti)

button = Button(screen_width // 2 - 170, screen_height // 2 - 170, button_img)

# Ana döngü
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    # Arka planı hareket ettir
    if not game_over:
        bg_x1 -= scroll_speed
        bg_x2 -= scroll_speed

    # Eğer bir arka plan tamamen ekrandan çıkarsa, yeniden yerine koy
    if bg_x1 <= -screen_width:
        bg_x1 = screen_width
    if bg_x2 <= -screen_width:
        bg_x2 = screen_width

    # Arka planları ekrana çiz
    screen.blit(uw, (bg_x1, 0))
    screen.blit(uw, (bg_x2, 0))

    # güncelle ve ekrana çiz
    bird_group.update()
    bird_group.draw(screen)

    if not game_over:
        pipe_group.update()
        pipe_group.draw(screen)

    # score kontrolü ve hızlandırma
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
            and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    # Hızı 5 skorda bir arttır
    if score % 5 == 0 and score > 0:
        scroll_speed = 2 + (score // 5)  # Hızı arttır

    # En yüksek skoru güncelle
    if score > best_score:
        best_score = score

    # Skoru ekrana yazdır
    draw_text(f"Score: {score}", font, white, int(610), 30)
    draw_text(f"Best Score: {best_score}", font, white, int(5), 30)

    if pygame.sprite.spritecollide(batti, pipe_group, False, pygame.sprite.collide_mask):
        game_over = True

    # Eğer kuş yere çarptıysa
    if batti.rect.bottom >= screen_height:
        game_over = True
        flying = False
        scroll_speed = 0

    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()
    # Ekranı güncelle
    pygame.display.update()

    # FPS kontrolü
    pygame.time.Clock().tick(60)

# Ana döngü
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Mouse'a her tıklandığında click müziği çal
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_sound.play()

        # Eğer start_screen ise ve ekrana tıklandıysa müzik değiştir
        if start_screen and event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mixer.music.stop()  # Ana müziği durdur
            start_screen = False

    # Eğer oyun biterse ölüm müziğini çal
    if reset_game() == 'game over':
        death_sound.play()

    # Burada yazı yazdırma işlemi
    draw_text("Battı Balık", font, text_col, int(screen_width / 3), 100)
    pygame.display.update()
