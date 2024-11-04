from math import sin, cos, radians, sqrt
import sys
import time
from random import choice, uniform, randint
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image  # Importa a biblioteca Pillow para texturas

# Variáveis globais
window_width = 800
window_height = 600

# Variáveis de controle da câmera
camera_mode = 0  # 0: primeira pessoa, 1 e 2: câmeras fixas
pos_x, pos_y, pos_z = 0.0, 1.0, 5.0
rot_y = 0.0
keys = {}

# Iluminação
light_on = True

# Lista de objetos na cena
objects = []

# Nome do objeto próximo
near_object_name = None

# Variáveis para animação
toro_rotation_angle = 0.0
bonus_animation_active = False
bonus_animation_start_time = None
bonus_animation_duration = 5  # Duração da animação de bônus em segundos

# Variáveis para pontuação e informações educativas
score = 0
last_collected_shape = None
educational_info = {
    'Cubo': 'O cubo tem 6 faces quadradas e 12 arestas iguais.',
    'Esfera': 'A esfera é um sólido perfeitamente redondo em três dimensões.',
    'Cone': 'O cone tem uma base circular e um vértice.',
    'Toro': 'O toro é uma superfície gerada pela rotação de um círculo em torno de um eixo.',
    'Teapot': 'O bule de Utah é um modelo padrão em computação gráfica.',
    'Dodecaedro': 'O dodecaedro regular tem 12 faces pentagonais.',
    'Casa': 'Uma casa típica tem uma base cúbica e um telhado em forma de pirâmide.',
}

# Estados do jogo
game_state = 'menu'  # Pode ser 'menu', 'playing', 'paused'

# Dicionário para texturas
textures = {}

# Variáveis para o Quiz
quiz_active = False
current_question = None

# Dicionário de perguntas para o quiz
quiz_questions = {
    'Cubo': {
        'question': 'Quantas faces tem um cubo?',
        'options': ['A) 4', 'B) 6', 'C) 8'],
        'answer': 'B',
    },
    'Esfera': {
        'question': 'Qual é a fórmula do volume de uma esfera?',
        'options': ['A) (4/3)πr³', 'B) πr²', 'C) 2πr'],
        'answer': 'A',
    },
    'Cone': {
        'question': 'Quantas arestas tem um cone?',
        'options': ['A) 1', 'B) 2', 'C) 0'],
        'answer': 'A',
    },
    'Teapot': {
        'question': 'O bule de Utah é famoso em que área?',
        'options': ['A) Matemática', 'B) Física', 'C) Computação Gráfica'],
        'answer': 'C',
    },
    'Dodecaedro': {
        'question': 'Quantas faces tem um dodecaedro regular?',
        'options': ['A) 12', 'B) 20', 'C) 30'],
        'answer': 'A',
    },
    'Toro': {
        'question': 'Um toro tem formato semelhante a um:',
        'options': ['A) Donut', 'B) Cubo', 'C) Cone'],
        'answer': 'A',
    },
    'Casa': {
        'question': 'Qual é o formato do telhado em uma casa típica?',
        'options': ['A) Cônico', 'B) Piramidal', 'C) Plano'],
        'answer': 'B',
    },
    'Cilindro': {
        'question': 'Qual é a fórmula do volume de um cilindro?',
        'options': ['A) πr²h', 'B) (1/3)πr²h', 'C) 2πr²'],
        'answer': 'A',
    },
    'Pirâmide': {
        'question': 'Quantas faces tem uma pirâmide de base quadrada?',
        'options': ['A) 4', 'B) 5', 'C) 6'],
        'answer': 'B',
    },
    'Octaedro': {
        'question': 'Um octaedro é composto por quais tipos de faces?',
        'options': ['A) Quadrados', 'B) Triângulos', 'C) Pentágonos'],
        'answer': 'B',
    },
}

# Classe para representar objetos na cena
class GameObject:
    def __init__(self, shape, color, position, size, composite=False):
        self.shape = shape  # 'Cubo', 'Esfera', 'Cone', etc.
        self.color = color
        self.position = position
        self.size = size
        self.collected = False
        self.composite = composite  # Indica se é um objeto composto
        self.collected_time = None  # Tempo em que o objeto foi coletado
        self.respawn_delay = 6  # Tempo para reaparecer (6 segundos)

    def respawn(self):
        possible_shapes = [
            'Cubo', 'Esfera', 'Cone', 'Toro', 'Teapot', 'Dodecaedro',
            'Cilindro', 'Pirâmide', 'Octaedro'
        ]
        composite_shapes = ['Casa']
        if randint(0, 4) == 0:  # 20% de chance de ser um objeto composto
            self.shape = choice(composite_shapes)
            self.composite = True
        else:
            self.shape = choice(possible_shapes)
            self.composite = False
        # Gera cores mais vivas (saturadas)
        self.color = (
            uniform(0.5, 1),
            uniform(0.5, 1),
            uniform(0.5, 1)
        )
        self.position = (uniform(-10, 10), 0.5, uniform(-15, -5))  # Nova posição aleatória
        self.size = uniform(0.5, 2)  # Novo tamanho
        self.collected = False
        self.collected_time = None

