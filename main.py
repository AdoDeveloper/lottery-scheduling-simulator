"""
Interfaz gráfica para el simulador de planificación por lotería.
Autor: @Adolfo Cortez
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import random
from proceso import Proceso
from simulador import SimuladorLoteria

class InterfazSimulador:
    """
    Interfaz gráfica principal del simulador.
    Proporciona visualización intuitiva del algoritmo de Lottery Scheduling.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Planificación por Lotería - Lottery Scheduling")
        self.root.geometry("1600x950")
        self.root.configure(bg='#f0f0f0')
        
        # Variables de control
        self.simulador = None
        self.simulacion_activa = False
        self.thread_simulacion = None
        self.procesos_creados = []
        self.colores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
                       '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#52BE80']
        
        self.crear_widgets()
        self.centrar_ventana()
        
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def crear_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # TÍTULO PRINCIPAL
        frame_titulo = tk.Frame(self.root, bg='#2C3E50', height=70)
        frame_titulo.pack(fill=tk.X)
        frame_titulo.pack_propagate(False)
        
        titulo = tk.Label(frame_titulo, 
                         text="SIMULADOR DE PLANIFICACIÓN POR LOTERÍA", 
                         font=('Arial', 22, 'bold'), bg='#2C3E50', fg='white')
        titulo.pack(expand=True, pady=5)
        
        subtitulo = tk.Label(frame_titulo, 
                            text="Algoritmo: Lottery Scheduling (Waldspurger & Weihl, 1994)", 
                            font=('Arial', 11), bg='#2C3E50', fg='#ecf0f1')
        subtitulo.pack()
        
        # FRAME PRINCIPAL CON 3 COLUMNAS
        frame_principal = tk.Frame(self.root, bg='#f0f0f0')
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # COLUMNA IZQUIERDA: Controles CON SCROLL
        self.crear_panel_controles(frame_principal)
        
        # COLUMNA CENTRO: Visualización
        self.crear_panel_visualizacion(frame_principal)
        
        # COLUMNA DERECHA: Información y análisis CON SCROLL
        self.crear_panel_informacion(frame_principal)
        
    def crear_panel_controles(self, parent):
        """Crea el panel de controles en la columna izquierda CON SCROLL"""
        # Frame contenedor con scrollbar
        frame_container_izq = tk.Frame(parent, bg='white')
        frame_container_izq.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), 
                                padx=5, pady=5)
        
        # Canvas y scrollbar
        canvas_scroll_izq = tk.Canvas(frame_container_izq, bg='white', highlightthickness=0)
        scrollbar_izq = ttk.Scrollbar(frame_container_izq, orient="vertical", 
                                     command=canvas_scroll_izq.yview)
        
        # Frame interior
        frame_controles = tk.Frame(canvas_scroll_izq, bg='white')
        
        # Configurar canvas
        canvas_scroll_izq.configure(yscrollcommand=scrollbar_izq.set)
        
        # Empaquetar
        scrollbar_izq.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_scroll_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear ventana en canvas
        canvas_window_izq = canvas_scroll_izq.create_window((0, 0), window=frame_controles, anchor='nw')
        
        # Función para actualizar scroll
        def configurar_scroll_izq(event=None):
            canvas_scroll_izq.configure(scrollregion=canvas_scroll_izq.bbox("all"))
            canvas_width = canvas_scroll_izq.winfo_width()
            canvas_scroll_izq.itemconfig(canvas_window_izq, width=canvas_width)
        
        frame_controles.bind('<Configure>', configurar_scroll_izq)
        canvas_scroll_izq.bind('<Configure>', configurar_scroll_izq)
        
        # Scroll con rueda del mouse SOLO en este canvas
        def _on_mousewheel_izq(event):
            canvas_scroll_izq.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas_scroll_izq.bind("<Enter>", lambda e: canvas_scroll_izq.bind_all("<MouseWheel>", _on_mousewheel_izq))
        canvas_scroll_izq.bind("<Leave>", lambda e: canvas_scroll_izq.unbind_all("<MouseWheel>"))
        
        # AHORA CREAR CONTENIDO DENTRO DE frame_controles
        
        tk.Label(frame_controles, text="CONFIGURACIÓN Y CONTROLES", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(pady=10)
        
        # SECCIÓN 1: Configuración de simulación
        config_frame = tk.LabelFrame(frame_controles, text=" Parámetros de Simulación ", 
                                    bg='white', font=('Arial', 10, 'bold'))
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(config_frame, text="Quantum (ciclos):", bg='white', 
                font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.entry_quantum = ttk.Entry(config_frame, width=10, font=('Arial', 10))
        self.entry_quantum.insert(0, "3")
        self.entry_quantum.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(config_frame, text="Velocidad:", bg='white', 
                font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.scale_velocidad = ttk.Scale(config_frame, from_=0.1, to=2.0, 
                                        orient=tk.HORIZONTAL, length=120)
        self.scale_velocidad.set(1.0)
        self.scale_velocidad.grid(row=1, column=1, pady=5, padx=5)
        self.label_vel = tk.Label(config_frame, text="1.0x", bg='white', font=('Arial', 9))
        self.label_vel.grid(row=1, column=2, padx=5)
        self.scale_velocidad.configure(command=self.actualizar_label_velocidad)
        
        # NUEVA: Pool de tickets globales
        self.var_pool_global = tk.BooleanVar(value=False)
        check_pool = tk.Checkbutton(config_frame, text="Usar pool de tickets globales", 
                                   variable=self.var_pool_global, bg='white',
                                   font=('Arial', 9), command=self.toggle_pool_global)
        check_pool.grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        self.label_pool = tk.Label(config_frame, text="Total tickets:", bg='white', 
                                  font=('Arial', 9), state=tk.DISABLED)
        self.label_pool.grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_pool = ttk.Entry(config_frame, width=10, state=tk.DISABLED)
        self.entry_pool.insert(0, "100")
        self.entry_pool.grid(row=3, column=1, padx=5, pady=3)
        
        # Configurar tickets manualmente
        self.var_tickets_manual = tk.BooleanVar(value=False)
        check_tickets = tk.Checkbutton(config_frame, text="Configurar tickets manualmente", 
                                      variable=self.var_tickets_manual, bg='white',
                                      font=('Arial', 9), command=self.toggle_tickets_manual)
        check_tickets.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # SECCIÓN 2: Creación de procesos
        proceso_frame = tk.LabelFrame(frame_controles, text=" Crear Proceso Manualmente ", 
                                     bg='white', font=('Arial', 10, 'bold'))
        proceso_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(proceso_frame, text="ID del Proceso:", bg='white', 
                font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_id = ttk.Entry(proceso_frame, width=8)
        self.entry_id.insert(0, "1")
        self.entry_id.grid(row=0, column=1, padx=5, pady=3)
        
        tk.Label(proceso_frame, text="Tiempo CPU:", bg='white', 
                font=('Arial', 9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_cpu = ttk.Entry(proceso_frame, width=8)
        self.entry_cpu.insert(0, "5")
        self.entry_cpu.grid(row=1, column=1, padx=5, pady=3)
        
        tk.Label(proceso_frame, text="Prioridad (1-5):", bg='white', 
                font=('Arial', 9)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_prioridad = ttk.Entry(proceso_frame, width=8)
        self.entry_prioridad.insert(0, "2")
        self.entry_prioridad.grid(row=2, column=1, padx=5, pady=3)
        
        # Campo de tickets
        self.label_tickets = tk.Label(proceso_frame, text="Tickets:", bg='white', 
                                     font=('Arial', 9), state=tk.DISABLED)
        self.label_tickets.grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_tickets = ttk.Entry(proceso_frame, width=8, state=tk.DISABLED)
        self.entry_tickets.insert(0, "20")
        self.entry_tickets.grid(row=3, column=1, padx=5, pady=3)
        
        self.entry_servidor = ttk.Entry(proceso_frame, width=8)
        self.entry_servidor.insert(0, "0")
        
        btn_frame = tk.Frame(proceso_frame, bg='white')
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.btn_agregar = tk.Button(btn_frame, text="Agregar Proceso", 
                                     command=self.agregar_proceso_manual,
                                     bg='#3498db', fg='white', font=('Arial', 9, 'bold'),
                                     relief=tk.RAISED, bd=2, cursor='hand2', width=15)
        self.btn_agregar.pack(side=tk.LEFT, padx=3)
        
        self.btn_aleatorio = tk.Button(btn_frame, text="Aleatorios", 
                                      command=self.agregar_procesos_aleatorios,
                                      bg='#9b59b6', fg='white', font=('Arial', 9, 'bold'),
                                      relief=tk.RAISED, bd=2, cursor='hand2', width=12)
        self.btn_aleatorio.pack(side=tk.LEFT, padx=3)
        
        # NUEVA SECCIÓN: Configuración de procesos aleatorios
        aleatorio_config_frame = tk.LabelFrame(frame_controles, text=" Configuración de Aleatorios ", 
                                              bg='white', font=('Arial', 10, 'bold'))
        aleatorio_config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(aleatorio_config_frame, text="Cantidad de procesos:", bg='white', 
                font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.entry_cant_aleatorios = ttk.Entry(aleatorio_config_frame, width=8)
        self.entry_cant_aleatorios.insert(0, "5")
        self.entry_cant_aleatorios.grid(row=0, column=1, padx=5, pady=3)
        
        info_aleatorio = tk.Label(aleatorio_config_frame, 
                                 text="💡 Si hay pool global activado,\nlos tickets se distribuyen\nautomáticamente entre procesos.",
                                 bg='#e8f4f8', fg='#2c3e50', font=('Arial', 8),
                                 justify=tk.LEFT, padx=5, pady=5)
        info_aleatorio.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # SECCIÓN 3: Lista de procesos creados
        lista_frame = tk.LabelFrame(frame_controles, text=" Procesos Creados ", 
                                   bg='white', font=('Arial', 10, 'bold'))
        lista_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(lista_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox_procesos = tk.Listbox(lista_frame, height=6, 
                                          yscrollcommand=scrollbar.set,
                                          font=('Courier', 9))
        self.listbox_procesos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.listbox_procesos.yview)
        
        self.btn_limpiar = tk.Button(lista_frame, text="Limpiar Lista", 
                                    command=self.limpiar_procesos,
                                    bg='#e74c3c', fg='white', font=('Arial', 9),
                                    relief=tk.RAISED, bd=2, cursor='hand2')
        self.btn_limpiar.pack(pady=5)
        
        # SECCIÓN 4: Botones de control de simulación
        control_frame = tk.LabelFrame(frame_controles, text=" Control de Simulación ", 
                                     bg='white', font=('Arial', 10, 'bold'))
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.btn_iniciar = tk.Button(control_frame, text="INICIAR SIMULACIÓN", 
                                    command=self.iniciar_simulacion,
                                    bg='#27ae60', fg='white', 
                                    font=('Arial', 11, 'bold'),
                                    height=2, relief=tk.RAISED, bd=3, cursor='hand2')
        self.btn_iniciar.pack(fill=tk.X, pady=5, padx=5)
        
        self.btn_pausar = tk.Button(control_frame, text="PAUSAR", 
                                   command=self.pausar_simulacion,
                                   bg='#f39c12', fg='white', 
                                   font=('Arial', 10, 'bold'),
                                   state=tk.DISABLED, relief=tk.RAISED, bd=2, cursor='hand2')
        self.btn_pausar.pack(fill=tk.X, pady=5, padx=5)
        
        self.btn_es = tk.Button(control_frame, text="ENTRADA/SALIDA", 
                              command=self.simular_entrada_salida,
                              bg='#8e44ad', fg='white', 
                              font=('Arial', 10, 'bold'),
                              state=tk.DISABLED, relief=tk.RAISED, bd=2, cursor='hand2')
        self.btn_es.pack(fill=tk.X, pady=5, padx=5)
        
        self.btn_reiniciar = tk.Button(control_frame, text="🔄 REINICIAR TODO", 
                                      command=self.reiniciar_todo,
                                      bg='#c0392b', fg='white', 
                                      font=('Arial', 10, 'bold'),
                                      relief=tk.RAISED, bd=2, cursor='hand2')
        self.btn_reiniciar.pack(fill=tk.X, pady=5, padx=5)
        
        # Información adicional
        info_label = tk.Label(frame_controles, 
                             text="💡 Pool de tickets globales:\nDefine un total fijo de tickets\npara el sorteo, independiente\nde los tickets individuales.",
                             bg='#ecf0f1', fg='#2c3e50', font=('Arial', 8),
                             justify=tk.LEFT, padx=10, pady=10)
        info_label.pack(fill=tk.X, padx=10, pady=10)
        
    def toggle_pool_global(self):
        """Activa/desactiva el pool de tickets globales"""
        if self.var_pool_global.get():
            self.entry_pool.config(state=tk.NORMAL)
            self.label_pool.config(state=tk.NORMAL)
        else:
            self.entry_pool.config(state=tk.DISABLED)
            self.label_pool.config(state=tk.DISABLED)
    
    def toggle_tickets_manual(self):
        """Activa/desactiva el campo de tickets manuales"""
        if self.var_tickets_manual.get():
            self.entry_tickets.config(state=tk.NORMAL)
            self.label_tickets.config(state=tk.NORMAL)
        else:
            self.entry_tickets.config(state=tk.DISABLED)
            self.label_tickets.config(state=tk.DISABLED)
    
    def actualizar_label_velocidad(self, valor):
        """Actualiza el label de velocidad"""
        self.label_vel.config(text=f"{float(valor):.1f}x")
        
    def crear_panel_visualizacion(self, parent):
        """Crea el panel de visualización en la columna central"""
        frame_viz = tk.LabelFrame(parent, text=" VISUALIZACIÓN EN TIEMPO REAL ", 
                                 font=('Arial', 12, 'bold'), bg='white', 
                                 relief=tk.RIDGE, bd=3)
        frame_viz.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E), 
                      padx=5, pady=5)
        
        # Estado actual de la simulación
        estado_frame = tk.Frame(frame_viz, bg='white')
        estado_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Fila 1: Tiempo y Quantum
        fila1 = tk.Frame(estado_frame, bg='white')
        fila1.pack(fill=tk.X)
        
        tk.Label(fila1, text="Tiempo:", bg='white', 
                font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        self.label_tiempo = tk.Label(fila1, text="0", bg='white', 
                                    font=('Arial', 11), fg='#e74c3c', width=5)
        self.label_tiempo.pack(side=tk.LEFT, padx=10)
        
        tk.Label(fila1, text="Quantum Rest.:", bg='white', 
                font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=(20,0))
        self.label_quantum_rest = tk.Label(fila1, text="0", bg='white', 
                                          font=('Arial', 11), fg='#3498db', width=5)
        self.label_quantum_rest.pack(side=tk.LEFT, padx=10)
        
        # Fila 2: Ticket sorteado
        fila2 = tk.Frame(estado_frame, bg='white')
        fila2.pack(fill=tk.X, pady=5)
        
        tk.Label(fila2, text="Ticket Sorteado:", bg='white', 
                font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        self.label_ticket = tk.Label(fila2, text="N/A", bg='white', 
                                    font=('Arial', 11), fg='#9b59b6')
        self.label_ticket.pack(side=tk.LEFT, padx=10)
        
        # Canvas para dibujar el estado visual
        canvas_frame = tk.Frame(frame_viz, bg='white')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#ecf0f1', 
                               highlightthickness=2, highlightbackground='#34495e')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Frame para último evento
        evento_frame = tk.Frame(frame_viz, bg='#34495e', height=70)
        evento_frame.pack(fill=tk.X, padx=10, pady=10)
        evento_frame.pack_propagate(False)
        
        tk.Label(evento_frame, text="ÚLTIMO EVENTO:", bg='#34495e', 
                fg='white', font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=5, pady=2)
        
        self.label_evento = tk.Label(evento_frame, text="Sistema esperando inicio de simulación...", 
                                    bg='#34495e', fg='#ecf0f1', 
                                    font=('Arial', 10), wraplength=600, justify=tk.LEFT)
        self.label_evento.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
    def crear_panel_informacion(self, parent):
        """Crea el panel de información en la columna derecha CON SCROLL"""
        # Frame contenedor con scrollbar
        frame_container = tk.Frame(parent, bg='white')
        frame_container.grid(row=0, column=2, sticky=(tk.N, tk.S, tk.W, tk.E), 
                            padx=5, pady=5)
        
        # Canvas y scrollbar para permitir scroll
        canvas_scroll = tk.Canvas(frame_container, bg='white', highlightthickness=0)
        scrollbar_vertical = ttk.Scrollbar(frame_container, orient="vertical", command=canvas_scroll.yview)
        
        # Frame interior que contendrá todo el contenido
        frame_info_interior = tk.Frame(canvas_scroll, bg='white')
        
        # Configurar canvas
        canvas_scroll.configure(yscrollcommand=scrollbar_vertical.set)
        
        # Empaquetar
        scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        canvas_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Crear ventana en canvas
        canvas_window = canvas_scroll.create_window((0, 0), window=frame_info_interior, anchor='nw')
        
        # Función para actualizar scroll region
        def configurar_scroll(event=None):
            canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
            canvas_width = canvas_scroll.winfo_width()
            canvas_scroll.itemconfig(canvas_window, width=canvas_width)
        
        frame_info_interior.bind('<Configure>', configurar_scroll)
        canvas_scroll.bind('<Configure>', configurar_scroll)
        
        # Scroll con rueda del mouse SOLO en este canvas
        def _on_mousewheel(event):
            canvas_scroll.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas_scroll.bind("<Enter>", lambda e: canvas_scroll.bind_all("<MouseWheel>", _on_mousewheel))
        canvas_scroll.bind("<Leave>", lambda e: canvas_scroll.unbind_all("<MouseWheel>"))
        
        # AHORA CREAR TODOS LOS WIDGETS DENTRO DE frame_info_interior
        
        # Título del panel
        tk.Label(frame_info_interior, text="INFORMACIÓN Y ANÁLISIS", 
                font=('Arial', 12, 'bold'), bg='white', fg='#2c3e50').pack(pady=10)
        
        # Proceso ejecutando
        proc_frame = tk.LabelFrame(frame_info_interior, text=" Proceso Ejecutando ", 
                                  bg='white', font=('Arial', 10, 'bold'))
        proc_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.label_proc_ejecutando = tk.Label(proc_frame, text="NINGUNO", 
                                             bg='white', font=('Arial', 16, 'bold'), 
                                             fg='#e74c3c', height=2)
        self.label_proc_ejecutando.pack(fill=tk.X, padx=10, pady=10)
        
        # Cola de listos con tabla
        cola_frame = tk.LabelFrame(frame_info_interior, text=" Cola de Listos ", 
                                  bg='white', font=('Arial', 10, 'bold'))
        cola_frame.pack(fill=tk.X, padx=10, pady=10)
        
        columns = ('ID', 'Tickets', 'CPU', 'Pri', 'Serv')
        self.tree_cola = ttk.Treeview(cola_frame, columns=columns, 
                                     show='headings', height=6)
        
        self.tree_cola.heading('ID', text='ID')
        self.tree_cola.heading('Tickets', text='Tickets')
        self.tree_cola.heading('CPU', text='CPU')
        self.tree_cola.heading('Pri', text='Pri')
        self.tree_cola.heading('Serv', text='Serv')
        
        self.tree_cola.column('ID', width=40, anchor=tk.CENTER)
        self.tree_cola.column('Tickets', width=60, anchor=tk.CENTER)
        self.tree_cola.column('CPU', width=60, anchor=tk.CENTER)
        self.tree_cola.column('Pri', width=40, anchor=tk.CENTER)
        self.tree_cola.column('Serv', width=50, anchor=tk.CENTER)
        scrollbar_tree = ttk.Scrollbar(cola_frame, orient=tk.VERTICAL, 
                                      command=self.tree_cola.yview)
        self.tree_cola.configure(yscroll=scrollbar_tree.set)
        
        self.tree_cola.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar_tree.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Procesos terminados
        term_frame = tk.LabelFrame(frame_info_interior, text=" Procesos Terminados ", 
                                  bg='white', font=('Arial', 10, 'bold'))
        term_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.label_terminados = tk.Label(term_frame, text="0 procesos", 
                                        bg='white', font=('Arial', 11))
        self.label_terminados.pack(pady=5)
        
        # Análisis teórico del último sorteo
        analisis_frame = tk.LabelFrame(frame_info_interior, text=" Análisis del Último Sorteo ", 
                                      bg='white', font=('Arial', 10, 'bold'))
        analisis_frame.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.text_analisis = scrolledtext.ScrolledText(analisis_frame, height=12, 
                                                       font=('Courier', 8), 
                                                       bg='#f9f9f9', wrap=tk.WORD)
        self.text_analisis.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Estadísticas finales - ÁREA GRANDE CON SCROLL
        stats_frame = tk.LabelFrame(frame_info_interior, text=" Estadísticas y Resultados Finales ", 
                                   bg='white', font=('Arial', 10, 'bold'))
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_stats = scrolledtext.ScrolledText(stats_frame, height=30, 
                                                    font=('Courier', 8), 
                                                    bg='#ecf0f1', wrap=tk.WORD)
        self.text_stats.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar pesos de columnas
        parent.columnconfigure(0, weight=1, minsize=350)
        parent.columnconfigure(1, weight=2, minsize=600)
        parent.columnconfigure(2, weight=1, minsize=450)
        parent.rowconfigure(0, weight=1)
        
    def agregar_proceso_manual(self):
        """Agrega un proceso manualmente desde los campos de entrada"""
        try:
            pid = int(self.entry_id.get())
            tiempo_cpu = int(self.entry_cpu.get())
            prioridad = int(self.entry_prioridad.get())
            servidor = int(self.entry_servidor.get())
            
            # Validaciones
            if tiempo_cpu <= 0:
                messagebox.showerror("Error", "El tiempo de CPU debe ser mayor a 0")
                return
            
            if prioridad < 1 or prioridad > 5:
                messagebox.showerror("Error", "La prioridad debe estar entre 1 y 5")
                return
            
            if any(p.identificador == pid for p in self.procesos_creados):
                messagebox.showerror("Error", f"Ya existe un proceso con ID {pid}")
                return
            
            if servidor != 0 and not any(p.identificador == servidor for p in self.procesos_creados):
                messagebox.showerror("Error", f"El proceso servidor {servidor} no existe.\nCrea primero el servidor.")
                return
            
            # Crear proceso
            proceso = Proceso(identificador=pid, tiempo_cpu=tiempo_cpu, 
                            prioridad=prioridad, proceso_servidor=servidor)
            
            # Configurar tickets
            if self.var_tickets_manual.get():
                tickets = int(self.entry_tickets.get())
                if tickets < 1:
                    messagebox.showerror("Error", "Los tickets deben ser al menos 1")
                    return
                
                # VALIDACIÓN: Si hay pool global, advertir si tickets exceden el pool
                if self.var_pool_global.get():
                    try:
                        pool_total = int(self.entry_pool.get())
                        if tickets > pool_total:
                            respuesta = messagebox.askyesno(
                                "Advertencia",
                                f"Los tickets ({tickets}) exceden el pool global ({pool_total}).\n\n"
                                f"El proceso tendrá mayor probabilidad proporcional,\n"
                                f"pero el sorteo siempre será del 1 al {pool_total}.\n\n"
                                f"¿Deseas continuar?"
                            )
                            if not respuesta:
                                return
                    except:
                        pass
                
                proceso.num_tickets = tickets
                proceso.num_tickets_original = tickets
            else:
                proceso.num_tickets = prioridad * 10
                proceso.num_tickets_original = prioridad * 10
            
            proceso.color = self.colores[len(self.procesos_creados) % len(self.colores)]
            
            self.procesos_creados.append(proceso)
            self.actualizar_lista_procesos()
            
            # Incrementar ID automáticamente
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(pid + 1))
            
            messagebox.showinfo("Éxito", f"Proceso P{pid} creado:\n"
                                        f"- CPU: {tiempo_cpu}\n"
                                        f"- Prioridad: {prioridad}\n"
                                        f"- Tickets: {proceso.num_tickets}")
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")
    
    def agregar_procesos_aleatorios(self):
        """Agrega N procesos distribuyendo tickets según el pool global"""
        try:
            # Obtener cantidad de procesos a crear
            cantidad = int(self.entry_cant_aleatorios.get())
            
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            if cantidad > 20:
                respuesta = messagebox.askyesno(
                    "Confirmación",
                    f"¿Estás seguro de crear {cantidad} procesos?\n"
                    f"Esto podría hacer la visualización confusa."
                )
                if not respuesta:
                    return
            
            base_id = len(self.procesos_creados) + 1
            
            # VERIFICAR que AMBAS opciones estén activadas para distribución inteligente
            if self.var_pool_global.get() and self.var_tickets_manual.get():
                try:
                    pool_total = int(self.entry_pool.get())
                    
                    if pool_total < cantidad:
                        messagebox.showerror("Error", 
                            f"El pool ({pool_total}) es menor que la cantidad de procesos ({cantidad}).\n"
                            f"Necesitas al menos {cantidad} tickets.")
                        return
                    
                    # Distribuir tickets de manera inteligente
                    tickets_asignados = self._distribuir_tickets_inteligente(pool_total, cantidad)
                    
                    if not tickets_asignados:  # Si falló la distribución
                        return
                    
                    # Crear procesos con tickets distribuidos
                    for i in range(cantidad):
                        pid = base_id + i
                        tiempo_cpu = random.randint(3, 10)
                        prioridad = random.randint(1, 3)
                        
                        proceso = Proceso(identificador=pid, tiempo_cpu=tiempo_cpu, 
                                        prioridad=prioridad, proceso_servidor=0)
                        
                        proceso.num_tickets = tickets_asignados[i]
                        proceso.num_tickets_original = tickets_asignados[i]
                        proceso.color = self.colores[len(self.procesos_creados) % len(self.colores)]
                        self.procesos_creados.append(proceso)
                    
                    # Verificación de suma
                    suma_real = sum(tickets_asignados)
                    
                    # Mensaje informativo con VERIFICACIÓN
                    detalle_tickets = ", ".join([f"P{base_id + i}={tickets_asignados[i]}" 
                                                for i in range(cantidad)])
                    
                    messagebox.showinfo(
                        "Procesos Creados ✓",
                        f"Se crearon {cantidad} procesos aleatorios\n\n"
                        f"Pool global configurado: {pool_total} tickets\n"
                        f"Suma de tickets asignados: {suma_real} tickets\n\n"
                        f"Distribución:\n{detalle_tickets}\n\n"
                        f"✓ VERIFICACIÓN: {suma_real} = {pool_total}"
                    )
                    
                except ValueError:
                    messagebox.showerror("Error", "El pool de tickets debe ser un número válido")
                    return
            
            # SIN pool global o SIN tickets manuales
            else:
                for i in range(cantidad):
                    pid = base_id + i
                    tiempo_cpu = random.randint(3, 10)
                    prioridad = random.randint(1, 3)
                    
                    proceso = Proceso(identificador=pid, tiempo_cpu=tiempo_cpu, 
                                    prioridad=prioridad, proceso_servidor=0)
                    
                    # Tickets automáticos por prioridad
                    proceso.num_tickets = prioridad * 10
                    proceso.num_tickets_original = prioridad * 10
                    
                    proceso.color = self.colores[len(self.procesos_creados) % len(self.colores)]
                    self.procesos_creados.append(proceso)
                
                messagebox.showinfo("Éxito", 
                    f"{cantidad} procesos creados.\n\n"
                    f"NOTA: Para distribución basada en pool,\n"
                    f"activa AMBAS opciones:\n"
                    f"1. Pool de tickets globales\n"
                    f"2. Configurar tickets manualmente")
            
            self.actualizar_lista_procesos()
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, str(base_id + cantidad))
            
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear procesos: {str(e)}")
    
    def _distribuir_tickets_inteligente(self, pool_total, cantidad):
        """
        Distribuye tickets de manera inteligente entre N procesos.
        GARANTIZA que la suma sea exactamente pool_total.
        
        Estrategia:
        1. Asigna ticket por ticket de manera aleatoria
        2. Asegura que todos tengan al menos 1 ticket
        3. Distribuye el resto aleatoriamente
        
        Args:
            pool_total: Total de tickets a distribuir
            cantidad: Número de procesos
            
        Returns:
            Lista de enteros con tickets para cada proceso que SUMAN pool_total
        """
        if cantidad <= 0:
            return []
        
        if pool_total < cantidad:
            # Si no hay suficientes tickets para dar 1 a cada proceso
            messagebox.showerror("Error", 
                f"Pool insuficiente: {pool_total} tickets para {cantidad} procesos.\n"
                f"Necesitas al menos {cantidad} tickets (1 por proceso).")
            return []
        
        # Inicializar: dar 1 ticket a cada proceso
        tickets = [1] * cantidad
        tickets_restantes = pool_total - cantidad
        
        # Distribuir los tickets restantes de manera aleatoria pero controlada
        while tickets_restantes > 0:
            # Elegir un proceso aleatorio
            idx = random.randint(0, cantidad - 1)
            # Darle un ticket
            tickets[idx] += 1
            tickets_restantes -= 1
        
        # VERIFICACIÓN FINAL (debugging)
        suma_final = sum(tickets)
        if suma_final != pool_total:
            # Esto NO debería ocurrir nunca con este algoritmo
            messagebox.showerror("Error Crítico", 
                f"Error en distribución: suma={suma_final}, esperado={pool_total}")
            return []
        
        # Mezclar la lista para que no siempre los primeros tengan más
        random.shuffle(tickets)
        
        return tickets
    
    def limpiar_procesos(self):
        """Limpia la lista de procesos"""
        if self.simulacion_activa:
            messagebox.showwarning("Advertencia", "No puedes limpiar durante la simulación")
            return
        
        if len(self.procesos_creados) == 0:
            return
            
        respuesta = messagebox.askyesno("Confirmar", "¿Deseas limpiar todos los procesos?")
        if respuesta:
            self.procesos_creados.clear()
            self.actualizar_lista_procesos()
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, "1")
    
    def actualizar_lista_procesos(self):
        """Actualiza la lista visual de procesos"""
        self.listbox_procesos.delete(0, tk.END)
        for p in self.procesos_creados:
            texto = f"P{p.identificador:2d} | CPU:{p.tiempo_cpu:2d} | Pri:{p.prioridad} | Tkt:{p.num_tickets:3d}"
            if p.proceso_servidor != 0:
                texto += f" | Srv:P{p.proceso_servidor}"
            self.listbox_procesos.insert(tk.END, texto)
            self.listbox_procesos.itemconfig(tk.END, bg=p.color)
    
    def iniciar_simulacion(self):
        """Inicia la simulación"""
        if len(self.procesos_creados) == 0:
            messagebox.showwarning("Advertencia", 
                                 "Debes agregar al menos un proceso antes de iniciar.\n\n"
                                 "Usa 'Agregar Proceso' o 'Aleatorios'.")
            return
        
        try:
            quantum = int(self.entry_quantum.get())
            if quantum <= 0:
                messagebox.showerror("Error", "El quantum debe ser mayor a 0")
                return
            
            velocidad = self.scale_velocidad.get()
            usar_manual = self.var_tickets_manual.get()
            
            # Pool de tickets globales
            pool_global = None
            if self.var_pool_global.get():
                pool_global = int(self.entry_pool.get())
                if pool_global <= 0:
                    messagebox.showerror("Error", "El pool de tickets debe ser mayor a 0")
                    return
            
            # Crear simulador
            self.simulador = SimuladorLoteria(quantum=quantum, velocidad=velocidad, 
                                             usar_tickets_manual=usar_manual,
                                             pool_tickets_global=pool_global)
            
            # Agregar procesos al simulador (copias para no modificar originales)
            for p in self.procesos_creados:
                proceso_copia = Proceso(
                    identificador=p.identificador,
                    tiempo_cpu=p.tiempo_cpu,
                    prioridad=p.prioridad,
                    proceso_servidor=p.proceso_servidor
                )
                proceso_copia.num_tickets = p.num_tickets
                proceso_copia.num_tickets_original = p.num_tickets_original
                proceso_copia.color = p.color
                self.simulador.agregar_proceso(proceso_copia)
            
            # Manejar préstamo de tickets cliente-servidor
            for p in self.simulador.cola_listos:
                if p.es_cliente():
                    for servidor in self.simulador.cola_listos:
                        if servidor.identificador == p.proceso_servidor:
                            self.simulador._prestar_tickets(p, servidor)
                            break
            
            # Cambiar estado de botones
            self.btn_iniciar.config(state=tk.DISABLED)
            self.btn_pausar.config(state=tk.NORMAL)
            self.btn_es.config(state=tk.NORMAL)
            self.btn_agregar.config(state=tk.DISABLED)
            self.btn_aleatorio.config(state=tk.DISABLED)
            self.btn_limpiar.config(state=tk.DISABLED)
            
            self.simulacion_activa = True
            
            # Limpiar visualizaciones
            self.text_analisis.delete(1.0, tk.END)
            self.text_analisis.insert(tk.END, "Esperando primer sorteo...")
            self.text_stats.delete(1.0, tk.END)
            
            # Iniciar thread de simulación
            self.thread_simulacion = threading.Thread(target=self.ejecutar_simulacion)
            self.thread_simulacion.daemon = True
            self.thread_simulacion.start()
            
        except ValueError:
            messagebox.showerror("Error", "Los valores deben ser números válidos")
    
    def ejecutar_simulacion(self):
        """Ejecuta la simulación en un thread separado"""
        try:
            while self.simulacion_activa and self.simulador.ejecutar_ciclo():
                velocidad = self.scale_velocidad.get()
                time.sleep(1.0 / velocidad)
                self.root.after(0, self.actualizar_interfaz)
            
            # Simulación terminada
            self.root.after(0, self.simulacion_terminada)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", 
                                                            f"Error en simulación:\n{str(e)}"))
    
    def actualizar_interfaz(self):
        """Actualiza todos los elementos visuales de la interfaz"""
        if not self.simulador:
            return
        
        # Actualizar labels de estado
        self.label_tiempo.config(text=str(self.simulador.tiempo_actual))
        self.label_quantum_rest.config(text=str(self.simulador.tiempo_quantum_restante))
        
        if self.simulador.ticket_sorteado:
            self.label_ticket.config(
                text=f"{self.simulador.ticket_sorteado}/{self.simulador.total_tickets_actual}")
        
        self.label_evento.config(text=self.simulador.ultimo_evento)
        
        # Actualizar proceso ejecutando
        if self.simulador.proceso_actual:
            texto = f"P{self.simulador.proceso_actual.identificador}\n"
            texto += f"CPU: {self.simulador.proceso_actual.tiempo_restante}/"
            texto += f"{self.simulador.proceso_actual.tiempo_cpu}"
            self.label_proc_ejecutando.config(text=texto, 
                                             bg=self.simulador.proceso_actual.color)
        else:
            self.label_proc_ejecutando.config(text="CPU IDLE", bg='white')
        
        # Actualizar tabla de cola de listos
        self.tree_cola.delete(*self.tree_cola.get_children())
        for p in self.simulador.cola_listos:
            valores = (
                f"P{p.identificador}",
                p.num_tickets,
                f"{p.tiempo_restante}/{p.tiempo_cpu}",
                p.prioridad,
                f"P{p.proceso_servidor}" if p.proceso_servidor != 0 else "-"
            )
            item = self.tree_cola.insert('', tk.END, values=valores)
            self.tree_cola.tag_configure(f'color_{p.identificador}', background=p.color)
            self.tree_cola.item(item, tags=(f'color_{p.identificador}',))
        
        # Actualizar procesos terminados
        self.label_terminados.config(
            text=f"{len(self.simulador.procesos_terminados)} procesos")
        
        # Actualizar análisis del último sorteo
        if hasattr(self.simulador, 'ultimo_analisis') and self.simulador.ultimo_analisis:
            self.text_analisis.delete(1.0, tk.END)
            self.text_analisis.insert(tk.END, self.simulador.ultimo_analisis['explicacion'])
        
        # Dibujar en canvas
        self.dibujar_estado()
    
    def dibujar_estado(self):
        """Dibuja el estado actual en el canvas"""
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Título
        self.canvas.create_text(width/2, 20, text="ESTADO DEL SISTEMA", 
                               font=('Arial', 14, 'bold'), fill='#2c3e50')
        
        # Dibujar CPU/Procesador
        cpu_y = 60
        self.canvas.create_rectangle(width/2 - 120, cpu_y, width/2 + 120, cpu_y + 90, 
                                     fill='#3498db', outline='#2c3e50', width=3)
        self.canvas.create_text(width/2, cpu_y + 20, text="PROCESADOR", 
                               font=('Arial', 13, 'bold'), fill='white')
        
        if self.simulador and self.simulador.proceso_actual:
            p = self.simulador.proceso_actual
            self.canvas.create_rectangle(width/2 - 70, cpu_y + 40, 
                                        width/2 + 70, cpu_y + 75,
                                        fill=p.color, outline='#2c3e50', width=2)
            self.canvas.create_text(width/2, cpu_y + 57, 
                                   text=f"P{p.identificador} (CPU:{p.tiempo_restante})", 
                                   font=('Arial', 12, 'bold'))
        else:
            self.canvas.create_text(width/2, cpu_y + 57, text="IDLE", 
                                   font=('Arial', 12, 'bold'), fill='white')
        
        # Dibujar cola de listos
        cola_y = 180
        self.canvas.create_text(width/2, cola_y, text="COLA DE LISTOS", 
                               font=('Arial', 13, 'bold'), fill='#2c3e50')
        
        if self.simulador and self.simulador.cola_listos:
            num_procesos = len(self.simulador.cola_listos)
            espacio = min(110, (width - 40) / max(num_procesos, 1))
            inicio_x = (width - (espacio * num_procesos)) / 2
            
            for i, p in enumerate(self.simulador.cola_listos):
                x = inicio_x + (i * espacio) + espacio/2
                y = cola_y + 50
                
                # Rectángulo del proceso
                self.canvas.create_rectangle(x - 40, y - 30, x + 40, y + 30, 
                                            fill=p.color, outline='#2c3e50', width=2)
                self.canvas.create_text(x, y - 15, text=f"P{p.identificador}", 
                                       font=('Arial', 11, 'bold'))
                self.canvas.create_text(x, y, text=f"T:{p.num_tickets}", 
                                       font=('Arial', 9))
                self.canvas.create_text(x, y + 13, text=f"CPU:{p.tiempo_restante}", 
                                       font=('Arial', 8))
        else:
            self.canvas.create_text(width/2, cola_y + 50, text="(vacía)", 
                                   font=('Arial', 11, 'italic'), fill='#7f8c8d')
        
        # Dibujar procesos terminados
        term_y = cola_y + 130
        self.canvas.create_text(width/2, term_y, text="PROCESOS TERMINADOS", 
                               font=('Arial', 13, 'bold'), fill='#27ae60')
        
        if self.simulador and self.simulador.procesos_terminados:
            num_term = min(len(self.simulador.procesos_terminados), 12)
            espacio = min(90, (width - 40) / max(num_term, 1))
            inicio_x = (width - (espacio * num_term)) / 2
            
            for i, p in enumerate(self.simulador.procesos_terminados[:12]):
                x = inicio_x + (i * espacio) + espacio/2
                y = term_y + 35
                
                self.canvas.create_oval(x - 22, y - 22, x + 22, y + 22, 
                                       fill='#27ae60', outline='#2c3e50', width=2)
                self.canvas.create_text(x, y, text=f"P{p.identificador}", 
                                       font=('Arial', 10, 'bold'), fill='white')
            
            if len(self.simulador.procesos_terminados) > 12:
                self.canvas.create_text(width/2, term_y + 70, 
                                       text=f"...y {len(self.simulador.procesos_terminados) - 12} más", 
                                       font=('Arial', 9, 'italic'), fill='#27ae60')
        else:
            self.canvas.create_text(width/2, term_y + 35, text="(ninguno)", 
                                   font=('Arial', 11, 'italic'), fill='#7f8c8d')
    
    def pausar_simulacion(self):
        """Pausa o reanuda la simulación"""
        if not self.simulador:
            return
        
        if self.simulador.pausado:
            self.simulador.reanudar()
            self.btn_pausar.config(text="PAUSAR")
        else:
            self.simulador.pausar()
            self.btn_pausar.config(text="▶ REANUDAR")
    
    def simular_entrada_salida(self):
        """Simula una operación de entrada/salida"""
        if self.simulador and self.simulador.proceso_actual:
            pid = self.simulador.proceso_actual.identificador
            self.simulador.simular_entrada_salida()
            messagebox.showinfo("E/S Simulada", 
                              f"Proceso P{pid} bloqueado por operación de E/S.\n"
                              f"Fue devuelto a la cola de listos.")
        else:
            messagebox.showwarning("Advertencia", "No hay proceso ejecutándose actualmente")
    
    def reiniciar_todo(self):
        """Reinicia completamente el simulador y limpia todo"""
        respuesta = messagebox.askyesno("Confirmar Reinicio", 
                                        "¿Deseas reiniciar completamente el simulador?\n\n"
                                        "Esto detendrá la simulación actual y limpiará\n"
                                        "todos los datos, pero mantendrá los procesos creados.")
        if not respuesta:
            return
        
        # Detener simulación
        self.simulacion_activa = False
        
        # Esperar a que termine el thread
        if self.thread_simulacion and self.thread_simulacion.is_alive():
            self.thread_simulacion.join(timeout=3)
        
        # Limpiar simulador
        self.simulador = None
        
        # Resetear interfaz
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_pausar.config(state=tk.DISABLED, text="PAUSAR")
        self.btn_es.config(state=tk.DISABLED)
        self.btn_agregar.config(state=tk.NORMAL)
        self.btn_aleatorio.config(state=tk.NORMAL)
        self.btn_limpiar.config(state=tk.NORMAL)
        
        self.label_tiempo.config(text="0")
        self.label_quantum_rest.config(text="0")
        self.label_ticket.config(text="N/A")
        self.label_evento.config(text="Sistema reiniciado - Listo para nueva simulación")
        self.label_proc_ejecutando.config(text="NINGUNO", bg='white')
        self.label_terminados.config(text="0 procesos")
        
        self.text_analisis.delete(1.0, tk.END)
        self.text_analisis.insert(tk.END, "Sistema reiniciado.\nEsperando nueva simulación...")
        
        self.text_stats.delete(1.0, tk.END)
        
        self.tree_cola.delete(*self.tree_cola.get_children())
        self.canvas.delete("all")
        
        messagebox.showinfo("Reinicio Completo", 
                        "El simulador ha sido reiniciado.\n"
                        "Los procesos creados se mantienen.\n\n"
                        "Puedes iniciar una nueva simulación cuando quieras.")
    
    def simulacion_terminada(self):
        """Maneja el fin de la simulación y muestra análisis completo"""
        self.simulacion_activa = False
        
        # Verificar que el simulador existe
        if not self.simulador:
            return
        
        self.btn_pausar.config(state=tk.DISABLED)
        self.btn_es.config(state=tk.DISABLED)
        
        # Mostrar estadísticas y análisis
        stats= self.simulador.obtener_estadisticas()
        if stats:
            self.text_stats.delete(1.0, tk.END)
            
            # Estadísticas numéricas básicas
            self.text_stats.insert(tk.END, "="*50 + "\n")
            self.text_stats.insert(tk.END, "ESTADISTICAS FINALES DE LA SIMULACION\n")
            self.text_stats.insert(tk.END, "="*50 + "\n\n")
            self.text_stats.insert(tk.END, f"Tiempo total de simulacion: {stats['tiempo_total']} ciclos\n")
            self.text_stats.insert(tk.END, f"Procesos terminados: {stats['procesos_terminados']}\n")
            self.text_stats.insert(tk.END, f"Quantum utilizado: {self.simulador.quantum} ciclos\n")
            
            if self.simulador.pool_tickets_global:
                self.text_stats.insert(tk.END, f"Pool de tickets globales: {self.simulador.pool_tickets_global}\n")
            
            self.text_stats.insert(tk.END, "\n")
            
            self.text_stats.insert(tk.END, "METRICAS DE RENDIMIENTO:\n")
            self.text_stats.insert(tk.END, "-"*50 + "\n")
            self.text_stats.insert(tk.END, f"Tiempo de espera promedio: {stats['tiempo_espera_promedio']:.2f} ciclos\n")
            self.text_stats.insert(tk.END, f"Tiempo de retorno promedio: {stats['tiempo_retorno_promedio']:.2f} ciclos\n")
            self.text_stats.insert(tk.END, f"Tiempo de respuesta promedio: {stats['tiempo_respuesta_promedio']:.2f} ciclos\n\n")
            
            # Detalle por proceso
            self.text_stats.insert(tk.END, "DETALLE POR PROCESO:\n")
            self.text_stats.insert(tk.END, "-"*50 + "\n")
            self.text_stats.insert(tk.END, "Proc | Espera | Retorno | Respuesta | CPU Total\n")
            self.text_stats.insert(tk.END, "-"*50 + "\n")
            
            for p in stats['procesos']:
                respuesta = p.tiempo_inicio_ejecucion - p.tiempo_llegada
                self.text_stats.insert(tk.END, 
                    f" P{p.identificador:2d} |  {p.tiempo_espera:4d}  |  {p.tiempo_retorno:5d}  |"
                    f"   {respuesta:6d}  |    {p.tiempo_cpu:3d}\n")
            
            self.text_stats.insert(tk.END, "\n\n")
            
            # ANÁLISIS COMPLETO DE ORDEN DE FINALIZACIÓN
            analisis_orden = self.simulador.analizador.generar_analisis_orden_finalizacion(
                stats['procesos']
            )
            self.text_stats.insert(tk.END, analisis_orden)
            
            self.text_stats.insert(tk.END, "\n\n")
            
            # Resumen estadístico de sorteos
            resumen = self.simulador.analizador.obtener_resumen_estadistico()
            self.text_stats.insert(tk.END, resumen)
            
            # Mensaje final
            messagebox.showinfo("Simulación Terminada", 
                            "La simulación ha finalizado exitosamente.\n\n"
                            "Revisa la sección 'Estadísticas y Resultados Finales'\n"
                            "para ver el análisis completo de por qué cada\n"
                            "proceso terminó en su posición específica.\n\n"
                            "Usa el scroll para ver todo el análisis.\n\n"
                            "Puedes usar 'REINICIAR TODO' para una nueva simulación.")

def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    app = InterfazSimulador(root)
    
    # Mensaje de bienvenida
    messagebox.showinfo("Bienvenido al Simulador", 
                       "SIMULADOR DE PLANIFICACIÓN POR LOTERÍA\n\n"
                       "Características:\n"
                       "✓ Configuración de cantidad de procesos aleatorios\n"
                       "✓ Distribución inteligente de tickets con pool global\n"
                       "✓ Los tickets se reparten automáticamente\n"
                       "✓ Análisis teórico detallado\n"
                       "✓ Scroll en ambos paneles laterales\n\n"
                       "Instrucciones:\n"
                       "1. Opcional: Activa 'pool de tickets globales'\n"
                       "2. Opcional: Activa 'configurar tickets manualmente'\n"
                       "3. Define cantidad de procesos aleatorios (ej: 4)\n"
                       "4. Presiona 'Aleatorios' para crear procesos\n"
                       "   (Si pool está activo, tickets se distribuyen automáticamente)\n"
                       "5. Configura Quantum y velocidad\n"
                       "6. Presiona 'INICIAR SIMULACIÓN'\n\n"
                       "EJEMPLO:\n"
                       "Pool global: 30 tickets\n"
                       "Cantidad: 4 procesos\n"
                       "Resultado: P1=10, P2=6, P3=4, P4=10 (suma 30)")
    
    root.mainloop()

if __name__ == "__main__":
    main()