# Plantilla de Requerimientos de Aplicación (Application Requirement Prompt)

*INSTRUCCIONES PARA EL USUARIO O AGENTE M0: Para evitar carencias funcionales (alucinaciones operativas), NO entregue requerimientos vagos. Rellene esta plantilla de forma exhaustiva antes de iniciar el flujo de desarrollo.*

---

## 1. Visión General del Producto
[Describir el propósito principal de la aplicación, el stack tecnológico preferido, y la plataforma de despliegue]
*Ejemplo: "Sistema de gestión para peluquería, usando Python, Telegram Bot y SQLite, corriendo localmente."*

## 2. Perfil del Usuario Final (User Persona)
[Describir quién usará el sistema, en qué contexto y con qué limitaciones físicas o técnicas]
*Ejemplo: "Un peluquero que trabaja solo, con las manos ocupadas todo el tiempo. No puede tipear comandos largos. Usa el celular de a ratos cortos."*

## 3. Top 10 Acciones Diarias (Ordenadas por Frecuencia)
[Listar obligatoriamente las acciones que el usuario hará TODOS los días, de mayor a menor frecuencia. EL SISTEMA DEBE ESTAR OPTIMIZADO PARA ESTAS ACCIONES.]
1. *Ejemplo: Cobrar a un cliente que acaba de terminar (efectivo/transferencia) -> ACCIÓN CRÍTICA*
2. *Ejemplo: Ver la agenda del día ordenadamente.*
3. *Ejemplo: Agendar un turno rápido para alguien que acaba de llamar.*
4. ...
5. ...

## 4. Restricciones de Entorno y Arquitectura
[Listar limitaciones obligatorias del sistema, integraciones prohibidas y requisitos no funcionales]
*Ejemplo: "NO usar base de datos en la nube. NO hay integraciones con Mercado Pago. Debe funcionar 100% offline excepto por Telegram."*

## 5. Flujos Críticos de Negocio (Happy Paths)
[Describir paso a paso al menos 2 escenarios que NO PUEDEN FALLAR bajo ninguna circunstancia]
- *Flujo A: Cliente entra, se atiende, y el peluquero marca el cobro con 1 solo click o 1 mensaje de audio.*
- *Flujo B: Alguien llama, el peluquero revisa disponibilidad de hoy y reserva un slot vacío sin chocar horarios.*