# Função para carregar texturas
def load_textures():
    global textures
    texture_files = {
        'chao': 'grass.jpg',
        'cubo': 'wood.jpg',
        'esfera': 'metal.jpg',
        'cone': 'stone.jpg',
        'toro': 'gold.jpg',
        'teapot': 'ceramic.jpg',
        'dodecaedro': 'marble.jpg',
        'casa': 'brick.jpg',
        # Adicione texturas para novos objetos se desejar
    }
    for key, filename in texture_files.items():
        try:
            image = Image.open(filename)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGB").tobytes()
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height,
                0, GL_RGB, GL_UNSIGNED_BYTE, img_data
            )
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            textures[key] = texture_id
        except FileNotFoundError:
            print(f"Arquivo de textura '{filename}' não encontrado.")
            textures[key] = 0

# Função para inicializar os objetos na cena
def init_objects():
    global objects
    # Objetos iniciais com cores mais vivas
    objects = [
        GameObject('Cubo', (1, 0, 0), (-3, 0.5, -5), 1),      # Cubo vermelho
        GameObject('Esfera', (0, 1, 0), (0, 0.5, -5), 1),     # Esfera verde
        GameObject('Cone', (0, 0, 1), (3, 0.5, -5), 1),       # Cone azul
        GameObject('Toro', (1, 1, 0), (0, 0.5, -8), 1),       # Toro amarelo giratório
        GameObject('Teapot', (1, 0, 1), (5, 0.5, -6), 1),     # Teapot rosa
        GameObject('Dodecaedro', (0, 1, 1), (-5, 0.5, -6), 1),# Dodecaedro ciano
    ]

    # Objeto composto (exemplo: casa)
    objects.append(
        GameObject('Casa', (0.8, 0.5, 0.2), (0, 0, -10), 2, composite=True)
    )

# Função para desenhar cada objeto
def draw_object(obj):
    global toro_rotation_angle
    glPushMatrix()
    glTranslatef(*obj.position)
    if obj.composite:
        draw_house(obj.size)
    else:
        glColor3f(*obj.color)  # Define a cor do objeto
        glBindTexture(GL_TEXTURE_2D, textures.get(obj.shape.lower(), 0))
        glEnable(GL_TEXTURE_2D)
        # Combina a cor com a textura para cores mais vivas
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        if obj.shape == 'Cubo':
            glutSolidCube(obj.size)
        elif obj.shape == 'Esfera':
            quad = gluNewQuadric()
            gluQuadricTexture(quad, GL_TRUE)
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluSphere(quad, obj.size / 2, 20, 20)
            gluDeleteQuadric(quad)
        elif obj.shape == 'Cone':
            quad = gluNewQuadric()
            gluQuadricTexture(quad, GL_TRUE)
            gluQuadricNormals(quad, GLU_SMOOTH)
            gluCylinder(quad, obj.size / 2, 0, obj.size, 20, 20)
            gluDeleteQuadric(quad)
        elif obj.shape == 'Toro':
            glRotatef(toro_rotation_angle, 0, 1, 0)
            glutSolidTorus(obj.size / 4, obj.size / 2, 20, 20)
        elif obj.shape == 'Teapot':
            glScalef(obj.size, obj.size, obj.size)
            glutSolidTeapot(1)
        elif obj.shape == 'Dodecaedro':
            glPushMatrix()
            glTranslatef(0, obj.size / 2, 0)
            glScalef(obj.size, obj.size, obj.size)
            glutSolidDodecahedron()
            glPopMatrix()
        # Adicione outros objetos aqui se desejar
        glDisable(GL_TEXTURE_2D)
    glPopMatrix()

