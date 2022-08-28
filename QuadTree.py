from Poligonos import Polygon
from Ponto import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class QuadTree:
     def __init__(self, x0, x1, y0, y1, maximo=10):
          self.tot = 0
          self.maximo = maximo
          self.x0 = x0 
          self.x1 = x1 
          self.y0 = y0
          self.y1 = y1 
          self.vet = []
          self.isFull = False
          self.isEmpty = True
          self.topLeft = None
          self.topRight = None
          self.bottomLeft = None
          self.bottomRight = None

     def divide(self):
          self.isFull = True
          x0, x1 = self.x0, self.x1
          y0, y1 = self.y0, self.y1
          meioX = int(math.floor((x0+x1)/2))
          meioY = int(math.floor((y0+y1)/2))

          self.topLeft     = QuadTree(x0, meioX, y0, meioY, self.maximo)
          self.topRight    = QuadTree(meioX+1, x1, y0, meioY, self.maximo)
          self.bottomLeft  = QuadTree(x0, meioX, meioY+1, y1, self.maximo)
          self.bottomRight = QuadTree(meioX+1, x1, meioY+1, y1, self.maximo)

     def checaDentro(self, envelope):
          xmax = envelope[0]
          xmin = envelope[1]
          ymax = envelope[2]
          ymin = envelope[3]

          if (
              ((xmax >= self.x0 and xmax <= self.x1) or
              (xmin >= self.x0 and xmin <= self.x1)) and
              ((ymax >= self.y0 and ymax <= self.y1) or
              (ymin >= self.y0 and ymin <= self.y1)) or
              
              ((self.x0 >= xmin and self.x1 <= xmax) or
              (self.y0 >= ymin and self.y1 <= ymax))


             ): return True
          
          return False

     def pontosNoEnvelope(self, envelope):
          pontosDentro = []
          for p in self.vet:
               imprimePonto(p, (1,0,1))
               if estaDentroEnvelope(p, envelope):
                    pontosDentro.append(p)
                    
          if self.topLeft == None: return pontosDentro

          if self.topLeft.checaDentro(envelope): pontosDentro += self.topLeft.pontosNoEnvelope(envelope)
          if self.topRight.checaDentro(envelope): pontosDentro += self.topRight.pontosNoEnvelope(envelope)
          if self.bottomLeft.checaDentro(envelope): pontosDentro += self.bottomLeft.pontosNoEnvelope(envelope)
          if self.bottomRight.checaDentro(envelope): pontosDentro += self.bottomRight.pontosNoEnvelope(envelope)

          return pontosDentro

     def poligonos(self, altura = 0):
          p0 = Ponto(self.x1, self.y0, 0)
          p1 = Ponto(self.x0, self.y0, 0)
          p2 = Ponto(self.x0, self.y1, 0)
          p3 = Ponto(self.x1, self.y1, 0)
          poligono = Polygon()
          poligono.insereVerticeP(p0)
          poligono.insereVerticeP(p1)
          poligono.insereVerticeP(p2)
          poligono.insereVerticeP(p3)
          quadrados = [(poligono, altura)]

          if self.topLeft == None: return quadrados

          quadrados += self.topLeft.poligonos(altura+1)
          quadrados += self.topRight.poligonos(altura+1)
          quadrados += self.bottomLeft.poligonos(altura+1)
          quadrados += self.bottomRight.poligonos(altura+1)

          return quadrados

     def imprime(self, altura = 0, tabs=''):
          pos = ((self.x0,self.x1),(self.y0,self.y1))
          print(tabs, pos, '  ', self.isFull, len(self.vet))
          if(self.isFull):
               self.topLeft.imprime(altura+1, tabs+'   ')
               self.topRight.imprime(altura+1, tabs+'   ')
               self.bottomLeft.imprime(altura+1, tabs+'   ')
               self.bottomRight.imprime(altura+1, tabs+'   ')

     def add(self, ponto: Ponto, path = []):
          if not(ponto.x >= self.x0
             and ponto.x <= self.x1 
             and ponto.y >= self.y0
             and ponto.y <= self.y1): return False

          if len(self.vet) < self.maximo:
               self.isEmpty = False
               self.vet.append((ponto))
               self.tot += 1
               return True

          if self.topLeft == None: self.divide()

          if(
               self.topLeft.add(ponto, path + ['tl']) or 
               self.topRight.add(ponto, path + ['tr']) or 
               self.bottomLeft.add(ponto, path + ['bl']) or 
               self.bottomRight.add(ponto, path + ['br'])
            ): 
               self.tot += 1
               return True

          return False
     

     def contaPontos(self, triangulo):
          tot = 0
          tot_Quad = 0
          p1, p2, p3 = triangulo
          arestas = (
               (p1, p2),
               (p2, p3),
               (p3, p1)
          )
          vetores = getArestasDoTriangulo((p1,p2,p3))

          for p in self.vet:
               imprimePonto(p, (1,0,1))
               if estaDentro2(p, vetores, arestas):
                    imprimePonto(p, (1,0,0))
                    tot +=1
               else: tot_Quad += 1
               

               # tot +=1

          if self.topLeft == None:
               return tot, tot_Quad


          if tringuloDentroRetangulo(triangulo, self.topLeft):
               result = self.topLeft.contaPontos(triangulo)
               tot += result[0]
               tot_Quad += result[1]

          if tringuloDentroRetangulo(triangulo, self.topRight):
               result = self.topRight.contaPontos(triangulo)
               tot += result[0]
               tot_Quad += result[1]

          if tringuloDentroRetangulo(triangulo, self.bottomLeft):
               result = self.bottomLeft.contaPontos(triangulo)
               tot += result[0]
               tot_Quad += result[1]

          if tringuloDentroRetangulo(triangulo, self.bottomRight):
               result = self.bottomRight.contaPontos(triangulo)
               tot += result[0]
               tot_Quad += result[1]



          return tot, tot_Quad
          

