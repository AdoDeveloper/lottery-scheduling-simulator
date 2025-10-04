"""
Módulo con la lógica del simulador de planificación por lotería.
Autor: @Adolfo Cortez
Implementa el algoritmo de Waldspurger & Weihl (1994).
"""

import random
from proceso import Proceso
from analizador import AnalizadorLoteria

class SimuladorLoteria:
    """
    Simulador del algoritmo de planificación por lotería.
    
    Características:
    - Sorteo aleatorio basado en tickets
    - Asignación proporcional de CPU
    - Prevención de inanición mediante bonus por espera
    - Configuración de pool de tickets globales
    """
    
    def __init__(self, quantum=2, velocidad=1.0, usar_tickets_manual=False, pool_tickets_global=None):
        self.cola_listos = []
        self.proceso_actual = None
        self.procesos_terminados = []
        self.tiempo_actual = 0
        self.quantum = quantum
        self.tiempo_quantum_restante = 0
        self.historial = []
        self.velocidad = velocidad
        self.ticket_sorteado = None
        self.total_tickets_actual = 0
        self.ultimo_evento = "Sistema inicializado"
        self.pausado = False
        self.servidores_ejecutados = set()
        self.analizador = AnalizadorLoteria()
        self.ultimo_analisis = None
        self.usar_tickets_manual = usar_tickets_manual
        self.pool_tickets_global = pool_tickets_global  # None = usar tickets de procesos
        
    def agregar_proceso(self, proceso):
        """
        Agrega un proceso a la cola de listos.
        Asigna tickets según prioridad o usa tickets manuales.
        """
        # ═══════════════════════════════════════════════════════════════════
        # PASO 1: INICIALIZACIÓN DE PROCESO
        # ═══════════════════════════════════════════════════════════════════
        # Al agregar un proceso, se le asigna estado LISTO y se añade a la
        # cola de procesos elegibles para el sorteo de lotería.
        # ═══════════════════════════════════════════════════════════════════
        proceso.estado = "LISTO"
        self.cola_listos.append(proceso)
        
        # ═══════════════════════════════════════════════════════════════════
        # PASO 2: ASIGNACIÓN DE TICKETS
        # ═══════════════════════════════════════════════════════════════════
        # Si no se usan tickets manuales, se asignan automáticamente según
        # la prioridad del proceso y el tiempo de espera (anti-inanición).
        # ═══════════════════════════════════════════════════════════════════
        if not self.usar_tickets_manual:
            self._asignar_tickets()
            
        self.ultimo_evento = f"Proceso P{proceso.identificador} agregado (Prioridad: {proceso.prioridad}, CPU: {proceso.tiempo_cpu}, Tickets: {proceso.num_tickets})"
        return True
        
    def _asignar_tickets(self):
        """
        Asigna tickets a los procesos según:
        1. Prioridad (tickets base = prioridad × 10)
        2. Tiempo de espera (bonus = espera // 5)
        
        Esto implementa:
        - Justicia proporcional (más prioridad = más tickets)
        - Anti-inanición (más espera = más tickets)
        """
        # ═══════════════════════════════════════════════════════════════════
        # ASIGNACIÓN DINÁMICA DE TICKETS
        # ═══════════════════════════════════════════════════════════════════
        # Cada proceso recibe tickets basados en:
        # 1. Tickets base proporcionales a su prioridad (control de recursos)
        # 2. Bonus por tiempo de espera (prevención de inanición)
        # Esto garantiza justicia proporcional y progreso de todos los procesos.
        # ═══════════════════════════════════════════════════════════════════
        for proceso in self.cola_listos:
            # Tickets base según prioridad (refleja importancia del proceso)
            tickets_base = proceso.prioridad * 10
            
            # Bonus por tiempo de espera (evita inanición - cada 5 unidades de espera = 1 ticket extra)
            bonus_espera = proceso.tiempo_espera // 5
            
            # Total de tickets = base + bonus
            proceso.num_tickets = tickets_base + bonus_espera
            
    def _total_tickets(self):
        """
        Calcula el total de tickets de procesos que pueden ejecutarse.
        """
        # ═══════════════════════════════════════════════════════════════════
        # CÁLCULO DEL POOL DE TICKETS
        # ═══════════════════════════════════════════════════════════════════
        # Determina el total de tickets disponibles para el sorteo:
        # - Con pool global: usa un número fijo de tickets
        # - Sin pool global: suma los tickets de todos los procesos elegibles
        # ═══════════════════════════════════════════════════════════════════
        if self.pool_tickets_global is not None:
            # Modo pool global: número fijo de tickets
            return self.pool_tickets_global
        
        # Modo estándar: suma de tickets de procesos elegibles
        total = 0
        for p in self.cola_listos:
            if p.puede_ejecutarse(self.servidores_ejecutados):
                total += p.num_tickets
        return total
    
    def _sortear_proceso(self):
        """
        Realiza el sorteo de lotería para seleccionar el siguiente proceso.
        
        Con pool global: sortea del 1 al pool_total, luego asigna proporcionalmente
        Sin pool global: sortea entre la suma de tickets de todos los procesos
        """
        # ═══════════════════════════════════════════════════════════════════
        # PASO 3: FILTRADO DE PROCESOS ELEGIBLES
        # ═══════════════════════════════════════════════════════════════════
        # Identifica qué procesos pueden ejecutarse actualmente (sin dependencias
        # bloqueantes). Solo estos participan en el sorteo de lotería.
        # ═══════════════════════════════════════════════════════════════════
        procesos_validos = [p for p in self.cola_listos 
                        if p.puede_ejecutarse(self.servidores_ejecutados)]
        
        if not procesos_validos:
            self.ultimo_evento = "No hay procesos válidos para ejecutar"
            return None
        
        # ═══════════════════════════════════════════════════════════════════
        # PASO 4: DETERMINACIÓN DEL RANGO DE SORTEO
        # ═══════════════════════════════════════════════════════════════════
        # Calcula el total de tickets que participan en el sorteo:
        # - Pool global fijo: siempre el mismo rango
        # - Pool dinámico: suma de tickets de procesos válidos
        # ═══════════════════════════════════════════════════════════════════
        if self.pool_tickets_global is not None:
            # USO DE POOL GLOBAL: siempre sortear del pool fijo
            total_tickets = self.pool_tickets_global
        else:
            # SIN POOL GLOBAL: sumar tickets de todos los procesos
            total_tickets = sum(p.num_tickets for p in procesos_validos)
        
        if total_tickets == 0:
            self.ultimo_evento = "Total de tickets es 0"
            return None
            
        # ═══════════════════════════════════════════════════════════════════
        # PASO 5: SORTEO ALEATORIO
        # ═══════════════════════════════════════════════════════════════════
        # NÚCLEO DEL ALGORITMO: Genera un número aleatorio entre 1 y total_tickets
        # Este sorteo probabilístico garantiza que cada proceso tenga una
        # probabilidad de ser elegido proporcional a sus tickets.
        # Probabilidad(proceso_i) = tickets_i / total_tickets
        # ═══════════════════════════════════════════════════════════════════
        ticket_ganador = random.randint(1, total_tickets)
        self.ticket_sorteado = ticket_ganador
        self.total_tickets_actual = total_tickets
        
        # ═══════════════════════════════════════════════════════════════════
        # PASO 6: IDENTIFICACIÓN DEL GANADOR
        # ═══════════════════════════════════════════════════════════════════
        # Determina qué proceso es dueño del ticket sorteado mediante
        # acumulación de tickets (método de distribución proporcional).
        # ═══════════════════════════════════════════════════════════════════
        if self.pool_tickets_global is not None:
            # ───────────────────────────────────────────────────────────────
            # MODO POOL GLOBAL: Distribución proporcional
            # ───────────────────────────────────────────────────────────────
            # Calcula suma de tickets de procesos válidos
            suma_tickets_procesos = sum(p.num_tickets for p in procesos_validos)
            
            if suma_tickets_procesos == 0:
                # Si todos tienen 0 tickets, distribución equitativa (round-robin)
                proceso_ganador = random.choice(procesos_validos)
            else:
                # Mapear el ticket ganador a un proceso proporcionalmente
                # Cada proceso tiene una "porción" del pool proporcional a sus tickets
                acumulado = 0
                for proceso in procesos_validos:
                    # Calcular cuántos tickets del pool le corresponden a este proceso
                    proporcion = proceso.num_tickets / suma_tickets_procesos
                    tickets_en_pool = proporcion * total_tickets
                    acumulado += tickets_en_pool
                    
                    # Si el ticket ganador cae en el rango de este proceso, él gana
                    if ticket_ganador <= acumulado:
                        proceso_ganador = proceso
                        break
                else:
                    # Por si acaso hay error de redondeo, asignar al último
                    proceso_ganador = procesos_validos[-1]
        else:
            # ───────────────────────────────────────────────────────────────
            # MODO ESTÁNDAR: Método acumulativo directo
            # ───────────────────────────────────────────────────────────────
            # Acumula tickets hasta encontrar el proceso cuyo rango contiene
            # el ticket ganador. Ejemplo:
            # P1 tiene tickets 1-30, P2 tiene 31-50, P3 tiene 51-100
            # Si sorteo = 45, gana P2
            # ───────────────────────────────────────────────────────────────
            acumulado = 0
            proceso_ganador = None
            for proceso in procesos_validos:
                acumulado += proceso.num_tickets
                if ticket_ganador <= acumulado:
                    proceso_ganador = proceso
                    break
        
        # ═══════════════════════════════════════════════════════════════════
        # PASO 7: REGISTRO Y ANÁLISIS
        # ═══════════════════════════════════════════════════════════════════
        # Registra el resultado del sorteo para análisis estadístico y
        # verificación de justicia proporcional del algoritmo.
        # ═══════════════════════════════════════════════════════════════════
        if proceso_ganador:
            # Analizar el sorteo con explicaciones teóricas
            self.ultimo_analisis = self.analizador.analizar_sorteo(
                ticket_ganador, total_tickets, proceso_ganador, procesos_validos
            )
            self.ultimo_evento = f"Sorteo: Ticket {ticket_ganador}/{total_tickets} -> P{proceso_ganador.identificador} GANA"
        
        return proceso_ganador
    
    def _prestar_tickets(self, cliente, servidor):
        """
        Cliente presta sus tickets a su servidor.
        """
        # ═══════════════════════════════════════════════════════════════════
        # TRANSFERENCIA DE TICKETS
        # ═══════════════════════════════════════════════════════════════════
        # Mecanismo de inversión de prioridad: cuando un cliente necesita
        # un servidor, le transfiere sus tickets temporalmente para
        # incrementar la probabilidad de que el servidor ejecute y libere
        # el recurso compartido. Previene inversión de prioridad.
        # ═══════════════════════════════════════════════════════════════════
        if servidor in self.cola_listos:
            tickets_prestados = cliente.num_tickets
            servidor.tickets_prestados += tickets_prestados
            servidor.num_tickets += tickets_prestados
            cliente.tickets_prestados = tickets_prestados
            cliente.num_tickets = 0
            self.ultimo_evento = f"P{cliente.identificador} presta {tickets_prestados} tickets a P{servidor.identificador}"
            return True
        return False
    
    def _devolver_tickets(self, servidor):
        """
        Servidor devuelve tickets a sus clientes después de ejecutarse.
        """
        # ═══════════════════════════════════════════════════════════════════
        # DEVOLUCIÓN DE TICKETS
        # ═══════════════════════════════════════════════════════════════════
        # Una vez el servidor completa su ejecución, devuelve los tickets
        # prestados a sus clientes, restaurando las prioridades originales.
        # ═══════════════════════════════════════════════════════════════════
        for proceso in self.cola_listos:
            if proceso.proceso_servidor == servidor.identificador and proceso.tickets_prestados > 0:
                proceso.num_tickets += proceso.tickets_prestados
                servidor.num_tickets -= proceso.tickets_prestados
                servidor.tickets_prestados -= proceso.tickets_prestados
                self.ultimo_evento = f"P{servidor.identificador} devuelve {proceso.tickets_prestados} tickets a P{proceso.identificador}"
                proceso.tickets_prestados = 0
    
    def ejecutar_ciclo(self):
        """
        Ejecuta un ciclo de reloj del simulador.
        
        Pasos:
        1. Actualizar tiempos de espera
        2. Si no hay proceso ejecutando o se acabó quantum -> sortear
        3. Ejecutar proceso actual
        4. Verificar si terminó
        5. Guardar historial
        
        Returns:
            bool: True si hay procesos pendientes, False si terminó
        """
        if self.pausado:
            return True
        
        # ═══════════════════════════════════════════════════════════════════
        # CICLO PRINCIPAL DE SIMULACIÓN
        # ═══════════════════════════════════════════════════════════════════
        # Cada ciclo representa una unidad de tiempo del CPU donde se:
        # 1. Actualiza métricas de tiempo
        # 2. Realiza sorteo si es necesario
        # 3. Ejecuta el proceso ganador
        # 4. Verifica completitud
        # ═══════════════════════════════════════════════════════════════════
        
        self.tiempo_actual += 1
        
        # ───────────────────────────────────────────────────────────────────
        # PASO A: Actualización de tiempos de espera
        # ───────────────────────────────────────────────────────────────────
        # Incrementa el tiempo de espera de procesos que NO están ejecutando.
        # Este tiempo se usa para calcular el bonus anti-inanición.
        # ───────────────────────────────────────────────────────────────────
        for proceso in self.cola_listos:
            if proceso != self.proceso_actual:
                proceso.tiempo_espera += 1
        
        # ───────────────────────────────────────────────────────────────────
        # PASO B: Decisión de sorteo
        # ───────────────────────────────────────────────────────────────────
        # Se realiza un nuevo sorteo cuando:
        # - No hay proceso ejecutándose actualmente, O
        # - El quantum del proceso actual se agotó (expulsión por tiempo)
        # ───────────────────────────────────────────────────────────────────
        if self.proceso_actual is None or self.tiempo_quantum_restante == 0:
            if self.proceso_actual and self.proceso_actual.tiempo_restante > 0:
                # ═══════════════════════════════════════════════════════════
                # EXPULSIÓN POR QUANTUM AGOTADO
                # ═══════════════════════════════════════════════════════════
                # El proceso no terminó pero consumió su quantum completo.
                # Se devuelve a la cola de listos para participar en el
                # siguiente sorteo (garantiza justicia temporal).
                # ═══════════════════════════════════════════════════════════
                self.ultimo_evento = f"P{self.proceso_actual.identificador} EXPULSADO (quantum agotado)"
                self.proceso_actual.estado = "LISTO"
                self.cola_listos.append(self.proceso_actual)
                self.proceso_actual = None
            
            # ═══════════════════════════════════════════════════════════════
            # REASIGNACIÓN DE TICKETS ANTES DEL SORTEO
            # ═══════════════════════════════════════════════════════════════
            # Actualiza los tickets de todos los procesos considerando:
            # - Prioridad base (no cambia)
            # - Bonus por tiempo de espera (aumenta con el tiempo)
            # Esto mantiene la justicia del sistema a largo plazo.
            # ═══════════════════════════════════════════════════════════════
            if not self.usar_tickets_manual:
                self._asignar_tickets()
            
            # ═══════════════════════════════════════════════════════════════
            # REALIZACIÓN DEL SORTEO DE LOTERÍA
            # ═══════════════════════════════════════════════════════════════
            # Ejecuta el mecanismo central del algoritmo: sorteo probabilístico
            # basado en la distribución de tickets entre los procesos elegibles.
            # ═══════════════════════════════════════════════════════════════
            proceso_ganador = self._sortear_proceso()
            
            if proceso_ganador:
                # ───────────────────────────────────────────────────────────
                # Proceso ganador encontrado: preparar para ejecución
                # ───────────────────────────────────────────────────────────
                self.cola_listos.remove(proceso_ganador)
                self.proceso_actual = proceso_ganador
                self.proceso_actual.estado = "EJECUTANDO"
                self.tiempo_quantum_restante = self.quantum
                
                # Registrar primera vez que ejecuta (métrica de tiempo de respuesta)
                if self.proceso_actual.tiempo_inicio_ejecucion == -1:
                    self.proceso_actual.tiempo_inicio_ejecucion = self.tiempo_actual
                
                # Si es servidor, devolver tickets a clientes (fin de inversión de prioridad)
                self._devolver_tickets(self.proceso_actual)
        
        # ───────────────────────────────────────────────────────────────────
        # PASO C: Ejecución del proceso actual
        # ───────────────────────────────────────────────────────────────────
        # El proceso ganador del sorteo consume una unidad de tiempo del CPU
        # y una unidad de su quantum asignado.
        # ───────────────────────────────────────────────────────────────────
        if self.proceso_actual:
            self.proceso_actual.tiempo_restante -= 1
            self.tiempo_quantum_restante -= 1
            self.ultimo_evento = f"EJECUTANDO P{self.proceso_actual.identificador} (Restante: {self.proceso_actual.tiempo_restante}, Quantum: {self.tiempo_quantum_restante})"
            
            # ═══════════════════════════════════════════════════════════════
            # PASO D: Verificación de completitud
            # ═══════════════════════════════════════════════════════════════
            # Si el proceso terminó toda su ráfaga de CPU:
            # - Se marca como TERMINADO
            # - Se calcula su tiempo de retorno (métrica de rendimiento)
            # - Se añade a la lista de procesos completados
            # ═══════════════════════════════════════════════════════════════
            if self.proceso_actual.tiempo_restante == 0:
                self.proceso_actual.estado = "TERMINADO"
                self.proceso_actual.tiempo_retorno = (self.tiempo_actual - 
                                                     self.proceso_actual.tiempo_llegada)
                self.procesos_terminados.append(self.proceso_actual)
                self.servidores_ejecutados.add(self.proceso_actual.identificador)
                self.ultimo_evento = f"P{self.proceso_actual.identificador} TERMINADO (Tiempo retorno: {self.proceso_actual.tiempo_retorno})"
                self.proceso_actual = None
                self.tiempo_quantum_restante = 0
        else:
            # CPU inactiva: no hay procesos elegibles para ejecutar
            self.ultimo_evento = "CPU IDLE - No hay procesos para ejecutar"
        
        # ───────────────────────────────────────────────────────────────────
        # PASO E: Registro del historial
        # ───────────────────────────────────────────────────────────────────
        # Guarda el estado actual para análisis posterior y visualización
        # de la ejecución del algoritmo.
        # ───────────────────────────────────────────────────────────────────
        self._guardar_historial()
        
        # Continuar si hay procesos pendientes
        return len(self.cola_listos) > 0 or self.proceso_actual is not None
    
    def _guardar_historial(self):
        """
        Guarda el estado actual en el historial para análisis posterior.
        """
        # ═══════════════════════════════════════════════════════════════════
        # TRAZABILIDAD DEL SISTEMA
        # ═══════════════════════════════════════════════════════════════════
        # Registra el estado completo del sistema en cada ciclo para:
        # - Análisis de justicia proporcional
        # - Verificación de ausencia de inanición
        # - Visualización de la ejecución
        # - Validación del algoritmo
        # ═══════════════════════════════════════════════════════════════════
        estado = {
            'tiempo': self.tiempo_actual,
            'proceso_ejecutando': self.proceso_actual.identificador if self.proceso_actual else None,
            'cola_listos': [p.identificador for p in self.cola_listos],
            'terminados': len(self.procesos_terminados),
            'evento': self.ultimo_evento,
            'ticket_sorteado': self.ticket_sorteado,
            'total_tickets': self.total_tickets_actual
        }
        self.historial.append(estado)
    
    def simular_entrada_salida(self):
        """
        Simula una operación de E/S que bloquea el proceso actual.
        El proceso vuelve a la cola de listos.
        """
        # ═══════════════════════════════════════════════════════════════════
        # BLOQUEO POR E/S
        # ═══════════════════════════════════════════════════════════════════
        # Cuando un proceso realiza una operación de E/S:
        # - Se expulsa del CPU (libera el procesador)
        # - Retorna a la cola de listos (volverá a participar en sorteos)
        # - Su quantum se reinicia (nueva oportunidad de ejecución completa)
        # ═══════════════════════════════════════════════════════════════════
        if self.proceso_actual:
            self.ultimo_evento = f"E/S: P{self.proceso_actual.identificador} enviado a cola de listos"
            self.proceso_actual.estado = "LISTO"
            self.cola_listos.append(self.proceso_actual)
            self.proceso_actual = None
            self.tiempo_quantum_restante = 0
            return True
        return False
    
    def obtener_estadisticas(self):
        """
        Calcula y retorna estadísticas finales de la simulación.
        
        Returns:
            dict: Diccionario con todas las métricas de rendimiento
        """
        # ═══════════════════════════════════════════════════════════════════
        # MÉTRICAS DE RENDIMIENTO
        # ═══════════════════════════════════════════════════════════════════
        # Calcula las métricas estándar para evaluar el rendimiento del
        # algoritmo de planificación:
        # - Tiempo de espera: tiempo que el proceso pasó en cola de listos
        # - Tiempo de retorno: tiempo total desde llegada hasta terminación
        # - Tiempo de respuesta: tiempo desde llegada hasta primera ejecución
        # ═══════════════════════════════════════════════════════════════════
        if not self.procesos_terminados:
            return None
        
        tiempo_espera_promedio = (sum(p.tiempo_espera for p in self.procesos_terminados) / 
                                 len(self.procesos_terminados))
        tiempo_retorno_promedio = (sum(p.tiempo_retorno for p in self.procesos_terminados) / 
                                  len(self.procesos_terminados))
        tiempo_respuesta_promedio = (sum(p.tiempo_inicio_ejecucion - p.tiempo_llegada 
                                        for p in self.procesos_terminados) / 
                                    len(self.procesos_terminados))
        
        return {
            'tiempo_total': self.tiempo_actual,
            'procesos_terminados': len(self.procesos_terminados),
            'tiempo_espera_promedio': tiempo_espera_promedio,
            'tiempo_retorno_promedio': tiempo_retorno_promedio,
            'tiempo_respuesta_promedio': tiempo_respuesta_promedio,
            'procesos': self.procesos_terminados
        }
    
    def pausar(self):
        """Pausa la simulación"""
        self.pausado = True
    
    def reanudar(self):
        """Reanuda la simulación"""
        self.pausado = False
    
    def reiniciar(self):
        """Reinicia completamente el simulador"""
        # ═══════════════════════════════════════════════════════════════════
        # REINICIO COMPLETO DEL SISTEMA
        # ═══════════════════════════════════════════════════════════════════
        # Restaura el simulador a su estado inicial, limpiando todas las
        # estructuras de datos y reiniciando contadores.
        # ═══════════════════════════════════════════════════════════════════
        self.cola_listos.clear()
        self.proceso_actual = None
        self.procesos_terminados.clear()
        self.tiempo_actual = 0
        self.tiempo_quantum_restante = 0
        self.historial.clear()
        self.ticket_sorteado = None
        self.total_tickets_actual = 0
        self.ultimo_evento = "Simulador reiniciado"
        self.pausado = False
        self.servidores_ejecutados.clear()
        self.analizador.reiniciar()
        self.ultimo_analisis = None