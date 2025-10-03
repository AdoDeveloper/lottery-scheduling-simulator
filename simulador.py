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
    - Soporte para relaciones cliente-servidor
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
        proceso.estado = "LISTO"
        self.cola_listos.append(proceso)
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
        for proceso in self.cola_listos:
            # Tickets base según prioridad
            tickets_base = proceso.prioridad * 10
            
            # Bonus por tiempo de espera (evita inanición)
            bonus_espera = proceso.tiempo_espera // 5
            
            proceso.num_tickets = tickets_base + bonus_espera
            
    def _total_tickets(self):
        """Calcula el total de tickets de procesos que pueden ejecutarse"""
        if self.pool_tickets_global is not None:
            return self.pool_tickets_global
        
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
        procesos_validos = [p for p in self.cola_listos 
                        if p.puede_ejecutarse(self.servidores_ejecutados)]
        
        if not procesos_validos:
            self.ultimo_evento = "No hay procesos válidos para ejecutar"
            return None
        
        # Determinar total de tickets para el sorteo
        if self.pool_tickets_global is not None:
            # USO DE POOL GLOBAL: siempre sortear del pool fijo
            total_tickets = self.pool_tickets_global
        else:
            # SIN POOL GLOBAL: sumar tickets de todos los procesos
            total_tickets = sum(p.num_tickets for p in procesos_validos)
        
        if total_tickets == 0:
            self.ultimo_evento = "Total de tickets es 0"
            return None
            
        # SORTEO: Genera número aleatorio entre 1 y total_tickets
        ticket_ganador = random.randint(1, total_tickets)
        self.ticket_sorteado = ticket_ganador
        self.total_tickets_actual = total_tickets
        
        # Encuentra el proceso ganador
        if self.pool_tickets_global is not None:
            # CON POOL GLOBAL: distribución proporcional
            # Calcular suma de tickets de procesos válidos
            suma_tickets_procesos = sum(p.num_tickets for p in procesos_validos)
            
            if suma_tickets_procesos == 0:
                # Si todos tienen 0 tickets, distribución equitativa
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
                    
                    if ticket_ganador <= acumulado:
                        proceso_ganador = proceso
                        break
                else:
                    # Por si acaso hay error de redondeo
                    proceso_ganador = procesos_validos[-1]
        else:
            # SIN POOL GLOBAL: método estándar acumulativo
            acumulado = 0
            proceso_ganador = None
            for proceso in procesos_validos:
                acumulado += proceso.num_tickets
                if ticket_ganador <= acumulado:
                    proceso_ganador = proceso
                    break
        
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
        Implementa 'Ticket Transfer' de la teoría.
        """
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
        """Servidor devuelve tickets a sus clientes después de ejecutarse"""
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
            
        self.tiempo_actual += 1
        
        # Actualizar tiempo de espera de procesos que NO están ejecutando
        for proceso in self.cola_listos:
            if proceso != self.proceso_actual:
                proceso.tiempo_espera += 1
        
        # Si no hay proceso ejecutándose o se acabó el quantum, hacer sorteo
        if self.proceso_actual is None or self.tiempo_quantum_restante == 0:
            if self.proceso_actual and self.proceso_actual.tiempo_restante > 0:
                # Proceso expulsado por quantum agotado
                self.ultimo_evento = f"P{self.proceso_actual.identificador} EXPULSADO (quantum agotado)"
                self.proceso_actual.estado = "LISTO"
                self.cola_listos.append(self.proceso_actual)
                self.proceso_actual = None
            
            # Reasignar tickets antes del sorteo (incluye bonus por espera)
            if not self.usar_tickets_manual:
                self._asignar_tickets()
            
            # Realizar sorteo de lotería
            proceso_ganador = self._sortear_proceso()
            
            if proceso_ganador:
                self.cola_listos.remove(proceso_ganador)
                self.proceso_actual = proceso_ganador
                self.proceso_actual.estado = "EJECUTANDO"
                self.tiempo_quantum_restante = self.quantum
                
                # Registrar primera vez que ejecuta
                if self.proceso_actual.tiempo_inicio_ejecucion == -1:
                    self.proceso_actual.tiempo_inicio_ejecucion = self.tiempo_actual
                
                # Si es servidor, devolver tickets a clientes
                self._devolver_tickets(self.proceso_actual)
        
        # Ejecutar proceso actual
        if self.proceso_actual:
            self.proceso_actual.tiempo_restante -= 1
            self.tiempo_quantum_restante -= 1
            self.ultimo_evento = f"EJECUTANDO P{self.proceso_actual.identificador} (Restante: {self.proceso_actual.tiempo_restante}, Quantum: {self.tiempo_quantum_restante})"
            
            # Verificar si el proceso terminó
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
            self.ultimo_evento = "CPU IDLE - No hay procesos para ejecutar"
        
        # Guardar estado en historial
        self._guardar_historial()
        
        # Continuar si hay procesos pendientes
        return len(self.cola_listos) > 0 or self.proceso_actual is not None
    
    def _guardar_historial(self):
        """Guarda el estado actual en el historial para análisis posterior"""
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