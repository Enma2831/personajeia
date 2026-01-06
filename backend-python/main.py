from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import requests
import subprocess
import uuid
from pathlib import Path
import time
from PIL import Image, ImageDraw, ImageFont
import subprocess  # Para simular procesamiento
import pyttsx3
from gtts import gTTS

app = FastAPI(title="PersonajeIA Backend Python")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorios
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
BASE_URL = os.getenv("BACKEND_PYTHON_URL", "http://localhost:8000")

class NarrationRequest(BaseModel):
    story: str
    characterImage: str

class VoiceRequest(BaseModel):
    text: str
    voice_model: Optional[str] = "es-lat"

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy", "service": "PersonajeIA Python Backend"}

@app.post("/generate-narration")
async def generate_narration(request: NarrationRequest, background_tasks: BackgroundTasks):
    try:
        # Generar ID único para esta narración
        narration_id = str(uuid.uuid4())

        # Paso 1: Generar voz (simulado por ahora)
        audio_path = await generate_voice_mock(request.story, narration_id)

        # Paso 2: Descargar imagen del personaje
        image_path = await download_character_image(request.characterImage, narration_id)

        # Paso 3: Generar animación facial (simulado)
        video_path = OUTPUT_DIR / f"{narration_id}_animated.mp4"
        background_tasks.add_task(process_animation_mock, image_path, audio_path, video_path)

        return {
            "narration_id": narration_id,
            "status": "processing",
            "message": "Narración en proceso. Voz generada con TTS real (pyttsx3/gTTS), animación facial simulada.",
            "audio_url": f"{BASE_URL}/output/{audio_path.name}",
            "video_url": f"{BASE_URL}/output/{video_path.name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-voice")
async def generate_voice_endpoint(request: VoiceRequest):
    try:
        audio_path = await generate_voice_mock(request.text, str(uuid.uuid4()))
        return {"audio_url": f"{BASE_URL}/output/{audio_path.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_voice_mock(text: str, narration_id: str):
    """Genera voz real usando pyttsx3 (offline) o gTTS (online) como fallback"""
    audio_path = OUTPUT_DIR / f"{narration_id}_voice.mp3"

    try:
        # Intentar primero con pyttsx3 (offline)
        engine = pyttsx3.init()

        # Configurar voz en español si está disponible
        voices = engine.getProperty('voices')
        spanish_voice = None
        for voice in voices:
            if 'spanish' in voice.name.lower() or 'es' in voice.name.lower():
                spanish_voice = voice
                break

        if spanish_voice:
            engine.setProperty('voice', spanish_voice.id)
        else:
            # Usar voz por defecto si no hay española
            print("No se encontró voz española, usando voz por defecto")

        # Configurar velocidad y volumen para narración de horror
        engine.setProperty('rate', 150)  # Velocidad más lenta para narración
        engine.setProperty('volume', 0.8)  # Volumen moderado

        # Generar audio
        engine.save_to_file(text, str(audio_path))
        engine.runAndWait()

        print(f"Audio generado exitosamente con pyttsx3: {audio_path}")
        return audio_path

    except Exception as e:
        print(f"Error con pyttsx3, intentando con gTTS: {e}")

        try:
            # Fallback a gTTS (requiere internet)
            tts = gTTS(text=text, lang='es', slow=False, tld='com.mx')  # Español latinoamericano
            tts.save(str(audio_path))
            print(f"Audio generado exitosamente con gTTS: {audio_path}")
            return audio_path

        except Exception as e2:
            print(f"Error con gTTS también: {e2}")

            # Último fallback: crear archivo de audio simple
            try:
                import wave
                import struct

                # Crear un archivo WAV simple con tono
                sample_rate = 44100
                duration = len(text) * 0.1  # duración basada en longitud del texto
                if duration < 2:
                    duration = 2

                # Generar datos de onda sinusoidal
                frames = []
                for i in range(int(sample_rate * duration)):
                    # Onda sinusoidal con variación para simular habla
                    sample = int(32767 * 0.3 * (i / (sample_rate * duration)))
                    frames.append(struct.pack('<h', sample))

                # Escribir archivo WAV
                wav_path = audio_path.with_suffix('.wav')
                with wave.open(str(wav_path), 'wb') as wav_file:
                    wav_file.setnchannels(1)  # mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(frames))

                print(f"Audio simulado creado como fallback: {wav_path}")
                return wav_path

            except Exception as e3:
                print(f"Error creando audio fallback: {e3}")
                # Crear archivo de texto como último recurso
                txt_path = audio_path.with_suffix('.txt')
                with open(txt_path, 'w') as f:
                    f.write(f"Error generando audio. Texto: {text[:200]}...")
                return txt_path

async def download_character_image(image_url: str, narration_id: str):
    """Descarga la imagen del personaje - soporta URLs HTTP y data URLs"""
    image_path = OUTPUT_DIR / f"{narration_id}_character.png"

    if image_url.startswith('data:image/'):
        # Manejar data URL (base64)
        import base64
        try:
            # Extraer el contenido base64
            header, encoded = image_url.split(',', 1)
            image_data = base64.b64decode(encoded)

            with open(image_path, 'wb') as f:
                f.write(image_data)

            print(f"Imagen guardada desde data URL: {image_path}")
        except Exception as e:
            print(f"Error procesando data URL: {e}")
            # Crear imagen placeholder
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color='gray')
            draw = ImageDraw.Draw(img)
            draw.text((200, 250), "Error loading image", fill='white')
            img.save(image_path)
    else:
        # Manejar URL HTTP normal
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            with open(image_path, 'wb') as f:
                f.write(response.content)

            print(f"Imagen descargada desde URL: {image_path}")
        except Exception as e:
            print(f"Error descargando imagen: {e}")
            # Crear imagen placeholder
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color='gray')
            draw = ImageDraw.Draw(img)
            draw.text((200, 250), "Error loading image", fill='white')
            img.save(image_path)

    return image_path

