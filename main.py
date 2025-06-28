import pygame
import time
import random
import json

# pygame setup
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("sounds/background_music.mp3")

FPS = 60

info = pygame.display.Info()
screen_width = 1920
screen_height = 1080
active_screen = 0 #load into background screen 
 
screen = pygame.display.set_mode((screen_width, screen_height)) 
clock = pygame.time.Clock()
running = True

with open("data/data.json", "r") as f:
    data = json.load(f)
    high_score = data.get("high_score", 0) 
    music_power = data.get("music_v", 0.5)
    sound_power = data.get("sound_v", 0.5)
    skin = data.get("skin", 0)  # Default
    f.close()

options = {
    "music_volume": music_power,  # Default to 0.5 if not set
    "sound_volume": sound_power,  # Default to 0.5 if not set
    "music_knob_x": (music_power*300 + 810),
    "music_knob_y": (screen_height/2)-15,
    "sound_knob_x": (sound_power*300 + 810),
    "sound_knob_y": (screen_height/2)+85
}

pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(options["music_volume"])  # Range: 0.0 (mute) to 1.0 (max)


collision_sound1 = pygame.mixer.Sound("sounds/jump.mp3") 
collision_sound2 = pygame.mixer.Sound("sounds/jump2.mp3")  

game_over_sound = pygame.mixer.Sound("sounds/game_over.mp3")

button_click_sound = pygame.mixer.Sound("sounds/button.mp3")

platforms = []
score_font = pygame.font.SysFont("Arial", 72) #font 
high_score_font = pygame.font.SysFont("Arial", 48)

def set_volume(sound_volume):

    collision_sound1.set_volume(sound_volume)
    collision_sound2.set_volume(sound_volume)
    button_click_sound.set_volume(sound_volume)
    game_over_sound.set_volume(sound_volume)

set_volume(options["sound_volume"])
        
class Player:
    def __init__(self):
        super().__init__()
        self.image_right = pygame.image.load("assets/player_right.png")
        self.image_left = pygame.image.load("assets/player_left.png")
        self.image_left_girl = pygame.image.load("assets/player_left_girl.png")
        self.image_right_girl = pygame.image.load("assets/player_right_girl.png")
        self.rect = self.image_right.get_rect()
        self.rect.center = (screen_width / 2, screen_height / 2)
        self.vel_y = 0
        self.is_alive = True
        self.score = 0
        self.last_keypress = None
        self.skin = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 20
            self.last_keypress = 'left'
        if keys[pygame.K_RIGHT]:
            self.rect.x += 20
            self.last_keypress = 'right'

        self.vel_y += 0.5  # gravity
        self.rect.y += self.vel_y

        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.top + 20:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = -20
                    random.choice([collision_sound1, collision_sound2]).play()
                    break  # jump on only one platform per frame

        # scroll the screen up if player goes above a threshold  (top 1/3)
        if self.rect.top <= screen_height / 3:
            scroll_y = (screen_height / 3) - self.rect.top
            self.rect.top = screen_height / 3  # fix player position
            for platform in platforms:
                platform.rect.y += scroll_y
                self.score += scroll_y

        if self.rect.y >= screen_height:
            self.is_alive = False

    def reset(self):
        self.image = pygame.image.load("assets/player_right.png")
        self.rect = self.image.get_rect()
        self.rect.center = (screen_width / 2, screen_height / 2)
        self.vel_y = 0
        self.is_alive = True

