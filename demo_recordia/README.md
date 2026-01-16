# 🔐 KeepTrust Demo - Recordia

Sistema de memoria corporativa verificable con IA integrada.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

## 🚀 Demo en Vivo

Prueba la aplicación: [KeepTrust Demo](https://your-app.streamlit.app)

## ✨ Características

- 📋 **Registro de eventos críticos** con contexto empresarial
- 🤖 **Evaluación IA** asistida (OpenAI) con decisión humana final
- 🔒 **Hot Vault** - Evidencia sellada con hash SHA-256
- 📊 **Dashboard** con métricas y visualizaciones
- 📄 **Reportes KeepTrust** generados automáticamente
- 🧬 **Cadena documental** verificable
- 🔐 **Arquitectura AUP-EXO** para privacidad + auditabilidad

## 🏗️ Arquitectura

```
demo_recordia/
├── app.py                    # Aplicación principal Streamlit
├── recordia.sqlite           # Base de datos (se crea automáticamente)
├── hot_vault/                # Evidencia sellada (se crea automáticamente)
├── report_keeptrust.py       # Generador de reportes
├── recordia_chain.py         # Cadena documental
└── requirements.txt          # Dependencias Python
```

## 🔧 Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/B10sp4rt4n/KeepTrust.git
cd KeepTrust/demo_recordia

# Instalar dependencias
pip install -r requirements.txt

# (Opcional) Configurar API Key de OpenAI
export OPENAI_API_KEY="sk-tu-clave-aqui"

# Ejecutar aplicación
streamlit run app.py
```

## 🌐 Despliegue en Streamlit Cloud

### Paso 1: Fork o Clone este repositorio

### Paso 2: Ir a [share.streamlit.io](https://share.streamlit.io)

### Paso 3: Conectar tu repositorio

- Repository: `B10sp4rt4n/KeepTrust`
- Branch: `main`
- Main file path: `demo_recordia/app.py`

### Paso 4: (Opcional) Configurar Secrets

En Streamlit Cloud → App settings → Secrets:

```toml
OPENAI_API_KEY = "sk-tu-clave-aqui"
```

> **Nota:** La aplicación funciona sin API key en modo MOCK para demostraciones.

## 🔑 Configuración de OpenAI API

### Opción 1: Variable de entorno (local)
```bash
export OPENAI_API_KEY="sk-tu-clave-aqui"
```

### Opción 2: Streamlit Cloud Secrets
En la configuración de tu app en Streamlit Cloud, agrega:
```toml
OPENAI_API_KEY = "sk-tu-clave-aqui"
```

### Opción 3: En la aplicación (UI)
La app tiene un sidebar donde puedes ingresar tu API key directamente (campo de password).

## 📊 Modo MOCK vs Modo Real

- **Modo MOCK:** Sin API key, usa lógica de reglas predefinidas
- **Modo Real:** Con API key de OpenAI, evaluación inteligente con GPT-4o-mini

Ambos modos son completamente funcionales para demostración.

## 💼 Casos de Uso

| Sector | Aplicación | Beneficio |
|--------|-----------|-----------|
| **Legal** | Decisiones críticas | Evidencia defendible |
| **RH** | Incidentes laborales | Protección legal |
| **Compliance** | Trazabilidad normativa | Auditorías rápidas |
| **Operaciones** | Gestión de riesgos | Detección temprana |
| **Ventas** | Compromisos con clientes | Resolución de disputas |

## 🛡️ Seguridad

- ✅ **Inmutabilidad:** Hash SHA-256 por evento
- ✅ **No repudio:** Timestamp + decisión registrada
- ✅ **Privacidad:** Hot Vault local
- ✅ **Transparencia:** IA explicable
- ✅ **Control:** Humano siempre decide

## 📈 Stack Tecnológico

- **Backend:** Python 3.12+, SQLite
- **Frontend:** Streamlit
- **IA:** OpenAI API (GPT-4o-mini)
- **Visualización:** Matplotlib, Pandas
- **Seguridad:** SHA-256 hashing

## 📖 Documentación Completa

Ver [KEEPTRUST_MARKET_ANALYSIS.md](../KEEPTRUST_MARKET_ANALYSIS.md) para:
- Análisis de mercado completo
- Proyección de valoración
- Comparación con competidores
- Roadmap de desarrollo

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es parte de KeepTrust - Sistema de evidencia corporativa verificable.

## 📧 Contacto

- **GitHub:** [@B10sp4rt4n](https://github.com/B10sp4rt4n)
- **Proyecto:** [KeepTrust](https://github.com/B10sp4rt4n/KeepTrust)

---

**KeepTrust:** Cuando algo importa, queda sellado. Cuando necesitas demostrarlo, existe.