# Função para desenhar um objeto composto (exemplo: casa)
def draw_house(size):
    # Base da casa
    glColor3f(1, 1, 1)  # Base branca
    glBindTexture(GL_TEXTURE_2D, textures.get('casa', 0))
    glEnable(GL_TEXTURE_2D)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glPushMatrix()
    glScalef(size, size, size)
    glutSolidCube(1)
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)

    # Telhado
    glColor3f(0.8, 0.2, 0.2)  # Telhado vermelho
    glPushMatrix()
    glTranslatef(0, size / 2, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(size * 1.1, size / 2, 4, 4)
    glPopMatrix()

# Função para desenhar o chão com textura
def draw_ground():
    glColor3f(1, 1, 1)  # Evita influência na textura
    glBindTexture(GL_TEXTURE_2D, textures.get('chao', 0))
    glEnable(GL_TEXTURE_2D)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glTexCoord2f(0, 0); glVertex3f(-20, 0, -20)
    glTexCoord2f(10, 0); glVertex3f(20, 0, -20)
    glTexCoord2f(10, 10); glVertex3f(20, 0, 20)
    glTexCoord2f(0, 10); glVertex3f(-20, 0, 20)
    glEnd()
    glDisable(GL_TEXTURE_2D)

# As demais funções permanecem as mesmas...

# Função para detecção de colisão
def check_collision():
    global objects, pos_x, pos_y, pos_z, bonus_animation_active, bonus_animation_start_time
    global score, last_collected_shape, quiz_active, current_question

    for obj in objects:
        if not obj.collected:
            dx = pos_x - obj.position[0]
            dy = pos_y - obj.position[1]
            dz = pos_z - obj.position[2]
            distance = sqrt(dx ** 2 + dy ** 2 + dz ** 2)
            if distance < obj.size:
                obj.collected = True
                obj.collected_time = time.time()
                score += 10  # Incrementa a pontuação
                last_collected_shape = obj.shape
                print(f"Você coletou um objeto: {obj.shape}")
                if obj.shape == 'Toro':
                    bonus_animation_active = True
                    bonus_animation_start_time = time.time()
                # Inicia o quiz se houver uma pergunta para este objeto
                question_data = quiz_questions.get(obj.shape)
                if question_data:
                    quiz_active = True
                    current_question = question_data

# Função para verificar proximidade
def check_proximity():
    global objects, pos_x, pos_y, pos_z, near_object_name
    proximity_distance = 2.5
    min_distance = float('inf')
    near_object_name = None

    for obj in objects:
        if not obj.collected:
            dx = pos_x - obj.position[0]
            dy = pos_y - obj.position[1]
            dz = pos_z - obj.position[2]
            distance = sqrt(dx ** 2 + dy ** 2 + dz ** 2)
            if distance < proximity_distance and distance < min_distance:
                min_distance = distance
                near_object_name = obj.shape

# Função para desenhar texto na tela
def draw_text(x, y, text):
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 1, 0)  # Cor amarela para o texto
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

# Função para desenhar o quiz
def draw_quiz():
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 1, 0)  # Cor amarela para o texto
    y = window_height / 2 + 60
    draw_text(50, y, current_question['question'])
    for option in current_question['options']:
        y -= 30
        draw_text(70, y, option)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

# Função para desenhar a animação de bônus
def draw_bonus_animation():
    glPushMatrix()
    glTranslatef(pos_x, pos_y + 1.0, pos_z)
    glRotatef(toro_rotation_angle * 5, 0, 1, 0)
    glColor3f(1, 1, 0)  # Amarelo brilhante
    glutSolidSphere(0.5, 20, 20)
    glColor3f(1, 0.5, 0)  # Laranja
    glutWireSphere(0.7, 10, 10)
    glPopMatrix()

# Função para desenhar o menu
def display_menu():
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glColor3f(1, 1, 0)  # Cor amarela para o texto
    draw_text(window_width / 2 - 100, window_height / 2 + 40, "Bem-vindo ao Jogo Educativo!")
    draw_text(window_width / 2 - 80, window_height / 2 + 10, "Pressione ENTER para iniciar")
    draw_text(window_width / 2 - 60, window_height / 2 - 20, "Pressione ESC para sair")
    glEnable(GL_LIGHTING)

# Função de inicialização
def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_TEXTURE_2D)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.5, 0.7, 1.0, 1.0)
    init_objects()
    load_textures()

    # Configura a luz fixa (GL_LIGHT0)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 10, 0, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])

    # Configura a luz móvel (GL_LIGHT1)
    glEnable(GL_LIGHT1)
    glLightfv(GL_LIGHT1, GL_AMBIENT, [0.1, 0.1, 0.1, 1])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.6, 0.6, 0.6, 1])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [1, 1, 1, 1])

# Função para redimensionar a janela
def reshape(w, h):
    global window_width, window_height
    window_width = w
    window_height = h
    glViewport(0, 0, w, h)