class Platform:
    def __init__(self,x,y,width,height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((67, 67, 67))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        

        
@staticmethod        
def create_platforms(platforms):
    # Remove platforms that are off the screen (bottom)
    platforms[:] = [p for p in platforms if p.rect.y < screen_height]

    # Add new platform if the highest one is low enough
    highest_y = min([p.rect.y for p in platforms]) if platforms else screen_height
    if highest_y > 100:  # adjust how often to add
        x = random.randint(100, screen_width - 200)
        y = highest_y - random.randint(100, 150)
        platforms.append(Platform(x, y, 100, 20))

player = Player()
game_background = pygame.image.load("assets/game_background.png")
starter_platform = Platform(screen_width/2-50, 920, 100, 20)
platforms.append(starter_platform)
create_platforms(platforms)


while running:
    
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            with open("data/data.json", "w") as f:
               data = {
                    "high_score": high_score,
                    "music_v": options["music_volume"],
                    "sound_v": options["sound_volume"],
                    "skin": skin
                }
               json.dump(data, f)
            running = False

    if active_screen == 0: #background screen
        background = pygame.image.load("assets/background.png")
        screen.blit(background, (0, 0))

        option_button = pygame.image.load("assets/option_button.png")
        play_button = pygame.image.load("assets/play_button.png")
        screen.blit(play_button,((screen_width-240)/2,(screen_height-60)/2))
        screen.blit(option_button,((screen_width-240)/2,(screen_height-60)/2+90))

               
        boy_pos = (600, screen_height - 200)
        boy_skin = player.image_right.get_rect(topleft=boy_pos)
        boy_rect = boy_skin.inflate(20, 20)
        if skin == 0:
            pygame.draw.rect(screen, (0, 0, 0), boy_rect, width=10)
        screen.blit(player.image_right, boy_pos)

        girl_pos = (1200, screen_height - 200)
        girl_skin = player.image_left_girl.get_rect(topleft=girl_pos)
        girl_rect = girl_skin.inflate(20, 20)
        if skin == 1:
            pygame.draw.rect(screen, (0,0,0), girl_rect, width=10)
        screen.blit(player.image_left_girl, girl_pos)

        if girl_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            skin = 1
            button_click_sound.play()
            time.sleep(0.25)
        if boy_rect.collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            skin = 0
            button_click_sound.play()
            time.sleep(0.25)

        if mouse_pos[0] > (screen_width-240)/2 and mouse_pos[0] < (screen_width+240)/2 and mouse_pos[1] > (screen_height-60)/2 and mouse_pos[1] < (screen_height+60)/2:
            play_button_hover = pygame.image.load("assets/play_button_hovered.png")
            screen.blit(play_button_hover,((screen_width-240)/2,(screen_height-60)/2))
            if pygame.mouse.get_pressed()[0]:
                button_click_sound.play()
                
                time.sleep(0.25)
                active_screen = 1


        if mouse_pos[0] > (screen_width-240)/2 and mouse_pos[0] < (screen_width+240)/2 and mouse_pos[1] > (screen_height-60)/2+90 and mouse_pos[1] < (screen_height+60)/2+90:
            option_button_hover = pygame.image.load("assets/option_button_hovered.png")
            screen.blit(option_button_hover,((screen_width-240)/2,(screen_height-60)/2+90))
            if pygame.mouse.get_pressed()[0]:
                button_click_sound.play()
                time.sleep(0.25)
                active_screen = 2

    if active_screen == 2: #options screen
        screen.blit(background, (0, 0))
        music_text = pygame.font.SysFont("Arial", 24).render("Music Volume:", True, (255, 255, 255))
        sound_text = pygame.font.SysFont("Arial", 24).render("Sound Volume:", True, (255, 255, 255))
        screen.blit(music_text, (screen_width/2-150, screen_height/2-50))
        screen.blit(sound_text, (screen_width/2-150, screen_height/2+50))

        slider_x = (screen_width/2)-150
        slider_y = screen_height/2
        slider_width = 300
        slider_height = 10
        
        music_sound_rectangle = pygame.draw.rect(background, (67, 205, 240), (slider_x-20, slider_y-20, 350, 150))  #lightblue box sourounding settings
        music_slider = pygame.draw.rect(background, (192, 192, 192), (slider_x, slider_y, slider_width, slider_height))  
        music_knob = pygame.draw.rect(background,(153, 00, 48), (options["music_knob_x"], options["music_knob_y"], 20, 40))  
        volume_slider = pygame.draw.rect(background, (192, 192, 192), (slider_x, slider_y + 100, slider_width, slider_height))  
        sound_knob = pygame.draw.rect(background,(153, 00, 48), (options["sound_knob_x"], options["sound_knob_y"], 20, 40)) 
        music_knob_offset = mouse_pos[0] - (slider_x + 150) 

        if music_slider.collidepoint(mouse_pos): #music slder
            if pygame.mouse.get_pressed()[0]:
                music_volume = (mouse_pos[0] - slider_x) / slider_width
                options["music_volume"] =  music_volume
                pygame.mixer.music.set_volume(music_volume)
                options["music_knob_x"] = mouse_pos[0]-10

        if volume_slider.collidepoint(mouse_pos): #sound slider
            if pygame.mouse.get_pressed()[0]:
                sound_volume = (mouse_pos[0] - slider_x) / slider_width
                options["sound_knob_x"] = mouse_pos[0]-10
                options["sound_volume"] = sound_volume
                set_volume(sound_volume)

        back_button = pygame.image.load("assets/back_button.png")
        screen.blit(back_button,((screen_width-240)/2,(screen_height-60)/2+200))

        if mouse_pos[0] > (screen_width-240)/2 and mouse_pos[0] < (screen_width+240)/2 and mouse_pos[1] > (screen_height-60)/2+200 and mouse_pos[1] < (screen_height+60)/2+200:
            back_button_hover = pygame.image.load("assets/back_button_hovered.png")
            screen.blit(back_button_hover,((screen_width-240)/2,(screen_height-60)/2+200))
            if pygame.mouse.get_pressed()[0]:
                button_click_sound.play()
                time.sleep(0.25)
                active_screen = 0

    if active_screen == 1: #play screen
        create_platforms(platforms)
        screen.blit(game_background, (0, 0))
        score_on_board = score_font.render(str(int(player.score//100)), True, (255, 255, 255))
        high_score_on_board = high_score_font.render(str(int(high_score//100)), True, (255, 255, 255))
        screen.blit(score_on_board, (0,0))
        screen.blit(high_score_on_board, (0,60))

        if skin == 0: #boy skin
            if player.last_keypress == 'left':
                screen.blit(player.image_left, player.rect.topleft)
            else:
                screen.blit(player.image_right, player.rect.topleft)

        if skin == 1: #girl skin
            if player.last_keypress == 'left':
                screen.blit(player.image_left_girl, player.rect.topleft)
            else:
                screen.blit(player.image_right_girl, player.rect.topleft)

        for platform in platforms:
            if platform.rect.y <= screen_height and platform.rect.y >= 0:
                screen.blit(platform.image, platform.rect.topleft)
        player.update()
        if player.score > high_score:
            high_score = player.score


        if not player.is_alive:
            pygame.mixer.music.stop()
            game_over_sound.play()
            game_over_image = pygame.image.load("assets/game_over.png")
            screen.blit(game_over_image, (0, 0))
            pygame.display.flip()  
            time.sleep(2)
            pygame.mixer.music.play(-1)
            player.score = 0
            starter_platform = Platform(screen_width/2-50, 920, 100, 20)
            platforms.append(starter_platform)
            player.reset()
            create_platforms(platforms)
            active_screen = 0
        
    clock.tick(FPS)  # limits FPS 
    pygame.display.flip()

pygame.quit()