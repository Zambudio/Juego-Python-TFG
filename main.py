import sys
import pygame, random, os

# Tamaño pantalla
ANCHO_PANTALLA = 1000
ALTO_PANTALLA = 800

# Tamaño barra de vida jugador
LARGO_BARRA_VIDA = 200
ANCHO_BARRA_VIDA = 20

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
AMARILLO = (237, 250, 81)
ROJO = (255, 0, 0)

# Power up
POWERUP_CADA_X_PUNTOS = 200
POWERUP_EN_PANTALLA = False

# Textos en pantalla
TEXTO_CABECERA_INICIO = "MARS ATTACK"
TEXTO_FUNCIONAMIENTO = "Utiliza las teclas de direccion para moverte y SPACE para disparar"
TEXTO_INICIAR = "Pulse cualquier tecla para empezar"
TEXTO_CABECERA_FINAL = "FIN DE LA PARTIDA"
TEXTO_PUNTUACION = "Tu puntuacion : "
TEXTO_PUNTUACION_MAXIMA = "TU MEJOR PUNTUACION : "
TEXTO_FINALIZAR = "Pulse ENTER para volver a jugar // Pulse ESC para salir"

class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("recursos/jugador.png").convert()
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO_PANTALLA // 2
        self.rect.bottom = ALTO_PANTALLA - 10
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.vida = 100

    def update(self):
        self.velocidad_x = 0
        self.velocidad_y = 0
        tecla_pulsada = pygame.key.get_pressed()
        if tecla_pulsada[pygame.K_LEFT]:
            self.velocidad_x = -5
        if tecla_pulsada[pygame.K_RIGHT]:
            self.velocidad_x = 5
        self.rect.x += self.velocidad_x
        if self.rect.right > ANCHO_PANTALLA:
            self.rect.right = ANCHO_PANTALLA
        if self.rect.left < 0:
            self.rect.left = 0
        if tecla_pulsada[pygame.K_UP]:
            self.velocidad_y = -5
        if tecla_pulsada[pygame.K_DOWN]:
            self.velocidad_y = 5
        self.rect.y += self.velocidad_y
        if self.rect.bottom > ALTO_PANTALLA:
            self.rect.bottom = ALTO_PANTALLA
        if self.rect.top < 0:
            self.rect.top = 0

    def disparar(self):
        disparo = Disparo(self.rect.centerx, self.rect.top)
        all_sprites.add(disparo)
        disparos.add(disparo)
        sonido_disparo.play()

class Enemigos(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(lista_enemigos)
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO_PANTALLA - self.rect.width)
        self.rect.y = random.randrange(-140, -100)
        self.velocidad_y = random.randrange(1, 10)
        self.velocidad_x = random.randrange(-5, 5)

    def update(self):
        self.rect.y += self.velocidad_y
        self.rect.x += self.velocidad_x
        if self.rect.top > ALTO_PANTALLA + 10 or self.rect.left < -40 or self.rect.right > ANCHO_PANTALLA + 40:
            self.rect.x = random.randrange(ANCHO_PANTALLA - self.rect.width)
            self.rect.y = random.randrange(-140, - 100)
            self.velocidad_y = random.randrange(1, 10)

