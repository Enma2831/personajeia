const express = require('express');
const cors = require('cors');
const { GoogleGenAI } = require('@google/genai');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3002;

// Middleware
app.use(cors());
app.use(express.json());
app.use('/images', express.static(path.join(__dirname, 'images')));

// Health check
app.get('/', (req, res) => {
  res.json({ status: 'OK', service: 'PersonajeIA Node.js Backend', version: '1.0.0' });
});

// Crear directorio para imágenes si no existe
if (!fs.existsSync('images')) {
  fs.mkdirSync('images');
}

// Inicializar Gemini
const ai = new GoogleGenAI({
  // Configurar API key - usar variable de entorno en producción
  apiKey: process.env.GOOGLE_API_KEY || 'your-api-key-here'
});

// Endpoint para generar personaje
app.post('/generate-character', async (req, res) => {
  try {
    const { prompt } = req.body;

    // Prompt optimizado para personajes realistas
    const fullPrompt = `${prompt}. Create a highly realistic human character suitable for narrating horror stories. Photorealistic, detailed face, natural lighting, professional portrait photography.`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-image",
      contents: fullPrompt,
    });

    // Procesar respuesta y guardar imagen
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        const buffer = Buffer.from(part.inlineData.data, "base64");
        const filename = `character_${Date.now()}.png`;
        const filepath = path.join(__dirname, 'images', filename);

        fs.writeFileSync(filepath, buffer);

        res.json({
          success: true,
          imageUrl: `http://localhost:${PORT}/images/${filename}`,
          filepath: filepath
        });
        return;
      }
    }

    res.status(500).json({ error: 'No image generated' });

  } catch (error) {
    console.error('Error generating character:', error);
    res.status(500).json({ error: error.message });
  }
});

// Endpoint para generar expresiones
app.post('/generate-expressions', async (req, res) => {
  try {
    const { baseImage, expressions } = req.body;

    const results = [];

    for (const expression of expressions) {
      const prompt = `Take this character and create a ${expression} expression. Maintain the same person, same appearance, only change the facial expression to be ${expression}. Photorealistic, highly detailed.`;

      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-image",
        contents: [
          { text: prompt },
          { inlineData: { mimeType: "image/png", data: baseImage } }
        ],
      });

      // Procesar y guardar
      for (const part of response.candidates[0].content.parts) {
        if (part.inlineData) {
          const buffer = Buffer.from(part.inlineData.data, "base64");
          const filename = `expression_${expression}_${Date.now()}.png`;
          const filepath = path.join(__dirname, 'images', filename);

          fs.writeFileSync(filepath, buffer);
          results.push({
            expression,
            imageUrl: `http://localhost:${PORT}/images/${filename}`,
            filepath: filepath
          });
        }
      }
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