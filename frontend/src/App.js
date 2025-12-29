import React, { useState } from 'react';
import axios from 'axios';
import { Upload, Play, Download } from 'lucide-react';

function App() {
  const [characterPrompt, setCharacterPrompt] = useState('');
  const [storyText, setStoryText] = useState('');
  const [characterImage, setCharacterImage] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isNarrating, setIsNarrating] = useState(false);
  const [videoUrl, setVideoUrl] = useState(null);

  const generateCharacter = async () => {
    setIsGenerating(true);
    try {
      const response = await axios.post('http://localhost:3002/generate-character', {
        prompt: characterPrompt
      });
      setCharacterImage(response.data.imageUrl);
    } catch (error) {
      console.error('Error generating character:', error);
    }
    setIsGenerating(false);
  };

  const generateNarration = async () => {
    setIsNarrating(true);
    try {
      const response = await axios.post('http://localhost:8000/generate-narration', {
        story: storyText,
        characterImage: characterImage
      });
      setVideoUrl(response.data.videoUrl);
    } catch (error) {
      console.error('Error generating narration:', error);
    }
    setIsNarrating(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          PersonajeIA - Creador de Personajes Virtuales
        </h1>

        {/* Editor de Personaje */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Crear Personaje</h2>
          <textarea
            className="w-full p-3 border border-gray-300 rounded-md mb-4"
            rows="4"
            placeholder="Describe tu personaje realista para narrar historias de terror..."
            value={characterPrompt}
            onChange={(e) => setCharacterPrompt(e.target.value)}
          />
          <button
            onClick={generateCharacter}
            disabled={isGenerating}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md disabled:opacity-50"
          >
            {isGenerating ? 'Generando...' : 'Generar Personaje'}
          </button>
          {characterImage && (
            <div className="mt-4">
              <img src={characterImage} alt="Personaje generado" className="max-w-xs mx-auto rounded-lg" />
            </div>
          )}
        </div>

        {/* Narrador */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Narrar Historia</h2>
          <textarea
            className="w-full p-3 border border-gray-300 rounded-md mb-4"
            rows="8"
            placeholder="Pega tu historia de terror basada en experiencias reales..."
            value={storyText}
            onChange={(e) => setStoryText(e.target.value)}
          />
          <button
            onClick={generateNarration}
            disabled={isNarrating || !characterImage}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-md disabled:opacity-50"
          >
            {isNarrating ? 'Narrando...' : 'Generar Narración'}
          </button>
        </div>

        {/* Resultado */}
        {videoUrl && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Video Generado</h2>
            <video controls className="w-full max-w-md mx-auto">
              <source src={videoUrl} type="video/mp4" />
            </video>
            <div className="text-center mt-4">
              <a
                href={videoUrl}
                download="personaje_narracion.mp4"
                className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-md inline-flex items-center"
              >
                <Download className="mr-2" size={20} />
                Descargar Video
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;