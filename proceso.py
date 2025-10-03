"""
Módulo que define la clase Proceso para el simulador de planificación por lotería
Autor: @Adolfo Cortez
Basado en: Waldspurger & Weihl (1994)
"""

class Proceso:
    """
    Representa un proceso en el sistema operativo.
    
    Atributos:
        identificador: ID único del proceso
        num_tickets: Número de boletos de lotería (más tickets = más probabilidad)
        tiempo_cpu: Tiempo total de CPU que necesita el proceso
        tiempo_restante: Tiempo que falta por ejecutar
        prioridad: Nivel de prioridad (1-5, donde 5 es máxima)
        proceso_servidor: ID del proceso servidor (0 si no tiene)
    """
    
    def __init__(self, identificador, num_tickets=0, tiempo_llegada=0, 
                 tiempo_cpu=0, prioridad=1, proceso_servidor=0):
        self.identificador = identificador
        self.num_tickets = num_tickets
        self.num_tickets_original = num_tickets
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_cpu = tiempo_cpu
        self.tiempo_restante = tiempo_cpu
        self.tiempo_espera = 0
        self.tiempo_retorno = 0
        self.tiempo_inicio_ejecucion = -1
        self.prioridad = prioridad
        self.proceso_servidor = proceso_servidor
        self.tickets_prestados = 0
        self.estado = "NUEVO"
        self.color = None
        
    def es_cliente(self):
        """Retorna True si el proceso es un cliente (tiene servidor)"""
        return self.proceso_servidor != 0
    
    def puede_ejecutarse(self, servidores_ejecutados):
        """
        Verifica si el proceso puede ejecutarse.
        Los clientes solo pueden ejecutarse después de su servidor.
        """
        if not self.es_cliente():
            return True
        return self.proceso_servidor in servidores_ejecutados
    
    def resetear_tickets(self):
        """Resetea los tickets al valor original"""
        self.num_tickets = self.num_tickets_original
        self.tickets_prestados = 0
    
    def __str__(self):
        return f"P{self.identificador}"
    
    def __repr__(self):
        return self.__str__()
    
    def info_completa(self):
        """Retorna información completa del proceso"""
        return (f"P{self.identificador}: Tickets={self.num_tickets}, "
                f"CPU={self.tiempo_restante}/{self.tiempo_cpu}, "
                f"Prioridad={self.prioridad}, Estado={self.estado}")