# Função para desenhar a cena
def display():
    global toro_rotation_angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if game_state == 'menu':
        display_menu()
    elif game_state == 'playing':
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, window_width / window_height, 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Configura as câmeras
        if camera_mode == 0:
            center_x = pos_x + sin(rot_y)
            center_y = pos_y - 0.2
            center_z = pos_z - cos(rot_y)
            gluLookAt(pos_x, pos_y, pos_z,
                      center_x, center_y, center_z,
                      0, 1, 0)
        elif camera_mode == 1:
            gluLookAt(0, 15, 0, 0, 0, -5, 0, 1, 0)
        elif camera_mode == 2:
            gluLookAt(15, 5, 0, 0, 0, -5, 0, 1, 0)

        # Atualiza posição da luz móvel
        if light_on:
            glEnable(GL_LIGHT1)
            glLightfv(GL_LIGHT1, GL_POSITION, [pos_x, pos_y, pos_z, 1])
        else:
            glDisable(GL_LIGHT1)

        # Desenha o chão com textura
        draw_ground()

        # Desenha os objetos
        for obj in objects:
            if not obj.collected:
                draw_object(obj)

        # Atualiza o ângulo de rotação do toro
        toro_rotation_angle += 2.0

        # Desenha a animação de bônus se ativa
        if bonus_animation_active:
            draw_bonus_animation()

        # Desenha o texto de identificação e pontuação
        y_offset = window_height - 30
        glColor3f(1, 1, 0)  # Cor amarela para o texto
        if near_object_name is not None:
            draw_text(10, y_offset, f"Você está próximo de um(a): {near_object_name}")
            y_offset -= 20
        draw_text(10, y_offset, f"Pontuação: {score}")
        y_offset -= 20
        if last_collected_shape is not None:
            info = educational_info.get(last_collected_shape, '')
            draw_text(10, y_offset, f"Info: {info}")

        # Desenha o quiz se ativo
        if quiz_active:
            draw_quiz()

    glutSwapBuffers()

# Função de atualização
def update(value):
    global bonus_animation_active, bonus_animation_start_time

    if game_state == 'playing':
        check_collision()
        check_proximity()
        move_camera()

        # Verifica se algum objeto deve reaparecer
        current_time = time.time()
        for obj in objects:
            if obj.collected and obj.collected_time is not None:
                if current_time - obj.collected_time >= obj.respawn_delay:
                    obj.respawn()

        # Verifica se a animação de bônus deve ser desativada
        if bonus_animation_active and bonus_animation_start_time is not None:
            if current_time - bonus_animation_start_time >= bonus_animation_duration:
                bonus_animation_active = False
                bonus_animation_start_time = None

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # Aproximadamente 60 FPS

# Função para mover a câmera em primeira pessoa
def move_camera():
    global pos_x, pos_y, pos_z, rot_y, keys

    speed = 0.1
    if keys.get('w', False):
        pos_x += sin(rot_y) * speed
        pos_z -= cos(rot_y) * speed
    if keys.get('s', False):
        pos_x -= sin(rot_y) * speed
        pos_z += cos(rot_y) * speed
    if keys.get('a', False):
        rot_y -= radians(2)
    if keys.get('d', False):
        rot_y += radians(2)

# Função para lidar com teclas normais
def keyboard(key, x, y):
    global keys, light_on, camera_mode, game_state, quiz_active, current_question, score, last_collected_shape

    key_char = key.decode('utf-8').lower()
    keys[key_char] = True

    if key_char == '\x1b':  # ESC
        glutLeaveMainLoop()
    elif key_char == '\r':  # ENTER
        if game_state == 'menu':
            game_state = 'playing'
    elif quiz_active:
        answer = key_char.upper()
        if answer == current_question['answer']:
            print("Resposta correta!")
            score += 5  # Bônus por acertar
        else:
            print("Resposta incorreta.")
        quiz_active = False
        current_question = None
        last_collected_shape = None  # Resetar para não mostrar o painel novamente
    elif game_state == 'playing':
        if key_char == '1':
            camera_mode = 0
            print("Câmera em primeira pessoa ativada.")
        elif key_char == '2':
            camera_mode = 1
            print("Câmera fixa 1 ativada.")
        elif key_char == '3':
            camera_mode = 2
            print("Câmera fixa 2 ativada.")
        elif key_char == 'l':
            light_on = not light_on
            estado = "ligada" if light_on else "desligada"
            print(f"Luz móvel {estado}.")

# Função para lidar com o evento de tecla solta
def keyboard_up(key, x, y):
    global keys
    key_char = key.decode('utf-8').lower()
    keys[key_char] = False

# Função principal
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Jogo Educativo - Reconhecimento de Formas e Cores")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutTimerFunc(0, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