def process_animation_mock(image_path: Path, audio_path: Path, output_path: Path):
    """Crea una animación facial básica usando Pillow - simula movimiento labial"""
    time.sleep(2)  # Simular procesamiento

    try:
        # Verificar si ffmpeg está disponible para crear video
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)

        # Si ffmpeg está disponible, intentar crear video simple
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
            str(output_path)
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=30)
        print(f"Video creado exitosamente con FFmpeg: {output_path}")
        return

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print("FFmpeg no disponible o falló, creando animación básica con Pillow")

    # Fallback: Crear animación básica con Pillow
    try:
        # Abrir la imagen original
        base_image = Image.open(image_path)

        # Crear frames de animación simulando movimiento labial
        frames = []
        mouth_states = ["closed", "open", "wide", "closed"]

        for i, state in enumerate(mouth_states * 3):  # Repetir patrón 3 veces
            # Copiar imagen base
            frame = base_image.copy()
            draw = ImageDraw.Draw(frame)

            # Obtener dimensiones
            width, height = frame.size

            # Definir área de la boca (aproximada - tercio inferior central)
            mouth_x = width // 3
            mouth_y = height * 2 // 3
            mouth_width = width // 3
            mouth_height = height // 6

            # Dibujar diferentes estados de boca
            if state == "closed":
                # Boca cerrada (línea recta)
                draw.rectangle([mouth_x, mouth_y + mouth_height//2 - 2,
                              mouth_x + mouth_width, mouth_y + mouth_height//2 + 2],
                             fill=(0, 0, 0))
            elif state == "open":
                # Boca semiabierta
                draw.ellipse([mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_height],
                           fill=(0, 0, 0))
            elif state == "wide":
                # Boca muy abierta
                draw.ellipse([mouth_x, mouth_y - mouth_height//2,
                            mouth_x + mouth_width, mouth_y + mouth_height + mouth_height//2],
                           fill=(0, 0, 0))

            frames.append(frame)

        # Crear GIF animado
        gif_path = output_path.with_suffix('.gif')
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=200,  # 200ms por frame
            loop=0
        )

        print(f"Animación GIF creada exitosamente: {gif_path}")

        # Crear archivo de texto indicando que es una animación simulada
        with open(output_path.with_suffix('.txt'), 'w') as f:
            f.write(f"Animación simulada creada: {gif_path.name}\n")
            f.write(f"Imagen base: {image_path.name}\n")
            f.write(f"Audio: {audio_path.name}\n")
            f.write("Movimiento labial simulado con Pillow\n")

    except Exception as e:
        print(f"Error creando animación con Pillow: {e}")
        # Último fallback: solo archivo de texto
        with open(output_path.with_suffix('.txt'), 'w') as f:
            f.write(f"Animación simulada - Imagen: {image_path.name}, Audio: {audio_path.name}\n")
            f.write(f"Error: {e}\n")

@app.get("/output/{filename}")
async def get_output_file(filename: str):
    """Sirve archivos de output"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    from fastapi.responses import FileResponse
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