def estaDentro2(ponto : Ponto, vetores, arestas):
    x,y,z = ponto.x, ponto.y, ponto.z
    dentro = True

    for j in range(3):
        pI = arestas[j][0]
        vB = (pI.x - x, pI.y - y, pI.z - z)
        if not getZDirection(vetores[j], vB): dentro = False
        
    return dentro

def getZDirection(v1, v2):
    z = v1[0]*v2[1] - v1[1]*v2[0]
    return True if z>= 0 else False


def estaDentroEnvelope(ponto: Ponto, envelope):
    dentro = False
    if(ponto.x <= envelope[0] and ponto.x >= envelope[1]):
        if(ponto.y <= envelope[2] and ponto.y >= envelope[3]):
            dentro = True
    return dentro

def imprimePonto(ponto: Ponto, cor):
    r,g,b = cor
    glBegin(GL_POINTS);
    glColor3f(r,g,b)
    glVertex3f(ponto.x,ponto.y,ponto.z)
    glEnd()


def getArestasDoTriangulo(pontos):
     a1 = (pontos[0], pontos[1])
     a2 = (pontos[1], pontos[2])
     a3 = (pontos[2], pontos[0])
     # a1,a2,a3 = pontos
     v1 = (a1[1].x - a1[0].x, a1[1].y - a1[0].y, a1[1].z - a1[0].z) 
     v2 = (a2[1].x - a2[0].x, a2[1].y - a2[0].y, a2[1].z - a2[0].z) 
     v3 = (a3[1].x - a3[0].x, a3[1].y - a3[0].y, a3[1].z - a3[0].z) 
     return v1,v2,v3

def getZDirection(v1, v2):
    z = v1[0]*v2[1] - v1[1]*v2[0]
    return True if z>= 0 else False

def estaDentro(ponto, vetores, triangulo):
     # dentro = True
     x,y,z = ponto.x, ponto.y, ponto.z
     for vA, pI in zip(vetores, triangulo):
          vB = (pI.x - x, pI.y - y, pI.z - z)
          if not getZDirection(vA, vB): return False

     return True
        

def quadradoDentroDoTriangulo(quadrado, vetores, triangulo):
     for ponto in quadrado:
          if estaDentro(ponto, vetores, triangulo): return True
     return False

def tringuloDentroRetangulo(triangulo, retangulo : QuadTree):
     
     xMin = retangulo.x0
     xMax = retangulo.x1
     yMin = retangulo.y0
     yMax = retangulo.y1
     p0 = Ponto(xMin, yMin)
     p1 = Ponto(xMax, yMin)
     p2 = Ponto(xMin, yMax)
     p3 = Ponto(xMax, yMax)

     t = Polygon()
     t.insereVerticeP(p0)
     t.insereVerticeP(p1)
     t.insereVerticeP(p3)
     t.insereVerticeP(p2)
     t.desenhaPoligonoComCor(6)
# p0---------------p1
# |                |
# |                |
# |                |
# |                |
# |                |
# |                |
# p2---------------p3

     lTriangulo = [
          (triangulo[0], triangulo[1]),
          (triangulo[1], triangulo[2]),
          (triangulo[2], triangulo[0])
     ]

     t2 = Polygon()
     t2.insereVerticeP(triangulo[0])
     t2.insereVerticeP(triangulo[1])
     t2.insereVerticeP(triangulo[2])
     t2.desenhaPoligonoComCor(6)
     
     lRetangulo = [
          (p0, p1),
          (p1, p3),
          (p3, p2),
          (p2, p0)
     ]

     for lT in lTriangulo:
          for lR in lRetangulo:
               if HaInterseccao(lT[0], lT[1], lR[0], lR[1]): return True
                    # return True
                    # t3 = Polygon()
                    # t3.insereVerticeP(lT[0])
                    # t3.insereVerticeP(lT[1])
                    # t4 = Polygon()
                    # t4.insereVerticeP(lR[0])
                    # t4.insereVerticeP(lR[1])

                    # t3.desenhaPoligonoComCor(2)
                    # t4.desenhaPoligonoComCor(2)


     # return False
     
     for p in triangulo:
          if p.x >= xMin and p.x <= xMax and p.y >= yMin and p.y <= yMax: return True
          # print(p.x, p.y)
     
     # v1, v2, v3 = getArestasDoTriangulo(triangulo)
     quadrado = (p0, p1, p2, p3)
     vetores = getArestasDoTriangulo(triangulo)

     if quadradoDentroDoTriangulo(quadrado, vetores, triangulo): return True

     return False