class Disparo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("recursos/disparo_laser.png")
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = animacion_explosion[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50 # VELOCIDAD DE LA EXPLOSION

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(animacion_explosion):
                self.kill()
            else:
                center = self.rect.center
                self.image = animacion_explosion[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("recursos/powerup.png")
        self.image.set_colorkey(NEGRO)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO_PANTALLA - self.rect.width)
        self.rect.y = random.randrange(-140, -100)
        self.velocidad_y = random.randrange(1, 10)
        self.velocidad_x = random.randrange(-5, 5)

    def update(self):
        self.rect.y += self.velocidad_y
        self.rect.x += self.velocidad_x

        # Comprueba si se sale de la pantalla y hace que rebote
        if self.rect.top < 0:
            self.velocidad_y = -self.velocidad_y
            self.rect.top = 0
        elif self.rect.bottom > ALTO_PANTALLA:
            self.velocidad_y = -self.velocidad_y
            self.rect.bottom = ALTO_PANTALLA
        if self.rect.left < 0:
            self.velocidad_x = -self.velocidad_x
            self.rect.left = 0
        elif self.rect.right > ANCHO_PANTALLA:
            self.velocidad_x = -self.velocidad_x
            self.rect.right = ANCHO_PANTALLA

    def aplicar_powerup(self, jugador):
        jugador.vida += 20
        if jugador.vida > 100:
            jugador.vida = 100

def dibujar_texto(superficie, texto, size, x, y, color):
    ruta_fuente = os.path.join('recursos/Arcade.ttf')
    font = pygame.font.Font(ruta_fuente, size)
    text_surface = font.render(texto, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    superficie.blit(text_surface, text_rect)

def dibujar_barra_vida(superficie, x, y, porcentaje, color):
    relleno = (porcentaje / 100) * LARGO_BARRA_VIDA
    borde = pygame.Rect(x, y, LARGO_BARRA_VIDA, ANCHO_BARRA_VIDA)
    relleno = pygame.Rect(x, y, relleno, ANCHO_BARRA_VIDA)
    pygame.draw.rect(superficie, color, relleno)
    pygame.draw.rect(superficie, BLANCO, borde, 2)

def dibuja_fondo():
    fondo_escalado = pygame.transform.scale(imagen_fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
    pantalla.blit(fondo_escalado, (0, 0))

def mostrar_pantalla_inicio():
    dibuja_fondo()
    dibujar_texto(pantalla, TEXTO_CABECERA_INICIO, 65, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 4, BLANCO)
    dibujar_texto(pantalla, TEXTO_FUNCIONAMIENTO, 27, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2, BLANCO)
    dibujar_texto(pantalla, TEXTO_INICIAR, 27, ANCHO_PANTALLA // 2, ALTO_PANTALLA * 3 / 4, BLANCO)
    pygame.display.flip()
    esperando = True
    while esperando:
        reloj.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                esperando = False

def mostrar_pantalla_final(puntuacion,puntuacion_maxima):
    dibuja_fondo()
    dibujar_texto(pantalla, TEXTO_CABECERA_FINAL, 65, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 4, BLANCO)
    dibujar_texto(pantalla, TEXTO_PUNTUACION_MAXIMA + str(puntuacion_maxima), 65, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 4 + 50, VERDE)
    dibujar_texto(pantalla, TEXTO_PUNTUACION + str(puntuacion), 30, ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2, BLANCO)
    dibujar_texto(pantalla, TEXTO_FINALIZAR, 25, ANCHO_PANTALLA // 2, ALTO_PANTALLA * 3 / 4, BLANCO)
    pygame.display.flip()
    waiting = True
    while waiting:
        reloj.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def add_powerup():
    nuevo_powerup = PowerUp()
    all_sprites.add(nuevo_powerup)
    powerups.add(nuevo_powerup)

pygame.init()
pygame.mixer.init()

pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Juego TFG")
reloj = pygame.time.Clock()

# Cargar imagen de fondo del juego
imagen_fondo = pygame.image.load("recursos/fondo_pantalla.png").convert()

# Cargar imagenes enemigos
lista_enemigos = []
imagenes_enemigos = ["recursos/enemigo_grande_1.png", "recursos/enemigo_grande_2.png", "recursos/enemigo_grande_3.png", "recursos/enemigo_grande_4.png",
                "recursos/enemigo_mediano_1.png", "recursos/enemigo_mediano_2.png", "recursos/enemigo_pequeno_1.png", "recursos/enemigo_pequeno_2.png",
                "recursos/enemigo_diminuto_1.png", "recursos/enemigo_diminuto_2.png"]

for imagen in imagenes_enemigos:
    lista_enemigos.append(pygame.image.load(imagen).convert())

# Cargar imagenes explosion colision disparos - enemigos
animacion_explosion = []

for i in range(9):
    archivo = "recursos/Explosion0{}.png".format(i)
    img = pygame.image.load(archivo).convert()
    img.set_colorkey(NEGRO)
    img_scale = pygame.transform.scale(img, (70,70))
    animacion_explosion.append(img_scale)

# Cargar sonidos
sonido_disparo = pygame.mixer.Sound("recursos/sonido_disparo.ogg")
sonido_explosion = pygame.mixer.Sound("recursos/explosion.wav")
sonido_powerup = pygame.mixer.Sound("recursos/powerup_sonido.mp3")
sonido_colision_enemigo_nave = pygame.mixer.Sound("recursos/colision_jugador_enemigo.mp3")
pygame.mixer.music.load("recursos/musica_juego.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(loops=-1)

# Ejecuccion juego
game_over = True
ejecutando = True
powerup_en_pantalla = False
puntuacion_maxima = 0


while ejecutando:
    if game_over:
        game_over = False
        powerup_en_pantalla = False
        all_sprites = pygame.sprite.Group()
        imagenes_enemigos = pygame.sprite.Group()
        disparos = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        puntos = 0
        color_puntos_pantalla = BLANCO
        color_barra_vida = VERDE

        dibuja_fondo()
        mostrar_pantalla_inicio()

        jugador = Jugador()
        all_sprites.add(jugador)
        for i in range(8):
            enemigo = Enemigos()
            all_sprites.add(enemigo)
            imagenes_enemigos.add(enemigo)

    reloj.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                jugador.disparar()
        elif jugador.vida <= 30 or (puntos % POWERUP_CADA_X_PUNTOS == 0 and jugador.vida < 100):
            if not powerup_en_pantalla:
                add_powerup()
                powerup_en_pantalla = True

    all_sprites.update()

    # Verificar colisiones - enemigos - disparo
    hits = pygame.sprite.groupcollide(imagenes_enemigos, disparos, True, True)
    for hit in hits:
        puntos += 10
        sonido_explosion.play()
        explosion = Explosion(hit.rect.center)
        all_sprites.add(explosion)
        enemigo = Enemigos()
        all_sprites.add(enemigo)
        imagenes_enemigos.add(enemigo)

    # Verificar colisiones - jugador - enemigos
    hits = pygame.sprite.spritecollide(jugador, imagenes_enemigos, True)
    for hit in hits:
        sonido_colision_enemigo_nave.play()
        jugador.vida -= 20
        puntos -= 5
        enemigo = Enemigos()
        all_sprites.add(enemigo)
        imagenes_enemigos.add(enemigo)
        if jugador.vida <= 0:
            game_over = True
            if puntos > puntuacion_maxima:
                puntuacion_maxima = puntos
            mostrar_pantalla_final(puntos,puntuacion_maxima)

    # Verificar colisiones entre el jugador y los powerups
    hits = pygame.sprite.spritecollide(jugador, powerups, True)
    for hit in hits:
        hit.aplicar_powerup(jugador)
        sonido_powerup.play()
        powerup_en_pantalla = False

    pantalla.blit(imagen_fondo, [0, 0])

    all_sprites.draw(pantalla)

    # Marcador
    if puntos > puntuacion_maxima:
        color_puntos_pantalla = VERDE
    dibujar_texto(pantalla, str(puntos), 40, ANCHO_PANTALLA // 2, 10, color_puntos_pantalla)

    # Barra vida
    if jugador.vida > 70:
        color_barra_vida = VERDE
    elif jugador.vida > 50:
        color_barra_vida = AMARILLO
    else:
        color_barra_vida = ROJO

    dibujar_barra_vida(pantalla, 5, 5, jugador.vida, color_barra_vida)

    pygame.display.flip()


#Salida del juego
pygame.quit()
