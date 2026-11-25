"""Interfaz Tkinter, flujo automático de eventos e integración de la IA."""
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import Counter

from simulacion import (
    FONDO, PANEL, AZUL, BLANCO, GRIS, VERDE, ROJO,
    INDICADORES, BASE, ESCENARIOS, clasificar, generar_evento, dataset,
)
from algoritmo_genetico import GENERACIONES, AlgoritmoGenetico, resumir, metricas

# 4. Interfaz gráfica
class Aplicacion:
    def __init__(self,root):
        self.root = root
        root.title('WiFi Sentinel AI | Prototipo UMSA')
        root.geometry('1050x710')
        root.minsize(860,590)
        root.configure(bg=FONDO)
        self.rng = random.Random()
        self.modelo = None
        self.ga = None
        self.entrenando = False
        self.auto = False
        self.timer = None
        self.timer_ia = None
        self.verdad = None
        self.total = self.altos = 0
        self.live = Counter()
        self.vars = [tk.IntVar(root,0) for _ in INDICADORES]
        self.modo = tk.StringVar(root,'Original')
        self.intervalo = tk.StringVar(root,'1.0')
        self.lbl(root,'WIFI SENTINEL AI',24,AZUL,FONDO,True).pack(pady=(10,0))
        self.lbl(root,'UMSA · La Paz, Bolivia | Datos 100% simulados',11,GRIS,FONDO).pack(pady=(0,8))
        tabs = ttk.Notebook(root)
        tabs.pack(fill='both',expand=True,padx=12,pady=(0,12))
        sim = tk.Frame(tabs,bg=FONDO); ia = tk.Frame(tabs,bg=FONDO)
        tabs.add(sim,text='  01  Simulación en vivo  ')
        tabs.add(ia,text='  02  Inteligencia artificial  ')
        self.crear_sim(sim)
        self.crear_ia(ia)
        self.actualizar()
        root.protocol('WM_DELETE_WINDOW',self.cerrar)

    @staticmethod
    def lbl(p,t='',s=11,c=BLANCO,b=PANEL,bold=False):
        return tk.Label(p,text=t,font=('Arial',s,'bold' if bold else 'normal'),fg=c,bg=b)

    @staticmethod
    def boton(p,t,f,c='#2563eb'):
        return tk.Button(p,text=t,command=f,bg=c,fg=BLANCO,activebackground='#334155',
                         activeforeground=BLANCO,font=('Arial',10,'bold'),relief='flat',padx=8,pady=6,cursor='hand2')

    def panel(self,p):
        return tk.Frame(p,bg=PANEL,padx=12,pady=9)

    def crear_sim(self,p):
        barra = self.panel(p); barra.pack(fill='x',pady=5)
        self.btn_auto = self.boton(barra,'INICIAR FLUJO',self.alternar_flujo,'#15803d'); self.btn_auto.pack(side='left')
        self.lbl(barra,'Intervalo (s):',10).pack(side='left',padx=(12,4))
        ttk.Combobox(barra,textvariable=self.intervalo,values=('0.5','1.0','2.0','3.0'),state='readonly',width=5).pack(side='left')
        self.lbl(barra,'Modelo:',10).pack(side='left',padx=(12,4))
        self.selector_modelo = ttk.Combobox(barra,textvariable=self.modo,values=('Original',),state='readonly',width=13)
        self.selector_modelo.pack(side='left'); self.selector_modelo.bind('<<ComboboxSelected>>',lambda e:self.actualizar())
        self.estado_flujo = self.lbl(barra,'EN PAUSA',10,GRIS,bold=True); self.estado_flujo.pack(side='right')
        cuerpo = tk.Frame(p,bg=FONDO); cuerpo.pack(fill='both',expand=True)
        cuerpo.columnconfigure((0,1),weight=1,uniform='panel'); cuerpo.rowconfigure(0,weight=1)
        iz = self.panel(cuerpo); de = self.panel(cuerpo)
        iz.grid(row=0,column=0,sticky='nsew',padx=(0,4)); de.grid(row=0,column=1,sticky='nsew',padx=(4,0))
        self.lbl(iz,'ESCENARIO E INDICADORES',12,AZUL,bold=True).pack(anchor='w')
        self.selector = ttk.Combobox(iz,values=tuple(ESCENARIOS)+('Personalizado',),state='readonly')
        self.selector.set('Red normal'); self.selector.pack(fill='x',pady=6)
        self.selector.bind('<<ComboboxSelected>>',self.seleccionar)
        self.estados=[]
        for nombre,var in zip(INDICADORES,self.vars):
            fila=tk.Frame(iz,bg=PANEL); fila.pack(fill='x',pady=1)
            tk.Checkbutton(fila,text=nombre,variable=var,command=self.personalizar,bg=PANEL,fg=BLANCO,
                           selectcolor=FONDO,activebackground=PANEL,activeforeground=BLANCO,font=('Arial',10)).pack(side='left')
            et=self.lbl(fila,'',9,VERDE,bold=True); et.pack(side='right'); self.estados.append(et)
        self.vector_lbl=self.lbl(iz,'',14,AZUL,bold=True); self.vector_lbl.pack(pady=5)
        botones=tk.Frame(iz,bg=PANEL); botones.pack(fill='x')
        self.boton(botones,'Aleatorio',self.aleatorio).pack(side='left',expand=True,fill='x',padx=2)
        self.boton(botones,'Reiniciar',self.reiniciar,'#475569').pack(side='left',expand=True,fill='x',padx=2)
        self.real=self.lbl(iz,'',10,GRIS); self.real.pack(pady=5)
        self.lbl(de,'ANÁLISIS AUTOMÁTICO',12,AZUL,bold=True).pack(anchor='w')
        self.riesgo=self.lbl(de,'',23,BLANCO,bold=True); self.riesgo.pack(pady=(6,0))
        self.nivel=self.lbl(de,'',18,VERDE,bold=True); self.nivel.pack()
        self.barra=tk.Canvas(de,height=13,bg='#334155',highlightthickness=0); self.barra.pack(fill='x',pady=6)
        self.barra.bind('<Configure>',lambda e:self.dibujar_barra())
        self.formula=self.lbl(de,'',10,GRIS); self.formula.pack()
        self.consejo=self.lbl(de,'',10,VERDE); self.consejo.config(wraplength=340); self.consejo.pack(pady=5)
        self.compara=self.lbl(de,'',10,GRIS); self.compara.pack()
        self.boton(de,'REGISTRAR EVENTO MANUAL',self.registrar,'#15803d').pack(fill='x',pady=5)
        panel=self.panel(p); panel.pack(fill='both',pady=(6,0))
        cab=tk.Frame(panel,bg=PANEL); cab.pack(fill='x')
        self.lbl(cab,'HISTORIAL EN VIVO',12,AZUL,bold=True).pack(side='left')
        self.boton(cab,'Limpiar',self.limpiar,'#475569').pack(side='right')
        self.stats=self.lbl(panel,'Eventos: 0 | Alertas altas: 0',10,GRIS); self.stats.pack(anchor='w')
        cont=tk.Frame(panel,bg=PANEL); cont.pack(fill='both',expand=True,pady=4)
        cols=('hora','esc','vector','base','ia','ref')
        self.tabla=ttk.Treeview(cont,columns=cols,show='headings',height=5)
        for col,t,w in zip(cols,('Hora','Escenario simulado','Vector','Original','IA','Referencia'),(75,220,100,90,90,110)):
            self.tabla.heading(col,text=t); self.tabla.column(col,width=w,minwidth=55,anchor='w')
        scroll=ttk.Scrollbar(cont,orient='vertical',command=self.tabla.yview); self.tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right',fill='y'); self.tabla.pack(side='left',fill='both',expand=True)
        self.tabla.tag_configure('alto',background='#fee2e2',foreground='#991b1b')
        self.lbl(panel,'Referencia = etiqueta del simulador; no es conocida por el detector. Historial temporal (200 filas).',9,GRIS).pack(anchor='w')

    def crear_ia(self,p):
        top=self.panel(p); top.pack(fill='x',pady=5)
        self.btn_entrenar=self.boton(top,'ENTRENAR IA',self.entrenar,'#6d28d9'); self.btn_entrenar.pack(side='left')
        self.eta=self.lbl(top,'Sin entrenar',11,GRIS); self.eta.pack(side='left',padx=10)
        self.lbl(top,'50 individuos · 100 generaciones',10,GRIS).pack(side='right')
        self.progreso=ttk.Progressbar(p,maximum=GENERACIONES); self.progreso.pack(fill='x',pady=(0,6))
        body=tk.Frame(p,bg=FONDO); body.pack(fill='both',expand=True)
        body.columnconfigure((0,1),weight=1,uniform='ia'); body.rowconfigure(0,weight=1)
        iz=self.panel(body); de=self.panel(body)
        iz.grid(row=0,column=0,sticky='nsew',padx=(0,4)); de.grid(row=0,column=1,sticky='nsew',padx=(4,0))
        self.lbl(iz,'EVOLUCIÓN DEL FITNESS (F1)',12,AZUL,bold=True).pack(anchor='w')
        self.grafica=tk.Canvas(iz,bg=FONDO,height=170,highlightthickness=0); self.grafica.pack(fill='both',expand=True,pady=6)
        self.grafica.bind('<Configure>',lambda e:self.dibujar_grafica())
        self.fitness_lbl=self.lbl(iz,'Mejor: — | Promedio: —',11,VERDE); self.fitness_lbl.pack()
        self.lbl(iz,'Cromosoma [5 pesos + umbral]',10,GRIS).pack(pady=(6,0))
        self.lbl(iz,f'Original: {list(BASE)}',11).pack()
        self.cromosoma=self.lbl(iz,'Evolutivo: —',14,AZUL,bold=True); self.cromosoma.pack(pady=3)
        self.lbl(de,'OPERADORES GENÉTICOS',12,AZUL,bold=True).pack(anchor='w')
        self.detalle=self.lbl(de,'Entrena para observar la selección,\nel cruce, la mutación y la sustitución.',11,BLANCO)
        self.detalle.config(justify='left',anchor='nw'); self.detalle.pack(fill='both',expand=True,pady=8)
        self.lbl(de,'Sustitución: dos hijos reemplazan a los dos peores.',9,GRIS).pack(anchor='w')
        panel=self.panel(p); panel.pack(fill='x',pady=(6,0))
        self.lbl(panel,'COMPARACIÓN EN 600 EVENTOS DE PRUEBA INDEPENDIENTES',11,AZUL,bold=True).pack(anchor='w')
        self.resultados=self.lbl(panel,'Se mostrarán al finalizar el entrenamiento.',11,BLANCO)
        self.resultados.config(font=('Consolas',10),justify='left',anchor='w'); self.resultados.pack(fill='x',pady=4)
        self.lbl(panel,'F1 mide alertas ALTO frente a la etiqueta sintética. No valida redes reales.',9,GRIS).pack(anchor='w')

    def vector(self): return tuple(v.get() for v in self.vars)
    def activo(self): return self.modelo if self.modo.get()=='IA genética' and self.modelo else BASE

    def cargar(self,n,v,y=None):
        self.selector.set(n)
        for var,x in zip(self.vars,v): var.set(x)
        self.verdad=y
        self.actualizar()

    def seleccionar(self,e=None):
        self.pausar()
        n=self.selector.get()
        if n in ESCENARIOS: self.cargar(n,ESCENARIOS[n])
        else: self.verdad=None; self.actualizar()

    def personalizar(self):
        self.pausar(); self.selector.set('Personalizado'); self.verdad=None; self.actualizar()

    def aleatorio(self):
        self.pausar(); self.cargar(*generar_evento(self.rng))

    def reiniciar(self):
        self.pausar(); self.cargar('Red normal',ESCENARIOS['Red normal'])

    def actualizar(self):
        v=self.vector(); c=self.activo(); s,n,color,consejo=clasificar(v,c)
        for x,et in zip(v,self.estados): et.config(text='DETECTADO' if x else 'INACTIVO',fg=ROJO if x else VERDE)
        self.vector_lbl.config(text=f'X = {list(v)}')
        self.real.config(text='Referencia: '+('sin etiqueta' if self.verdad is None else 'amenaza simulada' if self.verdad else 'actividad legítima'))
        self.riesgo.config(text=f'{s} / {sum(c[:5])} puntos'); self.nivel.config(text=n,fg=color)
        self.formula.config(text=' + '.join(f'{w}({x})' for x,w in zip(v,c[:5]))+f' = {s} | T={c[5]}')
        self.consejo.config(text=consejo,fg=color)
        self.compara.config(text=f'Original: {clasificar(v)[1]} | IA: '+(clasificar(v,self.modelo)[1] if self.modelo else 'sin entrenar'))
        self.dibujar_barra()

    def dibujar_barra(self):
        c=self.activo(); s,_,color,_=clasificar(self.vector(),c)
        self.barra.delete('all')
        if s: self.barra.create_rectangle(0,0,self.barra.winfo_width()*s/sum(c[:5]),self.barra.winfo_height(),fill=color,outline='')

    def registrar(self):
        v=self.vector(); s,n,_,_=clasificar(v,self.activo()); base=clasificar(v); ia=clasificar(v,self.modelo) if self.modelo else None
        ref='—' if self.verdad is None else 'Amenaza' if self.verdad else 'Legítima'
        self.tabla.insert('',0,values=(datetime.now().strftime('%H:%M:%S'),self.selector.get(),str(list(v)),f'{base[0]} {base[1]}',f'{ia[0]} {ia[1]}' if ia else '—',ref),tags=('alto',) if n=='ALTO' else ())
        filas=self.tabla.get_children()
        if len(filas)>200: self.tabla.delete(*filas[200:])
        self.total+=1; self.altos+=int(n=='ALTO')
        if self.verdad is not None:
            # Contadores por modelo aplicado; no se usan para entrenar.
            self.live['etiquetados']+=1
            self.live['aciertos']+=int((n=='ALTO')==bool(self.verdad))
        self.stats.config(text=f'Eventos: {self.total} | Alertas altas: {self.altos} | Aciertos etiquetados (modelo aplicado): {self.live["aciertos"]}/{self.live["etiquetados"]}')

    def limpiar(self):
        self.tabla.delete(*self.tabla.get_children()); self.total=self.altos=0; self.live.clear()
        self.stats.config(text='Eventos: 0 | Alertas altas: 0')

    def alternar_flujo(self):
        if self.auto: self.pausar(); return
        self.auto=True; self.btn_auto.config(text='PAUSAR FLUJO',bg='#b45309'); self.estado_flujo.config(text='EN EJECUCIÓN',fg=VERDE); self.tick()

    def tick(self):
        self.timer=None
        if not self.auto: return
        self.cargar(*generar_evento(self.rng)); self.registrar()
        self.timer=self.root.after(int(float(self.intervalo.get())*1000),self.tick)

    def pausar(self):
        self.auto=False
        if self.timer is not None: self.root.after_cancel(self.timer); self.timer=None
        self.btn_auto.config(text='INICIAR FLUJO',bg='#15803d'); self.estado_flujo.config(text='EN PAUSA',fg=GRIS)

    def entrenar(self):
        if self.entrenando: return
        self.entrenando=True; self.btn_entrenar.config(state='disabled')
        self.ga=AlgoritmoGenetico(dataset(1200,2026)); self.progreso['value']=0
        self.resultados.config(text='Entrenando con 1.200 eventos sintéticos...')
        self.paso_ia()

    def paso_ia(self):
        self.timer_ia=None
        ga=self.ga
        if ga.generacion<GENERACIONES: ga.paso()
        self.progreso['value']=ga.generacion
        self.eta.config(text=f'Generación {ga.generacion}/{GENERACIONES}',fg=VERDE)
        self.fitness_lbl.config(text=f'Mejor: {ga.historial[-1]:.4f} | Promedio: {ga.promedios[-1]:.4f}')
        self.cromosoma.config(text=f'Evolutivo: {list(ga.mejor)}')
        a,b,h1,h2,k,m1,m2=ga.detalle
        self.detalle.config(text=f'Padre 1: {list(a)}\nPadre 2: {list(b)}\n\nCruce: '+(f'corte después del gen {k}' if k else 'sin cruce')+f'\nHijo 1: {list(h1)}\nHijo 2: {list(h2)}\n\nMutación hijo 1: '+(f'gen {m1+1}' if m1 is not None else 'no')+'\nMutación hijo 2: '+(f'gen {m2+1}' if m2 is not None else 'no'))
        self.dibujar_grafica()
        if ga.generacion<GENERACIONES:
            self.timer_ia=self.root.after(35,self.paso_ia)
        else:
            self.modelo=ga.mejor; self.entrenando=False
            self.btn_entrenar.config(state='normal'); self.eta.config(text='Entrenamiento finalizado',fg=VERDE)
            self.selector_modelo.config(values=('Original','IA genética')); self.modo.set('IA genética'); self.actualizar()
            prueba=resumir(dataset(600,2027)); a=metricas(BASE,prueba); b=metricas(self.modelo,prueba)
            texto='Modelo       F1     Prec.  Recall  FP%    VP  FP  VN  FN\n'
            for nombre,m in [('Original',a),('IA genética',b)]:
                texto+=f'{nombre:12} {m["f1"]:5.3f}  {m["precision"]:5.3f}  {m["recall"]:5.3f}  {100*m["fpr"]:5.1f}  {m["vp"]:3} {m["fp"]:3} {m["vn"]:3} {m["fn"]:3}\n'
            self.resultados.config(text=texto.rstrip())

    def dibujar_grafica(self):
        cv=self.grafica; cv.delete('all'); w=cv.winfo_width(); h=cv.winfo_height()
        if w<90 or h<70: return
        x0,y0,x1,y1=40,12,w-12,h-26
        for i in range(5):
            yy=y1-(y1-y0)*i/4; cv.create_line(x0,yy,x1,yy,fill='#334155',dash=(3,3)); cv.create_text(x0-5,yy,text=f'{i/4:.2f}',fill=GRIS,anchor='e',font=('Arial',8))
        for g in (0,25,50,75,100): cv.create_text(x0+(x1-x0)*g/100,y1+12,text=str(g),fill=GRIS,font=('Arial',8))
        if not self.ga: return
        for valores,color in ((self.ga.promedios,GRIS),(self.ga.historial,VERDE)):
            pts=[q for i,v in enumerate(valores) for q in (x0+(x1-x0)*i/GENERACIONES,y1-(y1-y0)*v)]
            if len(pts)>2: cv.create_line(*pts,fill=color,width=2)
        cv.create_text(x1-5,y0+8,text='Mejor / promedio',fill=GRIS,anchor='e',font=('Arial',8))

    def cerrar(self):
        self.pausar()
        if self.timer_ia is not None: self.root.after_cancel(self.timer_ia)
        self.root.destroy()

