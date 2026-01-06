const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
const express = require('express');
const cors = require('cors');
const { GoogleGenAI } = require('@google/genai');
const fs = require('fs');

const app = express();
const PORT = process.env.BACKEND_NODE_PORT || 3001;
const GOOGLE_API_KEY = process.env.GOOGLE_API_KEY;
const IMAGE_MODEL = process.env.GOOGLE_IMAGE_MODEL || 'imagen-3.0-generate';

// Middleware
app.use(cors());
app.use(express.json());
app.use('/images', express.static(path.join(__dirname, 'images')));

// Health check
app.get('/', (req, res) => {
  res.json({ status: 'OK', service: 'PersonajeIA Node.js Backend', version: '1.0.0' });
});

// Crear directorio para imagenes si no existe
const imagesDir = path.join(__dirname, 'images');
if (!fs.existsSync(imagesDir)) {
  fs.mkdirSync(imagesDir, { recursive: true });
}

// Inicializar Gemini
const ai = new GoogleGenAI({
  apiKey: GOOGLE_API_KEY
});

const extractInlineImages = (response) => {
  const parts = response?.candidates?.flatMap((candidate) => candidate.content?.parts || []) || [];
  return parts
    .map((part) => part.inlineData?.data)
    .filter(Boolean);
};

// Endpoint para generar personaje
app.post('/generate-character', async (req, res) => {
  try {
    if (!GOOGLE_API_KEY) {
      return res.status(500).json({ error: 'Falta configurar GOOGLE_API_KEY' });
    }

    const { prompt } = req.body;
    if (!prompt || !prompt.trim()) {
      return res.status(400).json({ error: 'Prompt de personaje requerido' });
    }

    // Prompt optimizado para personajes realistas
    const fullPrompt = `${prompt}. Create a highly realistic human character suitable for narrating horror stories. Photorealistic, detailed face, natural lighting, professional portrait photography.`;

    const response = await ai.models.generateImages({
      model: IMAGE_MODEL,
      prompt: fullPrompt,
      config: {
        numberOfImages: 1,
        aspectRatio: '9:16',
      },
    });

    const generated = response.generatedImages?.[0];
    const imageBytes = generated?.image?.imageBytes;

    if (!imageBytes) {
      const blocked = generated?.raiFilteredReason;
      return res.status(500).json({
        error: blocked
          ? `Modelo filtro la imagen: ${blocked}`
          : 'No se pudo generar la imagen con el modelo seleccionado',
      });
    }

    const buffer = Buffer.from(imageBytes, 'base64');
    const filename = `character_${Date.now()}.png`;
    const filepath = path.join(imagesDir, filename);

    fs.writeFileSync(filepath, buffer);

    res.json({
      success: true,
      imageUrl: `http://localhost:${PORT}/images/${filename}`,
      filepath: filepath,
    });
  } catch (error) {
    console.error('Error generating character:', error);
    res.status(500).json({ error: error.message });
  }
});

// Endpoint para generar expresiones
app.post('/generate-expressions', async (req, res) => {
  try {
    if (!GOOGLE_API_KEY) {
      return res.status(500).json({ error: 'Falta configurar GOOGLE_API_KEY' });
    }

    const { baseImage, expressions } = req.body;
    if (!baseImage || !expressions?.length) {
      return res.status(400).json({ error: 'Se requieren la imagen base y al menos una expresion' });
    }

    const baseImageData = baseImage.includes('base64,') ? baseImage.split('base64,')[1] : baseImage;
    const results = [];

    for (const expression of expressions) {
      const prompt = `Take this character and create a ${expression} expression. Maintain the same person, same appearance, only change the facial expression to be ${expression}. Photorealistic, highly detailed.`;

      const response = await ai.models.generateContent({
        model: 'gemini-2.0-flash-001',
        contents: [
          { text: prompt },
          { inlineData: { mimeType: 'image/png', data: baseImageData } },
        ],
      });

      const inlineImages = extractInlineImages(response);
      if (!inlineImages.length) {
        continue;
      }

      const buffer = Buffer.from(inlineImages[0], 'base64');
      const filename = `expression_${expression}_${Date.now()}.png`;
      const filepath = path.join(imagesDir, filename);

      fs.writeFileSync(filepath, buffer);
      results.push({
        expression,
        imageUrl: `http://localhost:${PORT}/images/${filename}`,
        filepath: filepath,
      });
    }

    res.json({ success: true, expressions: results });
  } catch (error) {
    console.error('Error generating expressions:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Backend Node.js running on port ${PORT}`);
});
