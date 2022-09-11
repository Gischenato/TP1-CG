
#? ***********************************************************************************
#?   PontosNoTriangulo.py
#?       Autor: Márcio Sarroglia Pinho
#?       pinho@pucrs.br
#?   Este programa exibe um conjunto de Pontos e um triangulo em OpenGL
#?   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#?   http://pyopengl.sourceforge.net/documentation/index.html
#?
#?   Sugere-se consultar também as páginas listadas
#?   a seguir:
#?   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#?   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#?
#?   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#?   conforme a descrição que está nestes links:
#?   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#?   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#?   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
#? ***********************************************************************************
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Poligonos import *
import random

from QuadTree import QuadTree
from Metodos import *

testando = Polygon()

#? ***********************************************************************************
#? Variaveis que controlam o triangulo do campo de visao
tam_tela = 600
tam_quad_tree = 100
qntPontos = 50000
calculo = 0
campo_de_visao = 0.25
AnguloDoCampoDeVisao=0.0

PontosDoCenario = Polygon()
CampoDeVisao = Polygon()
TrianguloBase = Polygon()
Envelope = Polygon()
Envelope.insereVertice(0, 0, 0)
Envelope.insereVertice(0, 0, 0)
Envelope.insereVertice(0, 0, 0)
Envelope.insereVertice(0, 0, 0)
quadTree = QuadTree(0, tam_tela, 0, tam_tela, maximo=tam_quad_tree)

PosicaoDoCampoDeVisao = Ponto

mostrar_pontos = True
mostrar_envelope = True
mostrar_quad_tree = False
mostrar_cores = True
mostra_poligonos_quad_tree = False
flagDesenhaEixos = False

poligonos_quadtree = []

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()
Tamanho = Ponto()
Meio = Ponto()

PontoClicado = Ponto()


#? **********************************************************************
#? GeraPontos(int qtd)
#?      Metodo que gera pontos aleatorios no intervalo [Min..Max]
#? **********************************************************************
def GeraPontos(qtd, Min: Ponto, Max: Ponto):
    global PontosDoCenario, poligonos_quadtree
    Escala = Ponto()
    Escala = (Max - Min) * (1.0/1000.0)
    tot = 0
    
    for _ in range(qtd):
        x = random.randint(0, 1000)
        y = random.randint(0, 1000)
        x = x * Escala.x + Min.x
        y = y * Escala.y + Min.y
        P = Ponto(x,y)
        while True:
            if quadTree.add(P): break
            tot += 1
            # print('Movendo ', P.x, P.y)
            P.x = P.x + 1
            if quadTree.add(P): break
            P.y = P.y + 1
            if P.x >= tam_tela: P.x = 1
            if P.y >= tam_tela: P.y = 1
        PontosDoCenario.insereVerticeP(P)
    quadTree.imprime()
    print(f'{tot} pontos movidos')
    poligonos_quadtree = quadTree.poligonos()
    print(quadTree.tot)

def recriaQuadTree(novo_tam):
    global tam_tela, quadTree, poligonos_quadtree
    quadTree = QuadTree(0, tam_tela, 0, tam_tela, maximo=novo_tam)
    for i in range(PontosDoCenario.getNVertices()):
        ponto : Ponto = PontosDoCenario.getRealVertice(i)
        while True:
            if quadTree.add(ponto): break
            # print('Movendo ', P.x, P.y)
            ponto.x = ponto.x + 1
            if quadTree.add(ponto): break
            ponto.y = ponto.y + 1
            if ponto.x >= tam_tela: ponto.x = 1
            if ponto.y >= tam_tela: ponto.y = 1


    poligonos_quadtree = quadTree.poligonos()
    print("NOVA QUAD TREE CRIADA")


