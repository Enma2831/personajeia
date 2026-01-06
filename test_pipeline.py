#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento completo de PersonajeIA
"""
import requests
import time
import json
from pathlib import Path

# URLs de los servicios
NODE_BACKEND = "http://localhost:3001"
PYTHON_BACKEND = "http://localhost:8000"

def test_character_generation():
    """Prueba la generación de personajes con Gemini - SALTADO (requiere API key)"""
    print("🧪 Generación de personajes - SALTADO (requiere GOOGLE_API_KEY)")
    return "skipped"

def test_voice_generation():
    """Prueba la generación de voz con TTS"""
    print("🧪 Probando generación de voz...")

    payload = {
        "text": "Hola, soy un personaje de horror. Esta es mi historia terrorífica que te contaré en primera persona.",
        "voice_model": "es-lat"
    }

    try:
        response = requests.post(f"{PYTHON_BACKEND}/generate-voice", json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        audio_url = result.get("audio_url")

        if audio_url:
            print(f"✅ Voz generada exitosamente: {audio_url}")
            return audio_url
        else:
            print("❌ Error: No se recibió URL de audio")
            return None

    except Exception as e:
        print(f"❌ Error generando voz: {e}")
        return None

def test_narration_pipeline():
    """Prueba el pipeline completo de narración"""
    print("🧪 Probando pipeline completo de narración...")

    # Crear una imagen de prueba simple usando Pillow si está disponible
    try:
        from PIL import Image, ImageDraw
        import base64
        import io

        # Crear imagen de prueba en memoria
        img = Image.new('RGB', (512, 512), color='gray')
        draw = ImageDraw.Draw(img)
        draw.text((200, 250), "Test Character", fill='white')

        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Crear data URL
        image_data_url = f"data:image/png;base64,{img_base64}"

    except ImportError:
        # Fallback si no hay Pillow
        image_data_url = "https://via.placeholder.com/512x512?text=Test+Image"

    payload = {
        "story": "Yo era una joven novia en 1892. Mi prometido me traicionó y me encerró en el sótano de nuestra mansión. Murieron todos, pero yo... yo sigo aquí. Esperando.",
        "characterImage": image_data_url
    }

    try:
        response = requests.post(f"{PYTHON_BACKEND}/generate-narration", json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
        narration_id = result.get("narration_id")

        if narration_id:
            print(f"✅ Narración iniciada exitosamente. ID: {narration_id}")
            print(f"📊 Estado: {result.get('status', 'desconocido')}")
            print(f"🎬 Video URL: {result.get('video_url', 'procesando...')}")
            return True
        else:
            print("❌ Error: No se recibió ID de narración")
            return False

    except Exception as e:
        print(f"❌ Error en pipeline de narración: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de PersonajeIA")
    print("=" * 50)

    # Verificar que los servicios estén corriendo
    services_ok = True

    try:
        requests.get(f"{NODE_BACKEND}/", timeout=5)
        print("✅ Backend Node.js: OK")
    except:
        print("❌ Backend Node.js: NO DISPONIBLE")
        services_ok = False

    try:
        requests.get(f"{PYTHON_BACKEND}/health", timeout=5)
        print("✅ Backend Python: OK")
    except:
        print("❌ Backend Python: NO DISPONIBLE")
        services_ok = False

    if not services_ok:
        print("\n❌ Servicios no disponibles. Asegúrate de que estén corriendo:")
        print("   - Backend Node.js en puerto 3001")
        print("   - Backend Python en puerto 8000")
        return

    print("\n🧪 Ejecutando pruebas individuales...")

    # Prueba 1: Generación de personajes
    image_url = test_character_generation()

    # Prueba 2: Generación de voz
    audio_url = test_voice_generation()

    # Prueba 3: Pipeline completo
    narration_ok = test_narration_pipeline()

    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS:")

    results = []
    if image_url == "skipped":
        results.append("⏭️  Generación de personajes (saltado - requiere API key)")
    elif image_url:
        results.append("✅ Generación de personajes")
    else:
        results.append("❌ Generación de personajes")

    if audio_url:
        results.append("✅ Generación de voz (TTS)")
    else:
        results.append("❌ Generación de voz (TTS)")

    if narration_ok:
        results.append("✅ Pipeline de narración completo")
    else:
        results.append("❌ Pipeline de narración completo")

    for result in results:
        print(f"   {result}")

    success_count = sum(1 for r in results if r.startswith("✅"))
    print(f"\n🎯 Resultado: {success_count}/{len(results)} pruebas exitosas")

    if success_count == len(results):
        print("🎉 ¡Todas las pruebas pasaron! La aplicación está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los logs para más detalles.")

if __name__ == "__main__":
    main()
