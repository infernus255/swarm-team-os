---
name: Deploy Standards
description: Instrucciones para artefactos de despliegue
applyTo: "app_result/deploy/**"
---

## Estandares para Despliegue

- Dockerfile debe ser multi-stage para optimizar tamano
- Los pipelines CI/CD deben incluir stages de build, test y deploy
- La infraestructura como codigo debe ser declarativa y agnostica
- Incluir documentacion clara de los pasos de despliegue
- Las configuraciones no deben contener secretos hardcodeados
