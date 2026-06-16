# Chatbot de Expertos Temáticos con Ollama SDK

Proyecto en Python para conversar con tres expertos temáticos usando Ollama SDK y el modelo local `gemma3:1b`.

## Expertos incluidos

Los tres expertos desarrollados pertenecen a distintas ramas. En concreto a:

- **Programación de Software**: desarrollo, arquitectura, mejores prácticas, pruebas y seguridad.
- **Marketing y Estrategia Comercial**: branding, posicionamiento, análisis de mercado, canales y métricas.
- **Jurídico-Legal**: contratos, normativas, cumplimiento, riesgos y redacción preventiva.

## Requisitos previos

Los requisitos para poder ejecutar el código son los siguientes:

- Python 3.10 o superior.
- Ollama instalado en el equipo.
- Servicio local de Ollama activo.
- Modelo `gemma3:1b` descargado localmente.

## Preparación del entorno

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instalación de dependencias:

```bash
pip install -r requirements.txt
```

Descarga previa del modelo local:

```bash
ollama pull gemma3:1b
```

Inicio del servicio local si no está activo:

```bash
ollama serve
```

## Ejecución

```bash
python main.py
```

## Uso de la consola

Al iniciar, el programa comprueba la conexión local con Ollama y valida que `gemma3:1b` esté disponible en el equipo.

Durante la conversación están disponibles estos comandos:

```text
/experto          cambiar de experto
/reiniciar        reiniciar el historial del experto activo
/reiniciar_todo   reiniciar el historial de todos los expertos
/estado           ver experto activo e historial
/ayuda            mostrar opciones disponibles
/salir            finalizar la aplicación
```

## Gestión del historial

Cada experto mantiene su propio historial de conversación. Al cambiar de experto, el programa permite conservar el historial existente de ese experto o reiniciarlo. Esto permite tener diálogos de múltiples intercambios con contextos diferenciado por especialidad / experto.

## Funcionamiento offline

El proyecto no usa servicios externos ni APIs en internet durante la ejecución. La generación de respuestas se realiza mediante el servicio local de Ollama y el modelo `gemma3:1b` descargado previamente.

## Manejo de errores

El programa informa claramente cuando:

- La librería `ollama` no está instalada.
- El servicio local de Ollama no está activo.
- El modelo `gemma3:1b` no está disponible localmente.
- El modelo no puede generar una respuesta durante la conversación.

## Estructura

```text
├── main.py
├── experts/
│   ├── __init__.py
│   └── expert_prompts.py
├── core/
│   ├── __init__.py
│   ├── chatbot.py
│   └── conversation.py
├── requirements.txt
└── README.md
```
