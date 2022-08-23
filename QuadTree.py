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
    glEnd();