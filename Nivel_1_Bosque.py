import pygame
import pytmx
import random

def draw_tilemap_offset(surface, tmxdata, offset_x, offset_y):
    for layer in tmxdata.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmxdata.get_tile_image_by_gid(gid)
                if tile:
                    surface.blit(tile, ((x * tmxdata.tilewidth) - offset_x, (y * tmxdata.tileheight) - offset_y))

def load_pygame(filename, colorkey=None):
    tmxdata = pytmx.util_pygame.load_pygame(filename, colorkey)
    return tmxdata

image_files = ["img/Comida/naranja.png"]

def draw_collectibles(surface, collectibles, camera_rect):
    for collectible in collectibles:
        # Selecciona una imagen al azar de la lista
        image_path = random.choice(image_files)
        image = pygame.image.load(image_path)
        rect = pygame.Rect(collectible.x, collectible.y, collectible.width, collectible.height)
        surface.blit(image, rect.move(-camera_rect.x, -camera_rect.y))

# Inicializar pygame
pygame.init()
logo = pygame.image.load('logo.png')
pygame.display.set_icon(logo)
pygame.display.set_caption('Hunger´s Hero')
screen = pygame.display.set_mode((1000, 575))
tmxdata = load_pygame("MapaBosque/MapaBosque/MapaBosque.tmx")
collision_objects = [obj for obj in tmxdata.objects if obj.properties.get("collision", False)]
collectibles = [obj for obj in tmxdata.objects if obj.properties.get("collectible", False)]

pygame.mixer.init()
pygame.mixer.music.load('sounds/Musiclv1.WAV')
pygame.mixer.music.set_volume(50.0)
pygame.mixer.music.play(-1)

collectible_sound = pygame.mixer.Sound("sounds/Selec.wav")
def play_collectible_sound():
    collectible_sound.play()

# Define las dimensiones de cada frame en la imagen.
frame_width = 32  # Ancho de un frame
frame_height = 64  # Alto de un frame
# Crea una lista para almacenar los frames.
frames_right = []
player_frames_right = pygame.image.load("img/Personaje/Derecha.png")
for y in range(0, player_frames_right.get_height(), frame_height):
    for x in range(0, player_frames_right.get_width(), frame_width):
        frame = player_frames_right.subsurface(pygame.Rect(x, y, frame_width, frame_height))
        frames_right.append(frame)

# Cargar los frames de movimiento hacia la izquierda
frames_left = []
player_frames_left = pygame.image.load("img/Personaje/Izquierda.png")
for y in range(0, player_frames_left.get_height(), frame_height):
    for x in range(0, player_frames_left.get_width(), frame_width):
        frame = player_frames_left.subsurface(pygame.Rect(x, y, frame_width, frame_height))
        frames_left.append(frame)

# Cargar los frames de salto hacia la derecha
frames_jump_right = []
player_frames_jump_right = pygame.image.load("img/Personaje/SaltoDerecha.png")
for y in range(0, player_frames_jump_right.get_height(), frame_height):
    for x in range(0, player_frames_jump_right.get_width(), frame_width):
        frame = player_frames_jump_right.subsurface(pygame.Rect(x, y, frame_width, frame_height))
        frames_jump_right.append(frame)

# Cargar los frames de salto hacia la izquierda
frames_jump_left = []
player_frames_jump_left = pygame.image.load("img/Personaje/SaltoIzquierda.png")
for y in range(0, player_frames_jump_left.get_height(), frame_height):
    for x in range(0, player_frames_jump_left.get_width(), frame_width):
        frame = player_frames_jump_left.subsurface(pygame.Rect(x, y, frame_width, frame_height))
        frames_jump_left.append(frame)


# Definir la variable para rastrear el estado de la animación
current_walk_frame = 0
current_jump_frame = 0

# Definir la velocidad de la animación (un valor mayor ralentizará la animación).
animation_speed = 10
frame_change_timer = 0

def play_saltar_sound():
    sonido_saltar = pygame.mixer.Sound("sounds/Salto.wav")
    sonido_saltar.play()

camera_rect = pygame.Rect(0, 0, 1000, 575)
player_image = pygame.image.load("img/Personaje/Tilin.png")
player_rect = player_image.get_rect()
player_rect.x = 50
player_rect.y = 50
player_rect.width = 30
player_rect.height = 60
player_velocity = [0, 0]
gravity = 1
jump_height = -15
jumping = False

