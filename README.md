
# Simulador de Planificación por Lotería

[![Versión Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green.svg)](LICENSE)
[![Plataforma](https://img.shields.io/badge/plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

  

Simulador interactivo de planificación de CPU que implementa el algoritmo **Lottery Scheduling** propuesto por Waldspurger & Weihl (1994). Incluye visualización en tiempo real, análisis teórico detallado y explicaciones educativas completas.

  

## Tabla de Contenidos

  

-  [Descripción General](#descripción-general)

-  [Características](#características)

-  [Fundamento del Algoritmo](#fundamento-del-algoritmo)

-  [Instalación](#instalación)

-  [Uso](#uso)

-  [Estructura del Proyecto](#estructura-del-proyecto)

-  [Opciones de Configuración](#opciones-de-configuración)

-  [Análisis Teórico](#análisis-teórico)

-  [Tecnologías](#tecnologías)

  

## Descripción General

  

Este simulador proporciona una implementación visual e interactiva del algoritmo Lottery Scheduling, un enfoque probabilístico de planificación de CPU que asigna tiempo de procesador proporcionalmente a las prioridades de los procesos mediante un sistema de boletos de lotería.

  

**Valor Educativo Principal:**

- Comprensión visual de la planificación no determinista

- Observación en tiempo real de la justicia proporcional y prevención de inanición

- Análisis detallado explicando por qué cada proceso termina en su posición específica

- Comparación con algoritmos tradicionales (Round Robin, Prioridad, SJF)

  

## Características

  

### Funcionalidad Principal

-  **Visualización en Tiempo Real**: Animación del estado de CPU, cola de listos y procesos completados

-  **Múltiples Modos de Configuración**:

- Asignación automática de tickets (prioridad × 10)

- Configuración manual de tickets por proceso

- Pool global de tickets con distribución proporcional

-  **Gestión de Procesos**:

- Creación manual de procesos con parámetros personalizados

- Generación aleatoria de procesos (5 a la vez)

- Relaciones cliente-servidor con transferencia de tickets

- Simulación de operaciones de E/S

  

### Análisis e Información

-  **Análisis por Sorteo**: Explicación detallada de por qué se ganó/perdió cada lotería

-  **Análisis de Orden Final**: Desglose completo de por qué cada proceso terminó 1°, 2°, 3°, etc.

-  **Métricas Estadísticas**:

- Tiempo de espera promedio

- Tiempo de retorno promedio

- Tiempo de respuesta promedio

- Estadísticas detalladas por proceso

  

### Características de Interfaz

- Interfaz de doble panel con scroll

- Velocidad de simulación ajustable (0.1x a 2.0x)

- Capacidad de pausar/reanudar

- Procesos codificados por colores para fácil seguimiento

- Funcionalidad de reinicio completo

  

## Fundamento del Algoritmo

  

### ¿Qué es Lottery Scheduling?

  

Lottery Scheduling es un algoritmo probabilístico donde:

1. Cada proceso recibe un número de boletos de lotería

2. El planificador selecciona aleatoriamente un boleto

3. El proceso dueño de ese boleto obtiene tiempo de CPU

4. Más boletos = mayor probabilidad de ganar

  

**Fórmula**: `P(proceso_i) = tickets_i / tickets_totales`


### Ventajas Clave

-  **Justicia proporcional**: Tiempo de CPU proporcional a los boletos

-  **Sin inanición**: Cada proceso tiene probabilidad no-cero

-  **Implementación simple**: Solo requiere generación de números aleatorios

-  **Prioridades flexibles**: Fácil de ajustar cambiando boletos

-  **Responsivo**: Nuevos procesos obtienen su parte justa inmediatamente

  

### Mecanismo Anti-Inanición

El simulador implementa un mecanismo de envejecimiento:

tickets_bonus = tiempo_espera / 5

tickets_totales = tickets_base + tickets_bonus

  

Esto asegura que los procesos que esperan mucho tiempo reciban boletos adicionales.

  

## Instalación

  

### Requisitos Previos

- Python 3.8 o superior

- tkinter (generalmente incluido con Python)

  

### Clonar Repositorio

  

git clone https://github.com/AdoDeveloper/lottery-scheduling-simulator.git

  

cd lottery-scheduling-simulator

  

### Verificar Instalación

  

bashpython --version # Debe ser 3.8+

  

### Ejecutar Simulador

  

bashpython python main.py

  

No se requieren dependencias adicionales - usa solo la biblioteca estándar de Python.

  
  

### Inicio Rápido

  

Iniciar el simulador:

  

bash python main.py

  

### Crear procesos:

  

Click en "Agregar Proceso" para creación manual

Click en "5 Aleatorios" para generación automática

  
  

### Configurar simulación (opcional):

  

Establecer Quantum (porción de tiempo por ejecución)

Ajustar velocidad de simulación

Habilitar tickets manuales o pool global de tickets

  
  

### Ejecutar:

  

Click en "INICIAR SIMULACIÓN"

Observar ejecución en tiempo real

Leer análisis detallado conforme ocurre cada sorteo

  
  

### Analizar resultados:

  

Hacer scroll hacia abajo en el panel derecho para ver análisis completo

Comprender por qué cada proceso terminó en su posición

  
  
  

### Configuración Avanzada

Pool Global de Tickets

Habilitar para fijar los tickets totales independientemente de los tickets individuales:

Tickets totales en el sistema: 100

P1 tiene 30 tickets → 30% probabilidad

P2 tiene 70 tickets → 70% probabilidad

El sorteo siempre ocurre entre 1-100

Tickets Manuales

Configurar cantidades exactas de tickets en lugar de cálculo automático:

Por defecto: tickets = prioridad × 10

Manual: tickets = cualquier valor que especifiques

Relaciones Cliente-Servidor

Crear dependencias de procesos donde los clientes prestan tickets a servidores:

Proceso 1 (Cliente) → ID Servidor: 2

Proceso 1 presta sus tickets al Proceso 2

Proceso 2 se ejecuta primero, luego devuelve los tickets

Estructura del Proyecto

lottery-scheduling-simulator/

│

├── proceso.py # Clase Proceso - Definición de procesos

├── analizador.py # Analizador teórico con explicaciones

├── simulador.py # Lógica del algoritmo de lotería

├── main.py # Interfaz gráfica principal (GUI)

└──README.md # Este archivo



### Descripción de Módulos

proceso.py

Define la clase Proceso con atributos:
  

identificador: ID único del proceso

num_tickets: Cantidad de boletos asignados

tiempo_cpu: Tiempo total de CPU necesario

prioridad: Nivel de prioridad (1-5)

proceso_servidor: ID del servidor (0 si no tiene)

  

analizador.py

Proporciona análisis teórico detallado:

  

Explica cada sorteo individual

Genera análisis de orden de finalización

Calcula estadísticas de probabilidad

Ofrece fundamento teórico

  

simulador.py

Implementa el algoritmo:

  

Gestión de cola de listos

Lógica de sorteo de lotería

Asignación de tickets con bonus por espera

Soporte de pool global de tickets

Manejo de relaciones cliente-servidor

  

interfaz_completa.py

Interfaz gráfica de usuario:

  

Paneles scrollables para controles e información

Visualización en tiempo real del estado del sistema

Controles interactivos de simulación

Displays de análisis y estadísticas

### Análisis Teórico

Explicación de Cada Sorteo

Para cada sorteo, el simulador explica:

  

Distribución de Tickets: Rangos de cada proceso

  

P1: [1-30] → 30% probabilidad

P2: [31-60] → 30% probabilidad

P3: [61-100] → 40% probabilidad

  

Por Qué Ganó: Análisis del proceso ganador

  

Su rango contenía el ticket sorteado

Probabilidad que tenía de ganar

Impacto de prioridad y tiempo de espera

  
  

Por Qué Perdieron: Análisis de los demás

  

Sus rangos no contenían el ticket

Comparación de probabilidades

Demostración de naturaleza probabilística

  
  
  

Análisis de Orden Final

Al terminar, explica por qué cada proceso finalizó en su posición:

Factores Analizados:

  

Éxito en Sorteos: Tasa real vs esperada

Prioridad: Impacto en asignación de tickets

Duración: Procesos cortos vs largos

Factor Aleatorio: Desviación de probabilidad teórica

Anti-Inanición: Bonus por tiempo de espera

  

Ejemplo de Salida:

POSICIÓN 1er LUGAR: PROCESO P3

- Ganó 15 de 25 sorteos (60%)

- Alta prioridad (4) → muchos tickets

- Proceso corto (5 ciclos) → terminó rápido

- Tuvo suerte: ganó más de lo esperado estadísticamente

## Tecnologías

  

Python 3.8+: Lenguaje principal

tkinter: Interfaz gráfica de usuario

threading: Simulación concurrente

random: Generación de sorteos aleatorios

  

### Por Qué Python Puro

Este proyecto usa únicamente la biblioteca estándar de Python para:

  

Facilitar instalación y ejecución

Eliminar dependencias externas

Maximizar compatibilidad entre plataformas

Enfocarse en el algoritmo, no en frameworks
