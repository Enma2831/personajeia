# PersonajeIA - Virtual Character Creator

Aplicación web local para crear personajes virtuales realistas con IA generativa, síntesis de voz y animación facial.

## Arquitectura General

### Componentes Principales
- **Frontend**: React + Tailwind CSS - Interfaz de usuario moderna
- **Backend Node.js**: Integración con Gemini para generación de imágenes
- **Backend Python**: FastAPI para TTS y animación facial
- **Pipeline de Procesamiento**: Imagen → Voz → Animación → Video

### Flujo de Datos
1. Usuario ingresa prompt para generar personaje
2. Gemini genera imagen base y expresiones
3. Usuario ingresa historia de terror
4. TTS genera audio en español latino
5. Animación facial sincroniza labios y agrega gestos
6. FFmpeg renderiza video vertical 9:16

## Requisitos del Sistema
- Node.js 18+
- Python 3.8+
- FFmpeg
- GPU recomendada para animación (opcional)

## 🚀 Estado Actual de la Implementación

### ✅ Funcionalidades Implementadas
- **Frontend React**: Interfaz completa con Tailwind CSS
- **Backend Node.js**: Integración con Gemini para generación de imágenes
- **Backend Python**: API FastAPI con TTS real (pyttsx3 + gTTS fallback)
- **Arquitectura Modular**: Servicios desacoplados con comunicación REST
- **TTS Real**: Síntesis de voz en español usando pyttsx3 (offline) o gTTS (online)
- **Pipeline Básico**: Generación de imagen → voz real → placeholder de video

### ⚠️ Limitaciones Actuales (Para Producción Completa)
- **Animación Facial**: Simulada (necesita Wav2Lip o similar)
- **Video Rendering**: Simulado (necesita FFmpeg instalado)
- **API Key**: Requiere configuración manual de Google API Key
- **OpenCV**: No instalado (necesario para procesamiento de imágenes avanzado)

## Instalación y Ejecución

### Opción 1: Script Automático (Recomendado)
```bash
# En Windows
start.bat

# O manualmente en Linux/Mac
./start.sh
```

### Opción 2: Manual
```bash
# Terminal 1: Backend Node.js
cd backend-node && node server.js

# Terminal 2: Backend Python
cd backend-python && python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)"

# Terminal 3: Frontend
cd frontend && npm start
```

### Configuración Inicial
1. **API Key de Google**: Edita `.env` y agrega tu `GOOGLE_API_KEY`
2. **Dependencias**: Las básicas están instaladas
3. **Acceso**: Frontend en `http://localhost:3000`

## 🧪 Testing la Funcionalidad Actual

### Test de TTS
```bash
cd backend-python
python test_tts.py
```
Esto genera un archivo de audio con voz en español.

### Verificar Servicios
- **Frontend**: http://localhost:3000
- **Backend Node.js**: http://localhost:3002 (Gemini images)
- **Backend Python**: http://localhost:8000 (TTS y animación)

### Flujo de Test Completo
1. Abre el frontend en el navegador
2. Ingresa un prompt para generar personaje (ej: "Una mujer misteriosa con ojos penetrantes")
3. Espera a que Gemini genere la imagen
4. Ingresa una historia corta de terror
5. El sistema generará voz real y simulará el video

## Próximos Pasos para Producción

### ✅ **Completado: TTS Real**
- ✅ pyttsx3 instalado y funcionando (TTS offline)
- ✅ gTTS como fallback (TTS online de mejor calidad)
- ✅ Configuración optimizada para narración de horror

### 1. **Animación Facial Real**
```bash
# Instalar Wav2Lip
git clone https://github.com/Rudrabha/Wav2Lip.git
cd Wav2Lip && pip install -r requirements.txt
```

### 2. **FFmpeg para Video Rendering**
```bash
# Windows: Descarga manual de https://ffmpeg.org/download.html
# Ya intentamos instalar automáticamente pero falló
```

### 3. **OpenCV para Procesamiento de Imágenes**
```bash
# Problema con Python 3.14 - intentar con versión anterior
pip install opencv-python
```

### 4. **Optimizaciones**
- GPU support para PyTorch
- Cache de expresiones faciales
- Validación de prompts
- Manejo de errores robusto

## Pipeline Detallado

### 1. Generación de Imagen con Gemini
El backend Node.js adapta el código proporcionado para generar personajes realistas:

```javascript
const response = await ai.models.generateContent({
  model: "gemini-2.5-flash-image",
  contents: fullPrompt, // Prompt optimizado para realismo
});
```

**Integración**: El prompt se enriquece con instrucciones específicas para fotorealismo y expresiones naturales. Las imágenes se guardan localmente y se sirven vía HTTP.

### 2. Síntesis de Voz con pyttsx3/gTTS
Backend Python usa TTS libraries reales:

```python
import pyttsx3
from gtts import gTTS

# pyttsx3 (offline, más rápido)
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Velocidad para narración
engine.setProperty('volume', 0.8)
engine.save_to_file(text, audio_path)
engine.runAndWait()

# gTTS fallback (online, mejor calidad)
tts = gTTS(text=text, lang='es', slow=False, tld='com.mx')
tts.save(audio_path)
```

**Características**: Voz en español, configuración optimizada para narración de horror (calmada e íntima).

### 3. Animación Facial con Wav2Lip
Para lip-sync preciso y gestos naturales:

- **Lip-sync**: Wav2Lip sincroniza movimiento labial con audio
- **Gestos**: Microexpresiones y parpadeo se agregan post-procesamiento
- **Implementación**: Ejecutar Wav2Lip como subprocess en Python

### 4. Render de Video con FFmpeg
Combina audio animado con video:

```bash
ffmpeg -y -loop 1 -i image.png -i audio.wav \
  -c:v libx264 -c:a aac -shortest \
  -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" \
  output.mp4
```

**Formato**: 9:16 vertical optimizado para TikTok/Reels.

## Recomendaciones de Mejora

### Realismo
- **Prompt Engineering**: Usar prompts detallados con referencias a iluminación, composición y estilo fotográfico
- **Modelos Avanzados**: Considerar Stable Diffusion fine-tuned para caras realistas
- **Post-procesamiento**: Aplicar super-resolution para mayor detalle

### Rendimiento
- **GPU Acceleration**: Usar CUDA para TTS y animación facial
- **Cache**: Almacenar expresiones comunes para reutilización
- **Paralelización**: Procesar múltiples pasos en paralelo

### Calidad Visual
- **Mejor Lip-sync**: Implementar modelos más avanzados como Wav2Lip 2.0
- **Expresiones Dinámicas**: Usar GANs para generar transiciones suaves entre expresiones
- **Audio Enhancement**: Aplicar noise reduction y normalization

### Escalabilidad
- **Arquitectura Hexagonal**: Separar dominio, aplicación e infraestructura
- **Microservicios**: Desacoplar componentes para deployment independiente
- **API Gateway**: Unificar comunicación entre servicios

### Seguridad y Privacidad
- **Local Execution**: Mantener todo procesamiento local para privacidad
- **Input Validation**: Sanitizar prompts y textos de usuario
- **Rate Limiting**: Prevenir abuso de recursos

---

**¡Tu PersonajeIA está lista para crear narradores virtuales de terror!** 🔥

¿Quieres que integremos alguna de estas mejoras ahora o tienes alguna pregunta específica sobre la implementación?
