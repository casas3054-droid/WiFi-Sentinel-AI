"""Escenarios sintéticos, indicadores y motor de clasificación de riesgo."""
import random

# 1. Configuración y modelo original del informe
FONDO, PANEL, AZUL = '#0f172a', '#1e293b', '#38bdf8'
BLANCO, GRIS, VERDE = '#f8fafc', '#94a3b8', '#4ade80'
AMARILLO, NARANJA, ROJO = '#facc15', '#fb923c', '#f87171'
INDICADORES = ('AP sospechoso', 'Escaneo de puertos', 'Anomalía ARP',
               'Fallos de autenticación', 'Tráfico anómalo')
BASE = (3, 2, 3, 2, 1, 5)
ESCENARIOS = {'Red normal': (0,0,0,0,0), 'Evil Twin': (1,0,0,0,0),
              'Escaneo de puertos': (0,1,0,0,0), 'Anomalía ARP': (0,0,1,0,0),
              'Fallos de autenticación': (0,0,0,1,0), 'Tráfico anómalo': (0,0,0,0,1),
              'Escaneo + ARP': (0,1,1,0,0), 'Amenazas múltiples': (1,1,1,1,1)}


def calcular_riesgo(vector, cromosoma=BASE):
    return sum(x*w for x,w in zip(vector, cromosoma[:5]))


def clasificar(vector, cromosoma=BASE):
    s = calcular_riesgo(vector, cromosoma)
    if s >= cromosoma[5]:
        return s, 'ALTO', ROJO, 'Revisar prioritariamente los indicadores.'
    if s >= 3:
        return s, 'MEDIO', NARANJA, 'Investigar la actividad sospechosa.'
    if s > 0:
        return s, 'BAJO', AMARILLO, 'Mantener la supervisión.'
    return s, 'NORMAL', VERDE, 'No se observan indicadores activos.'

# 2. Datos sintéticos. La etiqueta procede del escenario latente, NO de la fórmula.
# Probabilidades didácticas, no mediciones de redes reales de La Paz.
PERFILES = (
    ('Actividad habitual', 0, (.025,.10,.025,.09,.18)),
    ('Pico legítimo de actividad', 0, (.04,.20,.04,.22,.75)),
    ('Evil Twin simulado', 1, (.94,.12,.34,.25,.35)),
    ('Escaneo sospechoso simulado', 1, (.06,.94,.12,.25,.63)),
    ('Anomalía ARP simulada', 1, (.18,.30,.95,.13,.48)),
    ('Autenticación sospechosa simulada', 1, (.10,.24,.08,.95,.70)),
    ('Tráfico anómalo simulado', 1, (.12,.48,.20,.38,.94)),
    ('Amenazas combinadas simuladas', 1, (.78,.79,.80,.75,.86)),
)


def generar_evento(rng):
    nombre, etiqueta, probs = rng.choices(PERFILES, weights=(50,15,7,7,7,6,5,3), k=1)[0]
    vector = tuple(int(rng.random() < p) for p in probs)
    return nombre, vector, etiqueta


def dataset(n, semilla):
    rng = random.Random(semilla)
    return [(v,y) for _,v,y in (generar_evento(rng) for _ in range(n))]


