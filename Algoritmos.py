from Ponto import Ponto


def getZDirection(v1, v2):
    z = v1[0]*v2[1] - v1[1]*v2[0]
    return True if z>= 0 else False


def estaDentro(ponto : Ponto, vetores, vertices):
    x,y,z = ponto.x, ponto.y, ponto.z
    dentro = True

    for j in range(3):
        pI = vertices[j]
        vB = (pI.x - x, pI.y - y, pI.z - z)
        if not getZDirection(vetores[j], vB): dentro = False
        
    return dentro


def getVetoresDoTriangulo(pontos):
    a1 = (pontos[0], pontos[1])
    a2 = (pontos[1], pontos[2])
    a3 = (pontos[2], pontos[0])
    
    v1 = (a1[1].x - a1[0].x, a1[1].y - a1[0].y, a1[1].z - a1[0].z) 
    v2 = (a2[1].x - a2[0].x, a2[1].y - a2[0].y, a2[1].z - a2[0].z) 
    v3 = (a3[1].x - a3[0].x, a3[1].y - a3[0].y, a3[1].z - a3[0].z) 
    return v1,v2,v3


