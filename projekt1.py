import pygame
import sys
import datetime
import random
import os

# Inicjalizacja Pygame
pygame.init()

# Stałe
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
GRAVITY = 0.5
JUMP_POWER = -12
PLAYER_SPEED = 5
COIN_COLOR = (255, 215, 0)  # fallback
FONT_COLOR = (255, 255, 255)
BG_COLOR_REAL = (50, 50, 50)
BG_COLOR_PROTECTED = (70, 70, 120)
MESSAGE_DURATION = 120
MAX_HP = 100
DAMAGE = 50  # Zmienione z 10 na 50

# Docelowy rozmiar gracza
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 80

# Rozmiar drona
DRONE_SIZE = 40

# Rozmiar monety (po przeskalowaniu)
COIN_SIZE = 25

# Rozmiar rejestru
REGISTER_SIZE = 35

# Ścieżki do grafik skórek (w folderze zdjecia)
SKIN_FILES = {
    'Wojska Lądowe': ('zdjecia/zmechol.png', 120, 285),
    'Żandarmeria': ('zdjecia/rzeton.png', 130, 274),
    'WOC': ('zdjecia/encepence.png', 182, 278),
    'GROM': ('zdjecia/grom.png', 816, 1291)
}

# Ceny skórek
SKIN_PRICES = {
    'Wojska Lądowe': 0,
    'Żandarmeria': 50,
    'WOC': 100,
    'GROM': 200
}

# Kolory przycisków
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER = (120, 120, 120)
BUTTON_DISABLED = (40, 40, 40)

# Definicje poziomów - poprawione dla poziomu 1
LEVELS = [
    {  # Poziom 1 – łatwy (poprawione pozycje monet i rejestrów)
        'platforms': [
            (0, 720, 1024, 20),   # podłoga
            (230, 630, 150, 20),
            (500, 530, 150, 20),
            (330, 400, 150, 20),
            (600, 330, 150, 20),
            (400, 200, 150, 20)
        ],
        'coins': [
            (250, 610),  # na platformie 230,630
            (520, 510),  # na platformie 500,530
            (350, 380),  # na platformie 330,400
            (620, 310),  # na platformie 600,330
            (420, 180),  # na platformie 400,200
        ],
        'registers': [
            ('AX', 240, 610),  # blisko lewej krawędzi platformy 230,630
            ('BX', 510, 510),  # platforma 500,530
            ('CX', 340, 380),  # platforma 330,400
        ],
        'interrupts': [
            (150, 500), (400, 400), (650, 300)
        ]
    },
    {  # Poziom 2 – średni (poprawione odstępy)
        'platforms': [
            (0, 720, 1024, 20),      # podłoga
            (150, 650, 120, 20),     # pierwsza platforma nad podłogą
            (400, 580, 120, 20),     # druga
            (650, 510, 120, 20),     # trzecia
            (250, 450, 120, 20),     # czwarta
            (500, 370, 120, 20),     # piąta
            (700, 300, 120, 20),     # szósta
            (350, 240, 120, 20),     # siódma
            (550, 160, 120, 20)      # ósma (wysoko)
        ],
        'coins': [
            (170, 630),  # na platformie 150,650
            (420, 560),  # na platformie 400,580
            (670, 490),  # na platformie 650,510
            (270, 420),  # na platformie 250,440
            (520, 350),  # na platformie 500,370
            (720, 280),  # na platformie 700,300
            (370, 210),  # na platformie 350,230
            (570, 140)   # na platformie 550,160
        ],
        'registers': [
            ('AX', 160, 630),
            ('BX', 410, 560),
            ('CX', 660, 490),
            ('DX', 260, 420)
        ],
        'interrupts': [
            (100, 550), (300, 500), (500, 450), (700, 400)
        ]
    },
    {  # Poziom 3 – trudny (bez zmian)
        'platforms': [
            (0, 740, 1024, 20),
            (100, 650, 100, 20),
            (300, 600, 100, 20),
            (500, 550, 100, 20),
            (700, 500, 100, 20),
            (200, 470, 100, 20),
            (400, 400, 100, 20),
            (600, 350, 100, 20),
            (300, 270, 100, 20),
            (500, 250, 100, 20)
        ],
        'coins': [
            (130, 600), (330, 550), (530, 500), (730, 450), (230, 400), (430, 350), (630, 300), (330, 250)
        ],
        'registers': [
            ('AX', 120, 630), ('BX', 320, 580), ('CX', 520, 530), ('DX', 720, 480)
        ],
        'interrupts': [
            (100, 550), (250, 500), (400, 450), (550, 400), (700, 350), (300, 300)
        ]
    }
]

