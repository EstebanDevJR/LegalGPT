# 🧑‍⚖️ LegalGPT

**Asesor legal automatizado para PyMEs colombianas**

LegalGPT es una plataforma de inteligencia artificial especializada en proporcionar orientación legal clara y accesible para micro, pequeñas y medianas empresas en Colombia. Ayuda a empresarios que no entienden contratos, leyes laborales o tributarias a tomar decisiones informadas.

## ✨ Características Principales

### 🎯 Para PyMEs Colombianas
- **Lenguaje claro**: Evita jerga legal compleja
- **Contexto específico**: Legislación colombiana actualizada
- **Casos prácticos**: Orientación para situaciones reales de negocio
- **Costos accesibles**: Sistema de límites para controlar gastos

### 🧠 Inteligencia Artificial Especializada
- **RAG avanzado**: Langchain + Pinecone + OpenAI
- **Prompts especializados**: Diferentes tipos de consulta legal
- **Análisis de documentos**: Subida y procesamiento de PDFs
- **Respuestas contextualizadas**: Basadas en legislación real

### 🔐 Plataforma Completa
- **Autenticación**: Supabase Auth con JWT
- **Base de datos**: PostgreSQL con Row Level Security
- **API REST**: FastAPI con documentación automática
- **Sistema de límites**: Control de uso semanal/diario
- **Tracking**: Estadísticas detalladas de uso

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.9+
- Cuenta en [Supabase](https://supabase.com)
- API Key de [OpenAI](https://platform.openai.com)
- API Key de [Pinecone](https://pinecone.io)

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/legalgpt.git
cd legalgpt/backend
```

### 2. Configurar entorno virtual
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp env_example.txt .env

# Editar .env con tus credenciales
nano .env
```

### 4. Inicializar base de datos
```bash
python scripts/init_database.py
```

### 5. Iniciar servidor
```bash
python start.py --reload
```

¡Listo! Ve a http://localhost:8000/docs para ver la API.

## 📚 Documentación de la API

### Endpoints Principales

#### 🔐 Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Información del usuario actual
- `POST /auth/logout` - Cerrar sesión

#### 🧠 Consultas RAG
- `POST /rag/query` - Hacer consulta legal
- `GET /rag/suggestions` - Sugerencias de consultas
- `GET /rag/history` - Historial de consultas
- `POST /rag/feedback` - Enviar feedback

#### 📄 Documentos
- `POST /upload/document` - Subir documento PDF/TXT
- `GET /upload/documents` - Listar documentos subidos
- `DELETE /upload/documents/{id}` - Eliminar documento

#### 📊 Uso y Estadísticas
- `GET /usage/stats` - Estadísticas personales
- `GET /usage/limits` - Verificar límites
- `GET /usage/dashboard` - Dashboard completo

## 🎯 Casos de Uso

### Para Micro Empresas
```json
{
  "question": "¿Cómo hago un contrato de trabajo para mi primer empleado?",
  "context": "Tengo una microempresa de 2 personas"
}
```

### Para Pequeñas Empresas
```json
{
  "question": "¿Qué obligaciones tributarias tengo como SAS?",
  "context": "SAS con ingresos de 500 millones anuales"
}
```

### Análisis de Contratos
```json
{
  "question": "¿Este contrato me obliga a pagar indemnización?",
  "context": "Contrato de servicios con cláusula de exclusividad"
}
```

## 🏗️ Arquitectura Técnica

### Backend (FastAPI)
```
backend/
├── app/
│   └── main.py              # Aplicación principal
├── models/                  # Modelos Pydantic
│   ├── user.py
│   └── usage.py
├── services/                # Lógica de negocio
│   ├── auth_utils.py        # Autenticación
│   ├── llm_chain.py         # RAG con LangChain
│   ├── usage_service.py     # Límites y tracking
│   ├── pdf_parser.py        # Procesamiento PDFs
│   └── prompts.py           # Prompts especializados
├── routes/                  # Endpoints API
│   ├── auth.py
│   ├── rag.py
│   ├── upload.py
│   └── usage.py
└── scripts/
    └── init_database.py     # Inicialización DB
```

### Base de Datos (Supabase)
- `user_profiles` - Perfiles extendidos de usuarios
- `usage_tracking` - Tracking de consultas
- `uploaded_documents` - Documentos subidos
- `saved_queries` - Consultas favoritas
- `user_feedback` - Feedback y calificaciones

### Stack Tecnológico
- **Framework**: FastAPI
- **LLM**: OpenAI GPT-3.5/4
- **Vector DB**: Pinecone
- **RAG**: LangChain
- **Auth/DB**: Supabase
- **PDF Processing**: PyMuPDF, PDFPlumber, PyPDF2

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiI...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiI...

# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=tu-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=legalgpt

# Límites de uso
WEEKLY_QUERY_LIMIT=10
DAILY_QUERY_LIMIT=3
```

### Despliegue en Producción
```bash
# Con Docker
docker build -t legalgpt-backend .
docker run -p 8000:8000 --env-file .env legalgpt-backend

# Con systemd
sudo cp legalgpt.service /etc/systemd/system/
sudo systemctl enable legalgpt
sudo systemctl start legalgpt
```

## 📈 Roadmap

### Fase 1 ✅ (Actual)
- [x] Backend completo con FastAPI
- [x] Autenticación con Supabase
- [x] RAG básico con documentos legales colombianos
- [x] Sistema de límites de uso
- [x] API REST documentada

### Fase 2 🚧 (En desarrollo)
- [ ] Frontend React con dashboard
- [ ] Interfaz de chat en tiempo real
- [ ] Análisis avanzado de contratos
- [ ] Integración con Cámara de Comercio
- [ ] Notificaciones por email

### Fase 3 🔮 (Futuro)
- [ ] App móvil (React Native)
- [ ] Integración con DIAN
- [ ] Planes de suscripción
- [ ] Multi-tenant para estudios jurídicos
- [ ] Expansión a México y España

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

- 📧 Email: soporte@legalgpt.com
- 💬 Discord: [Unirse al servidor](https://discord.gg/legalgpt)
- 📚 Documentación: [docs.legalgpt.com](https://docs.legalgpt.com)
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/legalgpt/issues)

## 🙏 Agradecimientos

- [LangChain](https://langchain.com) por el framework RAG
- [Supabase](https://supabase.com) por la infraestructura backend
- [OpenAI](https://openai.com) por los modelos de lenguaje
- [FastAPI](https://fastapi.tiangolo.com) por el framework web
- Comunidad legal colombiana por el feedback

---

**LegalGPT** - Democratizando el acceso a asesoría legal para PyMEs colombianas 🇨🇴
