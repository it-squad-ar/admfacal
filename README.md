# 📥 Mail Invoice Processor

Automatización inteligente para la gestión de facturas recibidas por correo electrónico.

Este proyecto se conecta a una casilla de Gmail, identifica correos que contienen facturas, extrae los datos principales utilizando inteligencia artificial (LLM) y genera una planilla con la información consolidada. Además, reorganiza los correos aplicando etiquetas según su estado de procesamiento.

---

## 🚀 Funcionalidades

- 📧 Conexión a Gmail API.
- 🏷️ Clasificación de correos con etiquetas.
- 🧠 Extracción de datos usando modelos de lenguaje (LLM).
- 📄 Generación automática de planillas (Excel o CSV) con:
  - Fecha
  - N° de factura
  - CUIT
  - Razón social
  - Monto
- 🔄 Organización de adjuntos (PDF, XML, etc.) en carpetas locales.

---

## 📂 Estructura del Proyecto

## ⚒️ Cheat Sheet
- 🐙 Git Pull del repositorio
- 👾 Levantar _venv_:
  - Abrir consola PowerShell (Windows)
  - Crear: python -m venv venv
  - Activar: 
    - Windows: .\venv\scripts\activate
    - mac OS: source venv/bin/activate
  - Instalar librarias (primera vez): pip install -r requirements.txt
  - _En caso de no tener venv instalado:_ pip install