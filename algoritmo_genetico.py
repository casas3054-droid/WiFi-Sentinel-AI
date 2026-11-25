"""Inteligencia artificial evolutiva: evaluación y operadores genéticos."""
import random
from collections import Counter
from simulacion import BASE, calcular_riesgo

# Parámetros de la evolución genética
POBLACION, GENERACIONES = 50, 100
PC, PM = .90, .10

def resumir(datos):
    return Counter(datos)


def metricas(c, datos):
    """Datos agregados (vector, etiqueta): frecuencia. ALTO es la predicción positiva."""
    vp = fp = vn = fn = 0
    for (v,y), cantidad in datos.items():
        positivo = calcular_riesgo(v,c) >= c[5]
        if positivo and y: vp += cantidad
        elif positivo: fp += cantidad
        elif y: fn += cantidad
        else: vn += cantidad
    precision = vp/(vp+fp) if vp+fp else 0.0
    recall = vp/(vp+fn) if vp+fn else 0.0
    f1 = 2*vp/(2*vp+fp+fn) if 2*vp+fp+fn else 0.0
    fpr = fp/(fp+vn) if fp+vn else 0.0
    return dict(vp=vp,fp=fp,vn=vn,fn=fn,precision=precision,recall=recall,f1=f1,fpr=fpr)

# 3. Algoritmo genético: población, fitness, selección, cruce, mutación, sustitución.
def reparar(c):
    w = tuple(max(1,min(5,int(x))) for x in c[:5])
    return w + (max(4,min(12,sum(w),int(c[5]))),)


def individuo(rng):
    return reparar([rng.randint(1,5) for _ in range(5)] + [rng.randint(4,12)])


def cruzar(a,b,rng):
    if rng.random() >= PC:
        return a,b,None
    k = rng.randint(1,5)
    return reparar(a[:k]+b[k:]), reparar(b[:k]+a[k:]), k


def mutar(c,rng):
    if rng.random() >= PM:
        return c,None
    i = rng.randrange(6)
    opciones = range(1,6) if i<5 else range(4,min(12,sum(c[:5]))+1)
    nuevo = list(c)
    posibles = [x for x in opciones if x != c[i]]
    if not posibles: return c,None
    nuevo[i] = rng.choice(posibles)
    nuevo = reparar(nuevo)
    return nuevo,i if nuevo != c else None


class AlgoritmoGenetico:
    def __init__(self, datos, semilla=42):
        self.rng = random.Random(semilla)
        self.datos = resumir(datos)
        self.cache = {}
        self.poblacion = [BASE] + [individuo(self.rng) for _ in range(POBLACION-1)]
        self.generacion = 0
        self.mejor = max(self.poblacion,key=self.fitness)
        self.historial = [self.fitness(self.mejor)]
        self.promedios = [sum(map(self.fitness,self.poblacion))/POBLACION]
        self.detalle = None

    def fitness(self,c):
        if c not in self.cache:
            self.cache[c] = metricas(c,self.datos)['f1']
        return self.cache[c]

    def paso(self):
        # Estado fijo del documento: dos mejores generan dos hijos que sustituyen a los dos peores.
        self.rng.shuffle(self.poblacion)  # desempate aleatorio
        self.poblacion.sort(key=self.fitness,reverse=True)
        a,b = self.poblacion[:2]
        h1,h2,k = cruzar(a,b,self.rng)
        h1,m1 = mutar(h1,self.rng)
        h2,m2 = mutar(h2,self.rng)
        self.poblacion[-2:] = [h1,h2]
        self.generacion += 1
        self.mejor = max(self.poblacion,key=self.fitness)
        self.historial.append(self.fitness(self.mejor))
        self.promedios.append(sum(map(self.fitness,self.poblacion))/POBLACION)
        self.detalle = (a,b,h1,h2,k,m1,m2)

