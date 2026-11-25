"""WiFi Sentinel AI - punto de entrada y pruebas matemáticas.
Ejecutar: py main.py | Pruebas sin interfaz: py main.py --test
Solo biblioteca estándar de Python. No captura tráfico ni realiza ataques.
"""
import sys
import tkinter as tk
from itertools import product

from simulacion import BASE, clasificar, dataset
from algoritmo_genetico import (
    POBLACION, GENERACIONES, AlgoritmoGenetico, reparar, resumir, metricas,
)
from interfaz import Aplicacion

# 5. Pruebas matemáticas y de evolución sin abrir ventanas.
def pruebas():
    for v in product((0,1),repeat=5):
        s,n,_,_=clasificar(v)
        assert s==3*v[0]+2*v[1]+3*v[2]+2*v[3]+v[4]
        assert n==('ALTO' if s>=5 else 'MEDIO' if s>=3 else 'BAJO' if s else 'NORMAL')
    train=dataset(1200,2026); test=dataset(600,2027)
    assert {y for _,y in train}=={0,1} and {y for _,y in test}=={0,1}
    ga=AlgoritmoGenetico(train)
    for _ in range(GENERACIONES):
        ga.paso(); assert len(ga.poblacion)==POBLACION
        assert all(reparar(c)==c for c in ga.poblacion)
    assert all(a<=b for a,b in zip(ga.historial,ga.historial[1:]))
    assert len(ga.historial)==101
    print('32 combinaciones y 100 generaciones: OK')
    print('Cromosoma:',ga.mejor,'Fitness inicial/final:',ga.historial[0],ga.historial[-1])
    for c in (BASE,ga.mejor):
        m=metricas(c,resumir(test)); assert sum(m[k] for k in ('vp','fp','vn','fn'))==600
        print(c,m)

if __name__=='__main__':
    if '--test' in sys.argv: pruebas()
    else:
        root=tk.Tk(); Aplicacion(root); root.mainloop()