moving_left = False
jumping = True

collected_count = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        player_velocity[0] = -5
        frame_change_timer += 1  # Incrementa el temporizador
        if frame_change_timer >= animation_speed:
            frame_change_timer = 0  # Reinicia el temporizador
            current_walk_frame = (current_walk_frame + 1) % len(frames_left)  # Para caminar a la izquierda
        moving_left = True

    elif keys[pygame.K_d]:
        player_velocity[0] = 5
        frame_change_timer += 1
        if frame_change_timer >= animation_speed:
            frame_change_timer = 0
            current_walk_frame = (current_walk_frame + 1) % len(frames_right)  # Para caminar a la derecha
        moving_left = False

    else:
        player_velocity[0] = 0
        frame_change_timer = 0  # Reinicia el temporizador
        moving_left = False

    if keys[pygame.K_w] and not jumping:
        player_velocity[1] = jump_height
        jumping = True
        play_saltar_sound()  # Reproducir el sonido de salto
        frame_change_timer += 1  # Incrementa el temporizador
        if frame_change_timer >= animation_speed:
            frame_change_timer = 0  # Reinicia el temporizador
            current_jump_frame = (current_jump_frame + 1) % len(frames_jump_left)  # Para la animación de salto


    player_velocity[1] += gravity
    next_rect_x = player_rect.x + player_velocity[0]
    next_rect_y = player_rect.y + player_velocity[1]

    horizontal_collision = False
    for obj in collision_objects:
        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if obj_rect.colliderect(pygame.Rect(next_rect_x, player_rect.y, player_rect.width, player_rect.height)):
            horizontal_collision = True
            break

    if not horizontal_collision:
        player_rect.x = next_rect_x
    
    vertical_collision = False
    for obj in collision_objects:
        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if obj_rect.colliderect(pygame.Rect(player_rect.x, next_rect_y, player_rect.width, player_rect.height)):
            vertical_collision = True
            jumping = False
            player_velocity[1] = 0
            break

    if not vertical_collision:
        player_rect.y = next_rect_y

    camera_rect.centerx = player_rect.centerx
    camera_rect.centery = player_rect.centery
    camera_rect.x = max(0, min(camera_rect.x, tmxdata.width * tmxdata.tilewidth - camera_rect.width))
    camera_rect.y = max(0, min(camera_rect.y, tmxdata.height * tmxdata.tileheight - camera_rect.height))

    screen.fill((0, 0, 0))
    draw_tilemap_offset(screen, tmxdata, camera_rect.x, camera_rect.y)
    draw_collectibles(screen, collectibles, camera_rect)
    
    # Check collision with collectibles
    collected = []
    for collectible in collectibles:
        rect = pygame.Rect(collectible.x, collectible.y, collectible.width, collectible.height)
        if player_rect.colliderect(rect):
            collected.append(collectible)
            collected_count += 1
            play_collectible_sound()
    
    collectibles = [c for c in collectibles if c not in collected]

    if moving_left:
        if keys[pygame.K_w] and not jumping:
            current_jump_frame = 0  # Iniciar animación de salto
            jumping = True

        if jumping:
            screen.blit(frames_jump_left[current_jump_frame], player_rect.move(-camera_rect.x, -camera_rect.y))
            current_jump_frame = (current_jump_frame + 1) % len(frames_jump_left)
        else:
            screen.blit(frames_left[current_walk_frame], player_rect.move(-camera_rect.x, -camera_rect.y))
    else:
        if keys[pygame.K_w] and not jumping:
            current_jump_frame = 0  # Iniciar animación de salto
            jumping = True

        if jumping:
            screen.blit(frames_jump_right[current_jump_frame], player_rect.move(-camera_rect.x, -camera_rect.y))
            current_jump_frame = (current_jump_frame + 1) % len(frames_jump_right)
        else:
            screen.blit(frames_right[current_walk_frame], player_rect.move(-camera_rect.x, -camera_rect.y))


# Controla la velocidad de la animación utilizando un temporizador.
    pygame.time.delay(animation_speed)
    
    # Draw collectible count
    font = pygame.font.Font(None, 36)
    text = font.render(f"Comida: {collected_count}", True, (255, 255, 255))
    screen.blit(text, (screen.get_width() - 200, 20))
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()

