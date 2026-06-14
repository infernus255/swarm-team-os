# SWARM - Sequential Multi-Agent Pipeline para GitHub Copilot (VS Code)

Este directorio contiene la configuracion del pipeline multi-agente secuencial M0→M6 adaptado para **GitHub Copilot en VS Code**.

## Estructura

```
swarm/engines/.swarm_copilot/
├── .github/
│   ├── copilot-instructions.md       # Instrucciones globales del swarm (auto-detectado)
│   ├── agents/                       # Agentes personalizados de Copilot
│   │   ├── orchestrator.agent.md     # Gatekeeper del pipeline
│   │   ├── m0-bootstrapper.agent.md  # Project Manager
│   │   ├── m1-system-analyst.agent.md
│   │   ├── m2-business-analyst.agent.md
│   │   ├── m3-architect.agent.md
│   │   ├── m4-qa-engineer.agent.md
│   │   ├── m5-code-generator.agent.md
│   │   └── m6-devops.agent.md
│   ├── instructions/                 # Instrucciones path-specific
│   ├── prompts/                      # Slash commands reutilizables
│   └── skills/                       # Skills especializados
├── .swarn/                           # Cerebro inmutable del swarm
│   ├── specs/                        # Plantillas de especificaciones
│   ├── states/                       # Estado del pipeline
│   └── memory/                       # Memoria del proyecto
├── app_result/                       # Directorio de salida
├── AGENTS.md                         # Instrucciones multi-agente raiz
└── SETUP.md                          # Esta guia
```

## Como usar

### 1. Integrar en tu proyecto
Copia el contenido de `.github/` a la raiz de tu proyecto:
```bash
cp -r swarm/engines/.swarm_copilot/.github/* .github/
```

### 2. Usar el pipeline
1. Abre VS Code con tu proyecto
2. En el Chat de Copilot, selecciona el agente **@orchestrator**
3. Escribe tu requerimiento inicial
4. El orquestador guiara el flujo invocando automaticamente a cada agente

### 3. Modos de operacion
- **Greenfield:** Proyecto desde cero. Flujo completo M0→M6.
- **Brownfield:** Codigo existente. Salta M0, empieza en M1.

## Requisitos
- VS Code con GitHub Copilot extension
- Copilot Chat habilitado
- VS Code setting `github.copilot.chat.codeGeneration.useInstructionFiles: true` (para instrucciones globales)
