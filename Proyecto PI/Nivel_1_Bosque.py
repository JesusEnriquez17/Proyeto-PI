import pygame
import pytmx

def draw_tilemap(surface, tmxdata):
    # Iterar a través de todas las capas visibles del mapa de teselas (tilemap)
    for layer in tmxdata.visible_layers:
        # Verificar si la capa es una capa de teselas
        if isinstance(layer, pytmx.TiledTileLayer):
            # Iterar a través de las teselas en la capa
            for x, y, gid in layer:
                # Obtener la imagen de la tesela por su gid (identificador global)
                tile = tmxdata.get_tile_image_by_gid(gid)
                # Si la tesela tiene una imagen, dibujarla en la superficie
                if tile:
                    surface.blit(tile, (x * tmxdata.tilewidth, y * tmxdata.tileheight))

def load_pygame(filename, colorkey=None):
    # Cargar el mapa de teselas utilizando pytmx y configurarlo para el uso con pygame
    tmxdata = pytmx.util_pygame.load_pygame(filename, colorkey)
    return tmxdata

def draw_tilemap_offset(surface, tmxdata, offset_x, offset_y):
    # Iterar a través de todas las capas visibles del mapa de teselas (tilemap)
    for layer in tmxdata.visible_layers:
        # Verificar si la capa es una capa de teselas
        if isinstance(layer, pytmx.TiledTileLayer):
            # Iterar a través de las teselas en la capa
            for x, y, gid in layer:
                # Obtener la imagen de la tesela por su gid (identificador global)
                tile = tmxdata.get_tile_image_by_gid(gid)
                # Si la tesela tiene una imagen, dibujarla en la superficie
                if tile:
                    surface.blit(tile, ((x * tmxdata.tilewidth) - offset_x, (y * tmxdata.tileheight) - offset_y))

# Inicializar pygame
pygame.init()
# Configurar el tamaño de la ventana
screen = pygame.display.set_mode((1000, 575))
# Cargar datos del mapa de teselas
tmxdata = load_pygame("img/Mapas/MapaBosque.tmx")
# Extraer objetos de colisión del mapa de teselas
collision_objects = [obj for obj in tmxdata.objects if obj.properties.get("collision", False)]
pygame.mixer.init()
pygame.mixer.music.load('sounds/Action 01.WAV')
pygame.mixer.music.set_volume(50.0)  # Ajusta el volumen (0.0 a 1.0)
pygame.mixer.music.play(-1)  # -1 indica que la música se repetirá indefinidamente
# Definir la cámara
camera_rect = pygame.Rect(0, 0, 1000, 575)

# Definir rectángulo del jugador y algunas variables de física
player_rect = pygame.Rect(50, 50, 30, 60)  # x, y, width, height
player_velocity = [0, 0]  # [vx, vy]
gravity = 1
jump_height = -15
jumping = False

# Iniciar bucle de juego principal
running = True
while running:
    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Capturar entrada del teclado
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_velocity[0] = -5  # Mover izquierda
    elif keys[pygame.K_d]:
        player_velocity[0] = 5   # Mover derecha
    else:
        player_velocity[0] = 0   # Detener movimiento horizontal
    
    # Verificar si se presiona la tecla para saltar y el jugador no está ya saltando
    if keys[pygame.K_w] and not jumping:
        player_velocity[1] = jump_height  # Iniciar salto
        jumping = True
    
    # Aplicar gravedad al jugador
    player_velocity[1] += gravity  

    # Predecir la próxima posición del jugador antes de moverlo
    next_rect_x = player_rect.x + player_velocity[0]
    next_rect_y = player_rect.y + player_velocity[1]

    # Verificar colisiones en horizontal
    horizontal_collision = False
    for obj in collision_objects:
        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if obj_rect.colliderect(pygame.Rect(next_rect_x, player_rect.y, player_rect.width, player_rect.height)):
            horizontal_collision = True
            break

    # Actualizar posición x del jugador si no hay colisión horizontal
    if not horizontal_collision:
        player_rect.x = next_rect_x
    
    # Verificar colisiones en vertical
    vertical_collision = False
    for obj in collision_objects:
        obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        if obj_rect.colliderect(pygame.Rect(player_rect.x, next_rect_y, player_rect.width, player_rect.height)):
            vertical_collision = True
            jumping = False
            player_velocity[1] = 0  # Reiniciar velocidad vertical
            break

    # Actualizar posición y del jugador si no hay colisión vertical
    if not vertical_collision:
        player_rect.y = next_rect_y
    
     # 3. Actualizar la Cámara
    camera_rect.centerx = player_rect.centerx  # Centrar cámara en el jugador (eje x)
    camera_rect.centery = player_rect.centery  # Centrar cámara en el jugador (eje y)

    # Limitar la cámara para que no muestre áreas fuera del mapa
    camera_rect.x = max(0, min(camera_rect.x, tmxdata.width * tmxdata.tilewidth - camera_rect.width))
    camera_rect.y = max(0, min(camera_rect.y, tmxdata.height * tmxdata.tileheight - camera_rect.height))

    # Limpiar pantalla
    screen.fill((0, 0, 0))

    # Dibujar el mapa de teselas con la cámara ajustada
    draw_tilemap_offset(screen, tmxdata, camera_rect.x, camera_rect.y)
    
    # Dibujar al jugador ajustando a la cámara
    pygame.draw.rect(screen, (255, 0, 0), player_rect.move(-camera_rect.x, -camera_rect.y))
    
    # Actualizar la pantalla
    pygame.display.flip()
    pygame.time.Clock().tick(120)


# Finalizar pygame al salir del bucle de juego
pygame.quit()