#? **********************************************************************
#?  CriaTrianguloDoCampoDeVisao()
#?  Cria um triangulo a partir do vetor (1,0,0), girando este vetor
#?  em 45 e -45 graus.
#?  Este vetor fica armazenado nas variáveis "TrianguloBase" e
#?  "CampoDeVisao"
#? **********************************************************************
def CriaTrianguloDoCampoDeVisao():
    global TrianguloBase, CampoDeVisao

    vetor = Ponto(1,0,0)

    TrianguloBase.insereVertice(0,0,0)
    CampoDeVisao.insereVertice(0,0,0)
    
    vetor.rotacionaZ(45)
    TrianguloBase.insereVertice (vetor.x,vetor.y, vetor.z)
    CampoDeVisao.insereVertice (vetor.x,vetor.y, vetor.z)
    
    vetor.rotacionaZ(-90)
    TrianguloBase.insereVertice (vetor.x,vetor.y, vetor.z)
    CampoDeVisao.insereVertice (vetor.x,vetor.y, vetor.z)


#? ***********************************************************************************
#? void PosicionaTrianguloDoCampoDeVisao()
#?  Posiciona o campo de visão na posicao PosicaoDoCampoDeVisao,
#?  com a orientacao "AnguloDoCampoDeVisao".
#?  O tamanho do campo de visão eh de 25% da largura da janela.
#? **********************************************************************
def PosicionaTrianguloDoCampoDeVisao():
    global Tamanho, CampoDeVisao, PosicaoDoCampoDeVisao, TrianguloBase
    global AnguloDoCampoDeVisao, campo_de_visao


    tam_tela = Tamanho.x * campo_de_visao
    temp = Ponto()
    for i in range(TrianguloBase.getNVertices()):
        temp = TrianguloBase.getVertice(i)
        temp.rotacionaZ(AnguloDoCampoDeVisao)
        CampoDeVisao.alteraVertice(i, PosicaoDoCampoDeVisao + temp*tam_tela)


def AvancaCampoDeVisao(distancia):
    global PosicaoDoCampoDeVisao, AnguloDoCampoDeVisao
    vetor = Ponto(1,0,0)
    vetor.rotacionaZ(AnguloDoCampoDeVisao)
    PosicaoDoCampoDeVisao = PosicaoDoCampoDeVisao + vetor * distancia

#? ***********************************************************************************
#?
#? ***********************************************************************************
def init():
    global PosicaoDoCampoDeVisao, AnguloDoCampoDeVisao, tam_tela

    # Define a cor do fundo da tela (AZUL)
    glClearColor(0, 0, 1, 1)
    global Min, Max, Meio, Tamanho

    GeraPontos(qntPontos, Ponto(0,0), Ponto(tam_tela,tam_tela))
    Min, Max = PontosDoCenario.getLimits()
    #Min, Max = PontosDoCenario.LePontosDeArquivo("PoligonoDeTeste.txt")

    Meio = (Max+Min) * 0.5 # Ponto central da janela
    Tamanho = (Max - Min) # Tamanho da janela em X,Y

    # Ajusta variaveis do triangulo que representa o campo de visao
    PosicaoDoCampoDeVisao = Meio
    AnguloDoCampoDeVisao = 0

    # Cria o triangulo que representa o campo de visao
    CriaTrianguloDoCampoDeVisao()
    PosicionaTrianguloDoCampoDeVisao()
    
#? ***********************************************************************************
#?
#? ***********************************************************************************
def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

#? ***********************************************************************************
#?
#? ***********************************************************************************
def DesenhaEixos():
    global Min, Max, Meio

    glBegin(GL_LINES)
    # eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    # eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()

#? ***********************************************************************************
def reshape(w,h):
    global Min, Max

    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

#? ***********************************************************************************
#! -----------------------------------------------------------------------------------
def display():
    global PontoClicado, flagDesenhaEixos, mostrar_quad_tree
    global mostrar_envelope, poligonos_quadtree, mostrar_pontos, testando

    # PontosDoCenario = contaPontosNoTriangulo()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glColor3f(0.0, 1.0, 0.0)

    if mostrar_quad_tree:
        desenhaQuadTree()
    if (flagDesenhaEixos):
        glLineWidth(1)
        glColor3f(1,1,1); # R, G, B  [0..1]
        DesenhaEixos()

    if mostrar_pontos:
        glPointSize(1.5);
        # glColor3f(1,1,1) # R, G, B  [0..1]
        PontosDoCenario.desenhaVertices(color=(0,0,0))
    
    testando.desenhaPoligonoComCor(6)

    glLineWidth(3)
    glColor3f(1,0,0) # R, G, B  [0..1]
    CampoDeVisao.desenhaPoligono(color=(1,0,0))
    if calculo == 1:
        contaPontosNoTriangulo()
        mostrar_envelope = False
    elif calculo == 2:
        contaPontosNoTrianguloEnvelope()
    elif calculo == 3:
        contaPontosQuadTree()
        mostrar_envelope = False

    if mostrar_envelope:
        Envelope.desenhaPoligono(color=(0,1,0))

    glutSwapBuffers()

