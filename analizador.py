"""
Módulo de análisis teórico para el simulador de planificación por lotería.
Autor: @Adolfo Cortez
"""

class AnalizadorLoteria:
    """
    Analiza y explica las decisiones del algoritmo de lotería.
    Proporciona explicaciones teóricas basadas en Waldspurger & Weihl (1994).
    """
    
    def __init__(self):
        self.historial_sorteos = []
        self.estadisticas_proceso = {}
        
    def analizar_sorteo(self, ticket_sorteado, total_tickets, proceso_ganador, procesos_participantes):
        """
        Analiza un sorteo específico y genera explicación teórica detallada.
        
        Args:
            ticket_sorteado: Número del ticket que ganó
            total_tickets: Total de tickets en el sorteo
            proceso_ganador: Proceso que ganó el sorteo
            procesos_participantes: Lista de procesos que participaron
        
        Returns:
            Diccionario con análisis completo del sorteo
        """
        analisis = {
            'ticket_sorteado': ticket_sorteado,
            'total_tickets': total_tickets,
            'ganador': proceso_ganador,
            'participantes': procesos_participantes.copy(),
            'explicacion': self._generar_explicacion(ticket_sorteado, total_tickets, 
                                                     proceso_ganador, procesos_participantes)
        }
        
        self.historial_sorteos.append(analisis)
        self._actualizar_estadisticas(proceso_ganador, procesos_participantes)
        
        return analisis
    
    def _generar_explicacion(self, ticket, total, ganador, participantes):
        """
        Genera explicación detallada basada en teoría de Lottery Scheduling.
        Explica por qué ganó el proceso ganador y por qué perdieron los demás.
        """
        
        # Calcular probabilidad del ganador
        prob_ganador = (ganador.num_tickets / total * 100) if total > 0 else 0
        
        explicacion = []
        
        # 1. Contexto del sorteo
        explicacion.append(f"SORTEO #{len(self.historial_sorteos) + 1}")
        explicacion.append(f"="*50)
        explicacion.append(f"Ticket sorteado: {ticket} de {total} totales")
        explicacion.append("")
        
        # 2. Distribución de tickets con rangos
        explicacion.append("DISTRIBUCION DE TICKETS (Rangos):")
        explicacion.append("-"*50)
        
        tickets_acumulados = 0
        perdedores = []
        
        for p in sorted(participantes, key=lambda x: x.identificador):
            rango_inicio = tickets_acumulados + 1
            tickets_acumulados += p.num_tickets
            rango_fin = tickets_acumulados
            prob = (p.num_tickets / total * 100) if total > 0 else 0
            rango = f"[{rango_inicio:3d}-{rango_fin:3d}]"
            
            if p.identificador == ganador.identificador:
                explicacion.append(f"  P{p.identificador}: {p.num_tickets:3d} tickets {rango} -> {prob:5.1f}%  <-- GANADOR")
            else:
                explicacion.append(f"  P{p.identificador}: {p.num_tickets:3d} tickets {rango} -> {prob:5.1f}%")
                perdedores.append(p)
        
        explicacion.append("")
        
        # 3. POR QUÉ GANÓ este proceso
        explicacion.append("POR QUE GANO P{}:".format(ganador.identificador))
        explicacion.append("-"*50)
        
        # Calcular rango del ganador
        tickets_antes = sum(p.num_tickets for p in participantes 
                          if p.identificador < ganador.identificador)
        rango_inicio = tickets_antes + 1
        rango_fin = tickets_antes + ganador.num_tickets
        
        explicacion.append(f"1. RANGO DE TICKETS:")
        explicacion.append(f"   - Sus {ganador.num_tickets} tickets ocupan [{rango_inicio}-{rango_fin}]")
        explicacion.append(f"   - El ticket {ticket} cayo dentro de este rango")
        explicacion.append("")
        
        explicacion.append(f"2. PROBABILIDAD:")
        explicacion.append(f"   - Tenia {prob_ganador:.1f}% de probabilidad de ganar")
        explicacion.append(f"   - Formula: (sus_tickets / total_tickets) * 100")
        explicacion.append(f"   - Calculo: ({ganador.num_tickets} / {total}) * 100 = {prob_ganador:.1f}%")
        explicacion.append("")
        
        # Análisis de prioridad
        max_prioridad = max(p.prioridad for p in participantes)
        
        explicacion.append(f"3. FACTOR PRIORIDAD:")
        explicacion.append(f"   - Prioridad de P{ganador.identificador}: {ganador.prioridad}")
        
        if ganador.prioridad == max_prioridad:
            explicacion.append(f"   - Tiene la MAXIMA prioridad del grupo")
            explicacion.append(f"   - Teoria: Mayor prioridad -> Mas tickets -> Mas probabilidad")
            explicacion.append(f"   - Resultado: ESPERADO por tener ventaja")
        else:
            procs_mayor_prio = [p for p in participantes if p.prioridad > ganador.prioridad]
            explicacion.append(f"   - NO tiene la maxima prioridad")
            explicacion.append(f"   - Procesos con mas prioridad: {', '.join([f'P{p.identificador}' for p in procs_mayor_prio])}")
            explicacion.append(f"   - Resultado: DEMUESTRA NATURALEZA PROBABILISTICA")
            explicacion.append(f"   - Ventaja clave: EVITA INANICION de procesos con baja prioridad")
        
        explicacion.append("")
        
        # Análisis de tiempo de espera
        if ganador.tiempo_espera > 0:
            bonus = ganador.tiempo_espera // 5
            explicacion.append(f"4. BONUS POR ESPERA:")
            explicacion.append(f"   - Tiempo de espera: {ganador.tiempo_espera} ciclos")
            explicacion.append(f"   - Bonus recibido: {bonus} tickets adicionales")
            explicacion.append(f"   - Mecanismo anti-inanicion: A mayor espera, mas tickets")
            explicacion.append("")
        
        # 4. POR QUÉ PERDIERON los otros
        if perdedores:
            explicacion.append("POR QUE PERDIERON LOS DEMAS PROCESOS:")
            explicacion.append("-"*50)
            
            for p in perdedores:
                prob_p = (p.num_tickets / total * 100) if total > 0 else 0
                tickets_antes_p = sum(pr.num_tickets for pr in participantes 
                                    if pr.identificador < p.identificador)
                rango_inicio_p = tickets_antes_p + 1
                rango_fin_p = tickets_antes_p + p.num_tickets
                
                explicacion.append(f"P{p.identificador}:")
                explicacion.append(f"  - Rango de tickets: [{rango_inicio_p}-{rango_fin_p}]")
                explicacion.append(f"  - El ticket {ticket} NO cayo en su rango")
                explicacion.append(f"  - Probabilidad que tenia: {prob_p:.1f}%")
                
                if p.num_tickets < ganador.num_tickets:
                    explicacion.append(f"  - Tenia MENOS tickets que P{ganador.identificador} ({p.num_tickets} vs {ganador.num_tickets})")
                    explicacion.append(f"  - Razon probable: Menor prioridad o menos tiempo esperando")
                elif p.num_tickets > ganador.num_tickets:
                    explicacion.append(f"  - Tenia MAS tickets que P{ganador.identificador} ({p.num_tickets} vs {ganador.num_tickets})")
                    explicacion.append(f"  - Perdio por AZAR: Demuestra que el algoritmo NO es determinista")
                    explicacion.append(f"  - Esto es NORMAL: La aleatoriedad es parte del algoritmo")
                else:
                    explicacion.append(f"  - Tenia IGUAL cantidad de tickets que el ganador")
                    explicacion.append(f"  - El azar decidio a favor de P{ganador.identificador}")
                
                explicacion.append("")
        
        # 5. Fundamento teórico
        explicacion.append("FUNDAMENTO TEORICO (Waldspurger & Weihl, 1994):")
        explicacion.append("-"*50)
        explicacion.append("1. JUSTICIA PROPORCIONAL:")
        explicacion.append("   - Cada proceso recibe CPU proporcional a sus tickets")
        explicacion.append(f"   - P{ganador.identificador} deberia recibir ~{prob_ganador:.1f}% del tiempo total")
        explicacion.append("")
        explicacion.append("2. NATURALEZA PROBABILISTICA:")
        explicacion.append("   - El algoritmo NO es determinista")
        explicacion.append("   - A corto plazo: Resultados pueden variar")
        explicacion.append("   - A largo plazo: Converge a proporciones esperadas")
        explicacion.append("")
        explicacion.append("3. ANTI-INANICION:")
        explicacion.append("   - Ningun proceso puede esperar indefinidamente")
        explicacion.append("   - Bonus por espera asegura que todos eventualmente ejecuten")
        explicacion.append("   - Ventaja sobre algoritmos de prioridad estricta")
        explicacion.append("")
        
        return "\n".join(explicacion)
    
    def _actualizar_estadisticas(self, ganador, participantes):
        """Actualiza estadísticas acumuladas de victorias por proceso"""
        for p in participantes:
            if p.identificador not in self.estadisticas_proceso:
                self.estadisticas_proceso[p.identificador] = {
                    'victorias': 0,
                    'participaciones': 0,
                    'tickets_promedio': 0,
                    'tickets_acumulados': 0
                }
            
            stats = self.estadisticas_proceso[p.identificador]
            stats['participaciones'] += 1
            stats['tickets_acumulados'] += p.num_tickets
            stats['tickets_promedio'] = stats['tickets_acumulados'] / stats['participaciones']
            
            if p.identificador == ganador.identificador:
                stats['victorias'] += 1
    
    def generar_analisis_orden_finalizacion(self, procesos_terminados):
        """
        Genera análisis detallado explicando por qué cada proceso
        terminó en su posición específica (1°, 2°, 3°, etc.)
        """
        analisis = []
        
        analisis.append("="*50)
        analisis.append("ANALISIS: POR QUE CADA PROCESO TERMINO EN SU POSICION")
        analisis.append("="*50)
        analisis.append("")
        analisis.append("Este analisis explica las razones por las cuales cada proceso")
        analisis.append("finalizo en el orden mostrado, basandose en la teoria de")
        analisis.append("Lottery Scheduling de Waldspurger & Weihl (1994).")
        analisis.append("")
        
        for posicion, proceso in enumerate(procesos_terminados, 1):
            stats = self.estadisticas_proceso.get(proceso.identificador, {})
            victorias = stats.get('victorias', 0)
            participaciones = stats.get('participaciones', 0)
            tasa_exito = (victorias / participaciones * 100) if participaciones > 0 else 0
            tickets_prom = stats.get('tickets_promedio', 0)
            
            # Determinar sufijo ordinal
            if posicion == 1:
                sufijo = "er"
            elif posicion == 2:
                sufijo = "do"
            elif posicion == 3:
                sufijo = "ro"
            else:
                sufijo = "to"
            
            analisis.append("")
            analisis.append("#"*50)
            analisis.append(f"POSICION {posicion}{sufijo} LUGAR: PROCESO P{proceso.identificador}")
            analisis.append("#"*50)
            analisis.append("")
            
            analisis.append("DATOS DEL PROCESO:")
            analisis.append(f"  - Tiempo de CPU necesario: {proceso.tiempo_cpu} ciclos")
            analisis.append(f"  - Prioridad asignada: {proceso.prioridad}")
            analisis.append(f"  - Sorteos ganados: {victorias} de {participaciones} ({tasa_exito:.1f}%)")
            analisis.append(f"  - Tickets promedio: {tickets_prom:.1f}")
            analisis.append(f"  - Tiempo de espera total: {proceso.tiempo_espera} ciclos")
            analisis.append(f"  - Tiempo de retorno: {proceso.tiempo_retorno} ciclos")
            analisis.append("")
            
            # RAZÓN 1: Éxito en sorteos
            analisis.append(f"RAZON #1 - EXITO EN LOS SORTEOS:")
            analisis.append("-"*50)
            
            if participaciones > 0:
                probabilidad_teorica = tickets_prom
                desviacion = tasa_exito - probabilidad_teorica
                
                analisis.append(f"  Tasa de exito real: {tasa_exito:.1f}%")
                analisis.append(f"  Probabilidad teorica: {probabilidad_teorica:.1f}%")
                analisis.append(f"  Desviacion: {desviacion:+.1f}%")
                analisis.append("")
                
                if desviacion > 10:
                    analisis.append(f"  -> P{proceso.identificador} tuvo MUCHA SUERTE")
                    analisis.append(f"  -> Gano {desviacion:.1f}% mas de lo esperado estadisticamente")
                    analisis.append(f"  -> Esto ACELERO su finalizacion")
                elif desviacion < -10:
                    analisis.append(f"  -> P{proceso.identificador} tuvo MALA SUERTE")
                    analisis.append(f"  -> Gano {abs(desviacion):.1f}% menos de lo esperado")
                    analisis.append(f"  -> Esto RETRASO su finalizacion")
                else:
                    analisis.append(f"  -> Resultado CONSISTENTE con probabilidad teorica")
                    analisis.append(f"  -> El azar no jugo un rol significativo")
            
            analisis.append("")
            
            # RAZÓN 2: Prioridad
            analisis.append(f"RAZON #2 - IMPACTO DE LA PRIORIDAD:")
            analisis.append("-"*50)
            analisis.append(f"  Prioridad: {proceso.prioridad}/5")
            analisis.append(f"  Tickets base: {proceso.prioridad * 10}")
            analisis.append("")
            
            if proceso.prioridad >= 4:
                analisis.append(f"  -> PRIORIDAD MUY ALTA")
                analisis.append(f"  -> Recibio muchos tickets (ventaja significativa)")
                analisis.append(f"  -> Por eso termino rapidamente")
            elif proceso.prioridad == 3:
                analisis.append(f"  -> PRIORIDAD ALTA")
                analisis.append(f"  -> Buenos tickets, mas probabilidad que procesos de baja prioridad")
            elif proceso.prioridad == 2:
                analisis.append(f"  -> PRIORIDAD MEDIA")
                analisis.append(f"  -> Tickets moderados, sin grandes ventajas ni desventajas")
            else:
                analisis.append(f"  -> PRIORIDAD BAJA")
                analisis.append(f"  -> Pocos tickets, menor probabilidad de ganar sorteos")
                analisis.append(f"  -> Por eso tardo mas en terminar")
            
            analisis.append("")
            
            # RAZÓN 3: Duración del proceso
            analisis.append(f"RAZON #3 - TIEMPO DE CPU REQUERIDO:")
            analisis.append("-"*50)
            analisis.append(f"  Necesito: {proceso.tiempo_cpu} ciclos de CPU")
            analisis.append("")
            
            if proceso.tiempo_cpu <= 4:
                analisis.append(f"  -> PROCESO CORTO")
                analisis.append(f"  -> Incluso con pocos sorteos ganados, termino rapido")
                analisis.append(f"  -> La duracion corta compensa baja prioridad")
            elif proceso.tiempo_cpu <= 7:
                analisis.append(f"  -> PROCESO DE DURACION MEDIA")
                analisis.append(f"  -> Necesito balance entre tickets y sorteos ganados")
            else:
                analisis.append(f"  -> PROCESO LARGO")
                analisis.append(f"  -> Necesito ganar muchos sorteos para completarse")
                analisis.append(f"  -> La duracion larga requiere alta prioridad para terminar rapido")
            
            analisis.append("")
            
            # RAZÓN 4: Mecanismo anti-inanición
            if proceso.tiempo_espera > 20:
                bonus_total = proceso.tiempo_espera // 5
                analisis.append(f"RAZON #4 - MECANISMO ANTI-INANICION:")
                analisis.append("-"*50)
                analisis.append(f"  Tiempo de espera: {proceso.tiempo_espera} ciclos")
                analisis.append(f"  Bonus total recibido: ~{bonus_total} tickets extra")
                analisis.append("")
                analisis.append(f"  -> Espero MUCHO tiempo")
                analisis.append(f"  -> El algoritmo le dio tickets extra para evitar inanicion")
                analisis.append(f"  -> Sin este mecanismo, podria NUNCA haberse ejecutado")
                analisis.append("")
            
            # RAZÓN ESPECÍFICA SEGÚN POSICIÓN
            analisis.append(f"CONCLUSION - POR QUE TERMINO EN {posicion}{sufijo} LUGAR:")
            analisis.append("-"*50)
            
            if posicion == 1:
                analisis.append(f"  P{proceso.identificador} termino PRIMERO porque:")
                if proceso.prioridad >= 3 and proceso.tiempo_cpu <= 6:
                    analisis.append(f"  -> Combinacion ideal: Alta prioridad + Proceso no muy largo")
                elif tasa_exito > tickets_prom + 15:
                    analisis.append(f"  -> Tuvo mucha SUERTE en los sorteos")
                elif proceso.tiempo_cpu <= 4:
                    analisis.append(f"  -> Era un proceso MUY CORTO")
                else:
                    analisis.append(f"  -> Balance favorable de prioridad, duracion y suerte")
                analisis.append(f"  -> Obtuvo acceso a la CPU lo suficiente para completarse primero")
                
            elif posicion == len(procesos_terminados):
                analisis.append(f"  P{proceso.identificador} termino ULTIMO porque:")
                if proceso.prioridad <= 2 and proceso.tiempo_cpu >= 7:
                    analisis.append(f"  -> Peor combinacion: Baja prioridad + Proceso largo")
                elif tasa_exito < tickets_prom - 15:
                    analisis.append(f"  -> Tuvo MALA SUERTE en los sorteos")
                elif proceso.tiempo_cpu >= 9:
                    analisis.append(f"  -> Era un proceso MUY LARGO")
                else:
                    analisis.append(f"  -> Otros procesos tuvieron ventajas sobre el")
                analisis.append(f"  -> A pesar de eso, NO sufrio inanicion (eventualmente termino)")
                analisis.append(f"  -> Esto DEMUESTRA la ventaja del algoritmo sobre prioridad estricta")
                
            else:
                analisis.append(f"  P{proceso.identificador} termino en posicion INTERMEDIA porque:")
                analisis.append(f"  -> No tuvo las mejores condiciones (prioridad/duracion/suerte)")
                analisis.append(f"  -> Pero tampoco las peores")
                analisis.append(f"  -> Resultado consistente con su perfil estadistico")
            
            analisis.append("")
            analisis.append("="*50)
        
        # CONCLUSIÓN GENERAL
        analisis.append("")
        analisis.append("")
        analisis.append("*"*50)
        analisis.append("CONCLUSION GENERAL - TEORIA DE LOTTERY SCHEDULING")
        analisis.append("*"*50)
        analisis.append("")
        analisis.append("El orden final de los procesos esta determinado por 5 factores:")
        analisis.append("")
        analisis.append("1. TICKETS (determinados por PRIORIDAD):")
        analisis.append("   Mas tickets = Mayor probabilidad de CPU = Terminar mas rapido")
        analisis.append("   Formula: Tickets base = Prioridad × 10")
        analisis.append("")
        analisis.append("2. DURACION del proceso:")
        analisis.append("   Procesos cortos terminan antes incluso con pocos tickets")
        analisis.append("   Procesos largos necesitan ganar muchos sorteos")
        analisis.append("")
        analisis.append("3. FACTOR ALEATORIO (suerte):")
        analisis.append("   El azar puede beneficiar o perjudicar a cualquier proceso")
        analisis.append("   Corto plazo: Resultados pueden parecer injustos")
        analisis.append("   Largo plazo: Converge a proporciones de tickets")
        analisis.append("")
        analisis.append("4. MECANISMO ANTI-INANICION:")
        analisis.append("   Bonus: +1 ticket cada 5 ciclos de espera")
        analisis.append("   Garantiza que ningun proceso espere indefinidamente")
        analisis.append("   DIFERENCIA CLAVE vs. algoritmos de prioridad estricta")
        analisis.append("")
        analisis.append("5. QUANTUM (tiempo de ejecucion por turno):")
        analisis.append("   Cada proceso ejecuta durante 'quantum' ciclos al ganar")
        analisis.append("   Luego es expulsado y debe volver a participar en el sorteo")
        analisis.append("")
        analisis.append("VENTAJAS demostradas en esta simulacion:")
        analisis.append("  - Justicia proporcional: CPU ~ proporcion de tickets")
        analisis.append("  - Sin inanicion: Todos los procesos terminaron")
        analisis.append("  - Simplicidad: Solo requiere sorteo aleatorio")
        analisis.append("  - Flexibilidad: Soporte de prioridades via tickets")
        analisis.append("")
        analisis.append("DESVENTAJAS observadas:")
        analisis.append("  - No determinista: El orden puede variar entre ejecuciones")
        analisis.append("  - Sin garantias de tiempo: No se puede predecir cuando terminara un proceso")
        analisis.append("")
        analisis.append("Referencia: Waldspurger, C. A., & Weihl, W. E. (1994)")
        analisis.append("Lottery Scheduling: Flexible Proportional-Share Resource Management")
        analisis.append("*"*50)
        
        return "\n".join(analisis)
    
    def obtener_resumen_estadistico(self):
        """Genera resumen estadístico compacto de todos los sorteos"""
        resumen = []
        
        resumen.append("="*50)
        resumen.append("RESUMEN ESTADISTICO DE TODOS LOS SORTEOS")
        resumen.append("="*50)
        resumen.append("")
        
        total_sorteos = len(self.historial_sorteos)
        resumen.append(f"Total de sorteos realizados: {total_sorteos}")
        resumen.append("")
        resumen.append("Proceso|Victorias|Particip.|Tasa Exito|Tickets Prom")
        resumen.append("-"*50)
        
        for pid, stats in sorted(self.estadisticas_proceso.items()):
            vic = stats['victorias']
            part = stats['participaciones']
            tasa = (vic/part*100) if part > 0 else 0
            tprom = stats['tickets_promedio']
            resumen.append(f"  P{pid:2d}  |  {vic:4d}   |  {part:4d}   |  {tasa:5.1f}%  |  {tprom:5.1f}")
        
        resumen.append("")
        resumen.append("Interpretacion:")
        resumen.append("  - Tasa de Exito: Porcentaje de sorteos ganados")
        resumen.append("  - Tickets Prom: Promedio de tickets que tuvo el proceso")
        resumen.append("  - A mayor Tickets Prom, mayor deberia ser la Tasa de Exito")
        resumen.append("")
        
        return "\n".join(resumen)
    
    def reiniciar(self):
        """Reinicia todas las estadísticas del analizador"""
        self.historial_sorteos.clear()
        self.estadisticas_proceso.clear()