# Ciekawostki
FACTS = [
    "Podział jednostki centralnej na kilka jednostek funkcjonalnych pozwala na wykonywanie kilku operacji jednocześnie.",
    "W procesorze 8086 adresowanie indeksowe wykorzystuje rejestry SI i DI.",
    "Mechanizm auto modyfikacji rejestrów indeksowych automatycznie inkrementuje rejestry.",
    "Flaga I w x86 zezwala na przyjmowanie przerwań maskowalnych.",
    "Flaga D określa kierunek modyfikacji rejestrów indeksowych.",
    "Tryb rzeczywisty adresuje tylko 1 MB pamięci.",
    "Tryb chroniony umożliwia sprzętową ochronę pamięci.",
    "MMX to zestaw instrukcji SIMD.",
    "Układ 8255 to programowalny interfejs równoległy.",
    "Sterownik DMA przejmuje kontrolę nad magistralą.",
    "Przerwanie NMI jest niemaskowalne.",
    "Wektor przerwań to adres procedury obsługi.",
    "Segmentacja pozwala na ochronę obszarów pamięci.",
    "Stronicowanie dzieli pamięć na strony 4KB.",
    "Klawiatura PC przesyła kody MAKE i BREAK.",
    "Magistrala PCI obsługuje Plug & Play.",
    "Procesory ARM mają architekturę harwardzką.",
    "Bankowanie rejestrów w ARM przyspiesza zmianę kontekstu.",
    "Układ Watch Dog resetuje procesor przy zawieszeniu."
]

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def load_skins():
    skins = {}
    for name, (filename, orig_w, orig_h) in SKIN_FILES.items():
        try:
            img = pygame.image.load(filename)
            img = pygame.transform.scale(img, (PLAYER_WIDTH, PLAYER_HEIGHT))
            skins[name] = img
        except pygame.error:
            print(f"Nie można wczytać pliku {filename}. Używam zastępczego koloru.")
            surf = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            surf.fill((random.randint(100,255), random.randint(100,255), random.randint(100,255)))
            skins[name] = surf
    return skins

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER,
                 text_color=(255,255,255), action=None, thumbnail=None, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.action = action
        self.font = pygame.font.Font(None, 24)
        self.hovered = False
        self.thumbnail = thumbnail
        self.enabled = enabled

    def draw(self, screen):
        if not self.enabled:
            color = BUTTON_DISABLED
        else:
            color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        if self.thumbnail and self.enabled:
            thumb_rect = self.thumbnail.get_rect()
            thumb_rect.centery = self.rect.centery
            thumb_rect.left = self.rect.left + 5
            screen.blit(self.thumbnail, thumb_rect)
            text_x = thumb_rect.right + 10
        else:
            text_x = self.rect.centerx

        text_surf = self.font.render(self.text, True, self.text_color)
        if text_surf.get_width() > self.rect.width - 20:
            short_text = self.text[:15] + "..."
            text_surf = self.font.render(short_text, True, self.text_color)

        text_rect = text_surf.get_rect()
        if self.thumbnail and self.enabled:
            text_rect.midleft = (text_x, self.rect.centery)
        else:
            text_rect.center = self.rect.center
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if not self.enabled:
            return
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                self.action()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, skin_image):
        super().__init__()
        self.image = skin_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms):
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = PLAYER_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_POWER
            self.on_ground = False

        self.vel_y += GRAVITY
        dy += self.vel_y

        self.rect.x += dx
        self.check_collision(dx, 0, platforms)

        self.rect.y += dy
        self.on_ground = False
        self.check_collision(0, dy, platforms)

    def check_collision(self, dx, dy, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if dx > 0:
                    self.rect.right = platform.rect.left
                if dx < 0:
                    self.rect.left = platform.rect.right
                if dy > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, img=None):
        super().__init__()
        if img:
            # Skaluj obraz do wymiarów platformy
            self.image = pygame.transform.scale(img, (width, height))
        else:
            self.image = pygame.Surface((width, height))
            self.image.fill((100, 100, 100))  # szary
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, image=None):
        super().__init__()
        if image:
            self.image = image.copy()
        else:
            self.image = pygame.Surface((COIN_SIZE, COIN_SIZE))
            self.image.fill(COIN_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Register(pygame.sprite.Sprite):
    def __init__(self, x, y, name, image=None):
        super().__init__()
        self.name = name
        if image:
            self.image = image.copy()
        else:
            self.image = pygame.Surface((REGISTER_SIZE, REGISTER_SIZE))
            self.image.fill((0, 200, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Interrupt(pygame.sprite.Sprite):
    def __init__(self, x, y, drone_image):
        super().__init__()
        self.image = drone_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dx = random.choice([-2, 2])
        self.dy = random.choice([-2, 2])

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.dx *= -1
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.dy *= -1

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("CPU Quest")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"  # MENU, LEVEL_SELECT, CHAR_SELECT, GAME, SHOP, RULES

        # Wczytaj wszystkie grafiki
        self.load_graphics()

        # Skórki
        self.skins = load_skins()
        self.current_skin = 'Wojska Lądowe'

        # Stan gry
        self.coins = 0
        self.hp = MAX_HP
        self.unlocked_levels = [True] + [False] * (len(LEVELS)-1)
        self.unlocked_skins = {'Wojska Lądowe': True}
        for skin in SKIN_PRICES:
            if skin != 'Wojska Lądowe':
                self.unlocked_skins[skin] = False

        # Grupy sprite'ów
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins_group = pygame.sprite.Group()
        self.registers = pygame.sprite.Group()
        self.interrupts = pygame.sprite.Group()
        self.player = None
        self.current_level = 0

        # Komunikaty
        self.messages = []

        # Czcionki
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.message_font = pygame.font.Font(None, 20)

        # Przyciski
        self.menu_buttons = self.create_menu_buttons()
        self.level_buttons = []
        self.char_select_buttons = []
        self.shop_buttons = []
        self.rules_button = Button(400, 650, 200, 50, "Powrót", action=self.back_to_menu)

        # Pasek ciekawostek
        self.fact_index = random.randint(0, len(FACTS)-1)
        self.fact_timer = 0

    def load_graphics(self):
        # Logo
        try:
            self.logo = pygame.image.load('zdjecia/logo.png')
            self.logo = pygame.transform.scale(self.logo, (520, 100))
        except:
            self.logo = None

        # Tło sklepu
        try:
            self.shop_bg = pygame.image.load('zdjecia/tlo_postacie.png')
            self.shop_bg = pygame.transform.scale(self.shop_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.shop_bg = None

        # Tło wyboru poziomów
        try:
            self.level_select_bg = pygame.image.load('zdjecia/poziomy_wybor_tlo.png')
            self.level_select_bg = pygame.transform.scale(self.level_select_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.level_select_bg = None

        # Tła poziomów
        self.level_bgs = []
        for i in range(1, 4):
            try:
                bg = pygame.image.load(f'zdjecia/tlo_poziom{i}.png')
                bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.level_bgs.append(bg)
            except:
                self.level_bgs.append(None)

        # Dron
        try:
            drone_raw = pygame.image.load('zdjecia/dron.png')
            self.drone_img = pygame.transform.scale(drone_raw, (DRONE_SIZE, DRONE_SIZE))
        except:
            print("Nie można wczytać dron.png, używam czerwonego kwadratu")
            self.drone_img = pygame.Surface((DRONE_SIZE, DRONE_SIZE))
            self.drone_img.fill((255, 0, 0))

        # Moneta
        try:
            coin_raw = pygame.image.load('zdjecia/moneta.png')
            self.coin_img = pygame.transform.scale(coin_raw, (COIN_SIZE, COIN_SIZE))
        except:
            self.coin_img = None

        # Rejestry
        self.register_imgs = {}
        reg_files = {'AX': 'zdjecia/ax.png', 'BX': 'zdjecia/bx.png', 'CX': 'zdjecia/cx.png', 'DX': 'zdjecia/dx.png'}
        for name, fname in reg_files.items():
            try:
                img = pygame.image.load(fname)
                img = pygame.transform.scale(img, (REGISTER_SIZE, REGISTER_SIZE))
                self.register_imgs[name] = img
            except:
                self.register_imgs[name] = None

        # Platforma (RAM)
        try:
            self.ram_img = pygame.image.load('zdjecia/ram.png')
        except:
            self.ram_img = None

        # Tło menu głównego
        try:
            self.background = pygame.image.load('zdjecia/tlo.png')
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None

    def create_menu_buttons(self):
        x_center = SCREEN_WIDTH // 2 - 100
        return [
            Button(x_center, 250, 200, 50, "Graj", action=self.open_level_select),
            Button(x_center, 320, 200, 50, "Wybierz postać", action=self.open_char_select),
            Button(x_center, 390, 200, 50, "Sklep", action=self.open_shop),
            Button(x_center, 460, 200, 50, "Zasady", action=self.open_rules),
            Button(x_center, 530, 200, 50, "Wyjdź", action=self.exit_game)
        ]

    def create_level_buttons(self):
        buttons = []
        y = 200
        for i in range(len(LEVELS)):
            text = f"Poziom {i+1}"
            enabled = self.unlocked_levels[i]
            action = lambda idx=i: self.start_level(idx) if self.unlocked_levels[idx] else None
            btn = Button(300, y, 200, 50, text, action=action, enabled=enabled)
            buttons.append(btn)
            y += 70
        buttons.append(Button(300, y, 200, 50, "Powrót", action=self.back_to_menu))
        return buttons

    def create_char_select_buttons(self):
        """Tworzy przyciski wyboru postaci z odblokowanych skórek."""
        buttons = []
        y = 200
        for skin in SKIN_PRICES:
            if self.unlocked_skins[skin]:
                thumb = pygame.transform.scale(self.skins[skin], (40, 80))
                text = skin + (" (aktualna)" if skin == self.current_skin else "")
                btn = Button(300, y, 300, 70, text, thumbnail=thumb,
                             action=lambda s=skin: self.select_skin(s))
                buttons.append(btn)
                y += 80
        buttons.append(Button(300, y, 200, 50, "Powrót", action=self.back_to_menu))
        return buttons

    def create_shop_buttons(self):
        buttons = []
        y = 150
        for skin in SKIN_PRICES:
            price = SKIN_PRICES[skin]
            if self.unlocked_skins[skin]:
                text = f"{skin} (odblokowana)"
            else:
                text = f"{skin} - {price} monet"
            thumb = pygame.transform.scale(self.skins[skin], (30, 60))
            btn = Button(150, y, 300, 70, text, thumbnail=thumb, action=lambda s=skin: self.buy_skin(s))
            buttons.append(btn)
            y += 80
        buttons.append(Button(400, 650, 200, 50, "Powrót", action=self.back_to_menu))
        return buttons

    def buy_skin(self, skin_name):
        if self.unlocked_skins[skin_name]:
            self.add_message("Już masz tę skórkę!")
            return
        price = SKIN_PRICES[skin_name]
        if self.coins >= price:
            self.coins -= price
            self.unlocked_skins[skin_name] = True
            self.add_message(f"Kupiono {skin_name}!")
            self.shop_buttons = self.create_shop_buttons()
            # odśwież również przyciski wyboru postaci
            self.char_select_buttons = self.create_char_select_buttons()
        else:
            self.add_message("Za mało monet!")

    def add_message(self, text, duration=MESSAGE_DURATION):
        self.messages.append([text, duration])

    def open_level_select(self):
        self.level_buttons = self.create_level_buttons()
        self.state = "LEVEL_SELECT"

    def open_char_select(self):
        self.char_select_buttons = self.create_char_select_buttons()
        self.state = "CHAR_SELECT"

    def select_skin(self, skin_name):
        if skin_name != self.current_skin:
            self.current_skin = skin_name
            self.add_message(f"Wybrano skórkę: {skin_name}")
            # odśwież przyciski, aby zaktualizować etykietę "(aktualna)"
            self.char_select_buttons = self.create_char_select_buttons()

    def start_level(self, level_num):
        self.current_level = level_num
        self.hp = MAX_HP
        self.load_level(level_num)
        self.state = "GAME"

    def load_level(self, level_num):
        self.all_sprites.empty()
        self.platforms.empty()
        self.coins_group.empty()
        self.registers.empty()
        self.interrupts.empty()

        data = LEVELS[level_num]

        # Platformy z grafiką RAM
        for x, y, w, h in data['platforms']:
            p = Platform(x, y, w, h, self.ram_img)
            self.platforms.add(p)
            self.all_sprites.add(p)

        # Monety
        for x, y in data['coins']:
            c = Coin(x, y, self.coin_img)
            self.coins_group.add(c)
            self.all_sprites.add(c)

        # Rejestry
        for name, x, y in data['registers']:
            img = self.register_imgs.get(name)
            r = Register(x, y, name, img)
            self.registers.add(r)
            self.all_sprites.add(r)

        # Drony
        for x, y in data['interrupts']:
            i = Interrupt(x, y, self.drone_img)
            self.interrupts.add(i)
            self.all_sprites.add(i)

        # Gracz – używamy aktualnej skórki
        self.player = Player(100, 700, self.skins[self.current_skin])
        self.all_sprites.add(self.player)

        self.mode = "Real"
        self.interrupt_flag = 1
        self.program_counter = 0x0000

        self.add_message(f"Poziom {level_num + 1}")

    def level_complete(self):
        if self.current_level < len(LEVELS) - 1:
            self.unlocked_levels[self.current_level + 1] = True
            # Odśwież przyciski poziomów
            self.level_buttons = self.create_level_buttons()
        self.add_message("Poziom ukończony!", 60)
        self.state = "LEVEL_SELECT"

    def open_shop(self):
        self.shop_buttons = self.create_shop_buttons()
        self.state = "SHOP"

    def open_rules(self):
        self.state = "RULES"

    def back_to_menu(self):
        self.state = "MENU"

    def exit_game(self):
        self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "MENU":
                for btn in self.menu_buttons:
                    btn.handle_event(event)

            elif self.state == "LEVEL_SELECT":
                for btn in self.level_buttons:
                    btn.handle_event(event)

            elif self.state == "CHAR_SELECT":
                for btn in self.char_select_buttons:
                    btn.handle_event(event)

            elif self.state == "SHOP":
                for btn in self.shop_buttons:
                    btn.handle_event(event)

            elif self.state == "RULES":
                self.rules_button.handle_event(event)

            elif self.state == "GAME":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        self.interrupt_flag = 1 - self.interrupt_flag
                        self.add_message(f"Flaga I = {self.interrupt_flag}")
                    if event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

    def update(self):
        if self.state == "GAME" and self.player:
            self.player.update(self.platforms)
            self.interrupts.update()

            # Zebranie monet
            collected_coins = pygame.sprite.spritecollide(self.player, self.coins_group, True)
            if collected_coins:
                self.coins += len(collected_coins)
                self.add_message(f"+{len(collected_coins)} monet")

            # Zebranie rejestrów
            collected_regs = pygame.sprite.spritecollide(self.player, self.registers, True)
            for reg in collected_regs:
                self.coins += 5
                self.add_message(f"Zebrano rejestr {reg.name} (+5)")

            # Kolizja z dronami (tylko gdy flaga I=1)
            if self.interrupt_flag == 1:
                hits = pygame.sprite.spritecollide(self.player, self.interrupts, True)
                if hits:
                    self.hp -= DAMAGE
                    self.add_message(f"Uderzenie drona! HP: {self.hp}", 60)
                    if self.hp <= 0:
                        self.add_message("GAME OVER", 120)
                        pygame.time.wait(2000)
                        self.coins = max(0, self.coins - 50)  # Kara 50 monet
                        self.state = "MENU"
                        return

            # Symulacja PC
            self.program_counter = (self.program_counter + 1) & 0xFFFF

            # Sprawdzenie ukończenia poziomu
            if len(self.coins_group) == 0 and len(self.registers) == 0:
                self.level_complete()

        # Komunikaty
        for msg in self.messages[:]:
            msg[1] -= 1
            if msg[1] <= 0:
                self.messages.remove(msg)

        # Ciekawostki
        self.fact_timer += 1
        if self.fact_timer > FPS * 3:
            self.fact_timer = 0
            self.fact_index = (self.fact_index + 1) % len(FACTS)

    def draw(self):
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "LEVEL_SELECT":
            self.draw_level_select()
        elif self.state == "CHAR_SELECT":
            self.draw_char_select()
        elif self.state == "SHOP":
            self.draw_shop()
        elif self.state == "RULES":
            self.draw_rules()
        elif self.state == "GAME":
            self.draw_game()

        self.draw_fact_bar()
        pygame.display.flip()

    def draw_menu(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        if self.logo:
            x = SCREEN_WIDTH//2 - self.logo.get_width()//2
            self.screen.blit(self.logo, (x, 150))
        else:
            title = self.font.render("CPU QUEST", True, (0, 255, 0))
            x = SCREEN_WIDTH//2 - title.get_width()//2
            self.screen.blit(title, (x, 150))

        for btn in self.menu_buttons:
            btn.draw(self.screen)

    def draw_level_select(self):
        if self.level_select_bg:
            self.screen.blit(self.level_select_bg, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        title = self.font.render("WYBIERZ POZIOM", True, (255, 215, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        for btn in self.level_buttons:
            btn.draw(self.screen)

    def draw_char_select(self):
        if self.level_select_bg:
            self.screen.blit(self.level_select_bg, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        title = self.font.render("WYBIERZ POSTAĆ", True, (255, 215, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        for btn in self.char_select_buttons:
            btn.draw(self.screen)

    def draw_shop(self):
        if self.shop_bg:
            self.screen.blit(self.shop_bg, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        title = self.font.render("SKLEP", True, (255, 215, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        coins_text = self.small_font.render(f"Monety: {self.coins}", True, (255, 255, 0))
        self.screen.blit(coins_text, (50, 50))
        for btn in self.shop_buttons:
            btn.draw(self.screen)

    def draw_rules(self):
        self.screen.fill((30, 30, 30))
        title = self.font.render("ZASADY GRY", True, (255, 215, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        rules = [
            "Sterowanie: strzałki/WASD - ruch, Spacja - skok",
            "I - przełącz flagę I (przerwania aktywne gdy flaga=1)",
            "Zbieraj monety i rejestry (niebieskie) - dodają punkty.",
            "Unikaj dronów (czerwone) - zabierają HP.",
            "Po zebraniu wszystkich monet i rejestrów przechodzisz dalej.",
            "W sklepie możesz kupować nowe skórki za monety."
        ]
        y = 150
        for line in rules:
            text = self.small_font.render(line, True, (255,255,255))
            self.screen.blit(text, (50, y))
            y += 30
        self.rules_button.draw(self.screen)

    def draw_game(self):
        # Rysuj tło poziomu
        if self.current_level < len(self.level_bgs) and self.level_bgs[self.current_level]:
            self.screen.blit(self.level_bgs[self.current_level], (0, 0))
        else:
            self.screen.fill(BG_COLOR_REAL if self.mode == "Real" else BG_COLOR_PROTECTED)

        self.all_sprites.draw(self.screen)

        # Statystyki
        stats_y = 10
        coin_text = self.small_font.render(f"Monety: {self.coins}", True, FONT_COLOR)
        self.screen.blit(coin_text, (SCREEN_WIDTH - 200, stats_y))
        stats_y += 30

        hp_text = self.small_font.render(f"HP: {self.hp}/{MAX_HP}", True, (255, 100, 100))
        self.screen.blit(hp_text, (SCREEN_WIDTH - 200, stats_y))
        stats_y += 30

        now = datetime.datetime.now().strftime("%H:%M:%S")
        time_text = self.small_font.render(f"Czas: {now}", True, FONT_COLOR)
        self.screen.blit(time_text, (SCREEN_WIDTH - 200, stats_y))

        # Informacje o procesorze
        info_x = 10
        info_y = 150
        mode_text = self.small_font.render(f"Tryb: {self.mode}", True, FONT_COLOR)
        self.screen.blit(mode_text, (info_x, info_y))
        info_y += 30
        flag_text = self.small_font.render(f"Flaga I: {self.interrupt_flag}", True, FONT_COLOR)
        self.screen.blit(flag_text, (info_x, info_y))
        info_y += 30
        pc_text = self.small_font.render(f"PC: 0x{self.program_counter:04X}", True, FONT_COLOR)
        self.screen.blit(pc_text, (info_x, info_y))
        info_y += 30
        level_text = self.small_font.render(f"Poziom: {self.current_level + 1}/{len(LEVELS)}", True, FONT_COLOR)
        self.screen.blit(level_text, (info_x, info_y))

        # Komunikaty
        msg_y = 300
        for msg, _ in self.messages[-5:]:
            msg_surf = self.message_font.render(msg, True, (255, 255, 0))
            self.screen.blit(msg_surf, (10, msg_y))
            msg_y += 22

        # Instrukcja
        instr = self.small_font.render("ESC - menu, I - przełącz flagę", True, FONT_COLOR)
        self.screen.blit(instr, (10, SCREEN_HEIGHT - 60))

    def draw_fact_bar(self):
        bar_height = 50
        bar_rect = pygame.Rect(0, SCREEN_HEIGHT - bar_height, SCREEN_WIDTH, bar_height)
        pygame.draw.rect(self.screen, (0, 0, 0), bar_rect)
        pygame.draw.line(self.screen, (255, 255, 255), (0, SCREEN_HEIGHT - bar_height), (SCREEN_WIDTH, SCREEN_HEIGHT - bar_height), 2)

        fact = FACTS[self.fact_index]
        lines = wrap_text(f"💡 {fact}", self.small_font, SCREEN_WIDTH - 40)
        y = SCREEN_HEIGHT - bar_height + 10
        for line in lines:
            fact_surf = self.small_font.render(line, True, (200, 200, 0))
            self.screen.blit(fact_surf, (20, y))
            y += 22

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()