#* -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
def desenhaQuadTree():
    for x in reversed(poligonos_quadtree):
        x[0].desenhaPoligonoComCor(x[1])
#*********************************************************************************** 
#***********************************************************************************

def getVetoresDoTriangulo(arestas):
    a1,a2,a3 = arestas

    v1 = (a1[1].x - a1[0].x, a1[1].y - a1[0].y, a1[1].z - a1[0].z) 
    v2 = (a2[1].x - a2[0].x, a2[1].y - a2[0].y, a2[1].z - a2[0].z) 
    v3 = (a3[1].x - a3[0].x, a3[1].y - a3[0].y, a3[1].z - a3[0].z) 

    return v1,v2,v3

def contaPontosNoTriangulo():
    vetores = getVetoresDoTriangulo(CampoDeVisao.getAresta(x) for x in range(3))
    vertices = list(CampoDeVisao.getVertice(x) for x in range(3))
    dentro = 0
    fora = 0

    for i in range(PontosDoCenario.getNVertices()):
        ponto : Ponto = PontosDoCenario.getRealVertice(i)
        if estaDentro(ponto, vetores, vertices): 
            dentro+=1
            ponto.set(color=(0,0,0)) #PONTO FICA VERMELHO
            imprimePonto(ponto, (1,0,0))
        else:
            ponto.set(color=(0,0,0)) #PONTO FICA PRETO
            fora+=1
    print(f'Pontos dentro: {dentro}  -> Pontos fora: {fora}')
#*********************************************************************************** 
#Envelope
#*********************************************************************************** 
def calculaEnvelope():
    v1,v2,v3 = (CampoDeVisao.getRealVertice(x) for x in range(0,3))
    menorX, maiorX, menorY, maiorY = v1.x, v1.x, v1.y, v1.y
    maiorX = max(v1.x, v2.x, v3.x)
    menorX = min(v1.x, v2.x, v3.x)
    maiorY = max(v1.y, v2.y, v3.y)
    menorY = min(v1.y, v2.y, v3.y)

    p0 = Ponto(maiorX, menorY, 0)
    p1 = Ponto(menorX, menorY, 0)
    p2 = Ponto(menorX, maiorY, 0)
    p3 = Ponto(maiorX, maiorY, 0)

    Envelope.alteraVertice(0, p0)
    Envelope.alteraVertice(1, p1)
    Envelope.alteraVertice(2, p2)
    Envelope.alteraVertice(3, p3)
    return maiorX, menorX, maiorY, menorY


def estaDentroEnvelope(ponto: Ponto):
    envelope = calculaEnvelope()
    
    dentro = False
    if(ponto.x <= envelope[0] and ponto.x >= envelope[1]):
        if(ponto.y <= envelope[2] and ponto.y >= envelope[3]):
            dentro = True
    return dentro

def contaPontosNoTrianguloEnvelope():
    vetores = getVetoresDoTriangulo(CampoDeVisao.getAresta(x) for x in range(3))
    vertices = list(CampoDeVisao.getVertice(x) for x in range(3))
    dentro = 0
    dentroEnvelope = 0
    fora = 0
    foraEnvelope = 0

    for i in range(PontosDoCenario.getNVertices()):
        ponto : Ponto = PontosDoCenario.getRealVertice(i)
        if estaDentroEnvelope(ponto): 
            dentroEnvelope+=1
            if estaDentro(ponto, vetores, vertices):
                dentro+=1
                imprimePonto(ponto, (1,0,0)) # Ponto fica vermelho
            elif mostrar_envelope: 
                imprimePonto(ponto, (0,1,1)) # Ponto fica ciano
                fora+=1
            else:
                fora += 1
        else:
            fora += 1
            foraEnvelope+=1

    print(f'Pontos dentro do envelope: {dentroEnvelope}  -> Pontos fora do envelope: {foraEnvelope}')
    print(f'Pontos dentro: {dentro}  -> Pontos fora: {fora}')
