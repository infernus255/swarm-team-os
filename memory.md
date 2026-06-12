
### 2026-06-11T06:13:52.822246Z
- Initial environment adaptation setup complete.

### 2026-06-12T19:14:33.062401Z
- En entornos Windows y Docker, para que pase la validación de API keys, es necesario crear api_key_limits.json en la raíz del repositorio con los límites correspondientes y declarar las claves en hermes.env con el prefijo 'alias:' (ej. GEMINI_API_KEY=primary:CLAVE). Además, si Hermes se ejecuta únicamente dentro de Docker, se debe construir la imagen y etiquetarla como 'hermes-test:latest' para que la validación de estado la reconozca. Las imágenes privadas en GHCR requieren un PAT con scope 'read:packages' para evitar errores 'not found'.