# **********************************************************************************
#* QuadTree
# **********************************************************************************
def contaPontosQuadTree():
    vetores = list(CampoDeVisao.getRealVertice(x) for x in range(3))
    dentro = quadTree.contaPontos(vetores)

    dentro_QuadTree = dentro[1]
    dentro = dentro[0]
    fora = qntPontos - dentro
    
    print(f'Pontos dentro: {dentro}  -> Pontos fora: {fora}  |  quadTree: {dentro_QuadTree}')
# **********************************************************************************
# **********************************************************************************
#? **************************************************////*********************************
#? The function called whenever a key is pressed. Note the use of Python tuples to pass in: (key, x, y)
#? ESCAPE = '\033'
#? ***********************************************************************************
ESCAPE = b'\x1b'
def keyboard(*args):
    global flagDesenhaEixos, campo_de_visao, calculo, quadTree
    global mostrar_pontos, mostrar_envelope, mostrar_quad_tree

    global testando
    # print (args,' ts')
    # If escape is pressed, kill everything.
    # if args[0] == b'a':
    #     print(CampoDeVisao.getLimits())
    #     print(TrianguloBase.getLimits())
    #     PosicionaTrianguloDoCampoDeVisao()
    if args[0] == b'q' or args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'z':
        triangulo = [CampoDeVisao.getVertice(x) for x in range(3)]
        # for t in triangulo:
            # print((t.x, t.y))
        p0 = Ponto(0, 0)
        p1 = Ponto(300, 300)
        print(HaInterseccao(triangulo[0], triangulo[1], p0, p1))
        testando = Polygon()
        testando.insereVerticeP(p0)
        testando.insereVerticeP(p1)
        testando.desenhaPoligono()

    if args[0] == b'0': 
        calculo = 0
    if args[0] == b'1': 
        calculo = 1
    if args[0] == b'2':
        calculo = 2
        mostrar_envelope = True
    if args[0] == b'3': 
        calculo = 3
    if args[0] == b';':
        novo_tam = int(input('Novo tamanho'))
        recriaQuadTree(novo_tam)
    if args[0] == b'd': 
        mostrar_quad_tree = not mostrar_quad_tree
    if args[0] == b'h':
        campo_de_visao += .01
        PosicionaTrianguloDoCampoDeVisao()
    if args[0] == b'j':
        campo_de_visao -= .01
        PosicionaTrianguloDoCampoDeVisao()
    if args[0] == b'p':
        # PontosDoCenario.imprimeVertices()
        mostrar_pontos = not mostrar_pontos
    if args[0] == b'i':
        quadTree.troca()
    if args[0] == b' ':
        flagDesenhaEixos = not flagDesenhaEixos
    if args[0] == b'e':
        mostrar_envelope = not mostrar_envelope

    # Forca o redesenho da tela
    glutPostRedisplay()
#? **********************************************************************
#?  arrow_keys ( a_keys: int, x: int, y: int )   
#? **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    global AnguloDoCampoDeVisao, TrianguloBase

    # print ("Tecla:", a_keys)
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        AvancaCampoDeVisao(2)
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        AvancaCampoDeVisao(-2)
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        AnguloDoCampoDeVisao = AnguloDoCampoDeVisao + 2
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        AnguloDoCampoDeVisao = AnguloDoCampoDeVisao - 2

    PosicionaTrianguloDoCampoDeVisao()

    glutPostRedisplay()

#? ***********************************************************************************
#?
#? ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # universo definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

#? ***********************************************************************************
#?
#? ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return


#? ***********************************************************************************
#? Programa Principal
#? ***********************************************************************************

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA)
    # Define o tamanho inicial da janela grafica do programa
    glutInitWindowSize(tam_tela, tam_tela)
    glutInitWindowPosition(100, 100)
    wind = glutCreateWindow("Pontos no Triangulo")
    glutDisplayFunc(display)
    # glutIdleFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(arrow_keys)
    glutMouseFunc(mouse)
    init()
    
    try:
        # main()
        glutMainLoop()
    except SystemExit:
        pass

#! =====================================================================================

main()