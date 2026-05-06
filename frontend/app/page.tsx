'use client';
import React, { useState } from 'react';
import Link from 'next/link';

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [outputPath, setOutputPath] = useState('/output/videos');
  const [resolution, setResolution] = useState<[number, number]>([1920, 1080]);
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setStatus('processing');
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/generate-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          output_path: outputPath,
          resolution,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate video');
      }
      
      const data = await response.json();
      setStatus('completed');
      setResult(data);
      
    } catch (err: any) {
      setStatus(null);
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-blue-900 text-white">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">🎬 AutoVid</h1>
          <nav className="space-x-4">
            <Link href="/" className="hover:text-blue-300 transition">Home</Link>
            <a 
              href="https://github.com/govindtank/autovid" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-300 transition"
            >
              GitHub ↗
            </a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="text-center mb-12">
          <h2 className="text-5xl font-bold mb-4">Create Videos from Text</h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            AI-powered video generation platform. Simply describe your scene, 
            and AutoVid will decompose it into shots, download matching footage, 
            add voice-over, and compile everything into a beautiful video.
          </p>
        </section>

        {/* Form */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column - Input Form */}
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-semibold mb-4">📝 Create New Video</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Prompt Input */}
              <div>
                <label htmlFor="prompt" className="block text-sm font-medium mb-2">
                  Video Description (Prompt)
                </label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="A peaceful morning in a forest with sunlight filtering through trees, birds chirping..."
                  className="w-full h-32 px-4 py-3 bg-black/30 border border-white/20 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-white placeholder-gray-400"
                  required
                />
              </div>

              {/* Settings Panel */}
              <div className="bg-black/20 rounded-lg p-4 space-y-3">
                <h4 className="text-sm font-semibold text-blue-300">⚙️ Settings</h4>
                
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Output Path</label>
                  <input
                    type="text"
                    value={outputPath}
                    onChange={(e) => setOutputPath(e.target.value)}
                    className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs text-gray-400 mb-1">Resolution (Width × Height)</label>
                  <input
                    type="text"
                    value={`${resolution[0]}×${resolution[1]}`}
                    onChange={(e) => {
                      const [w, h] = e.target.value.split('×').map(n => parseInt(n.trim()));
                      setResolution([w || 1920, h || 1080]);
                    }}
                    className="w-full px-3 py-2 bg-black/50 border border-white/10 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={!prompt || status === 'processing'}
                className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
                  !prompt || status === 'processing'
                    ? 'bg-gray-600 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-lg'
                }`}
              >
                {status === 'processing' ? (
                  <span className="flex items-center justify-center gap-2">
                    ⏳ Processing...
                  </span>
                ) : (
                  '🚀 Generate Video'
                )}
              </button>
            </form>

            {/* Status Indicator */}
            {status === 'processing' && (
              <div className="mt-4 p-3 bg-blue-500/20 rounded-lg border border-blue-500/30">
                <p className="text-sm text-blue-200">✨ Decomposing prompt into scenes...</p>
                <p className="text-xs text-blue-300 mt-1">This will take a few minutes</p>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mt-4 p-3 bg-red-500/20 rounded-lg border border-red-500/30">
                <p className="text-sm text-red-200">❌ Error: {error}</p>
              </div>
            )}
          </div>

          {/* Right Column - Results Preview */}
          <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
            {!result ? (
              <div className="h-full flex flex-col justify-center items-center text-center text-gray-400">
                <div className="text-6xl mb-4">🎬</div>
                <h3 className="text-xl font-semibold mb-2">No Video Generated Yet</h3>
                <p className="mb-4">Fill out the form and click "Generate Video" to create your first AI-powered video!</p>
                
                {/* Feature Highlights */}
                <div className="grid grid-cols-2 gap-4 mt-6 text-xs">
                  <div className="bg-white/5 rounded-lg p-3">
                    <span className="text-2xl">🤖</span>
                    <p className="mt-1">LLM Scene Decomposition</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <span className="text-2xl">📥</span>
                    <p className="mt-1">Auto-download from Pexels</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <span className="text-2xl">🎤</span>
                    <p className="mt-1">Voice Synthesis</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3">
                    <span className="text-2xl">✂️</span>
                    <p className="mt-1">Smart Video Merging</p>
                  </div>
                </div>
              </div>
            ) : (
              <>
                <h3 className="text-xl font-semibold mb-4 text-green-300">✅ Generation Complete!</h3>
                
                <div className="bg-black/20 rounded-lg p-4 space-y-3 mb-4">
                  <p className="text-sm"><span className="text-gray-400">Task ID:</span> {result.task_id}</p>
                  <p className="text-sm"><span className="text-gray-400">Status:</span> {result.status}</p>
                  <p className="text-sm"><span className="text-gray-400">Scenes:</span> {result.scenes_count || 'N/A'}</p>
                  <p className="text-sm"><span className="text-gray-400">Duration:</span> {result.duration ? `${result.duration}s` : 'N/A'}</p>
                  <p className="text-sm"><span className="text-gray-400">Created:</span> {result.created_at ? result.created_at.substring(0, 19) : 'N/A'}</p>
                </div>

                {/* Video Preview */}
                {result.output_path && (
                  <div className="space-y-3">
                    <div className="bg-black/40 rounded-lg p-4 border border-white/20">
                      <p className="text-sm text-gray-400 mb-2">📂 Final Video File:</p>
                      <code className="block break-all text-green-300 font-mono text-xs">
                        {result.output_path}
                      </code>
                    </div>

                    <a
                      href={result.output_path.replace(/^\//, '')}
                      download={`autovid_${result.task_id}.mp4`}
                      className="block w-full py-3 bg-green-600 hover:bg-green-700 rounded-xl text-center font-semibold transition-colors"
                    >
                      ⬇️ Download Video
                    </a>
                  </div>
                )}

                {/* Error display */}
                {error && (
                  <div className="mt-4 p-3 bg-red-500/20 rounded-lg border border-red-500/30">
                    <p className="text-sm text-red-200">❌ Error: {error}</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 border-t border-white/10 pt-8 text-center text-gray-400">
          <p className="mb-2">AutoVid AI-Powered Video Generation Platform</p>
          <p className="text-sm">
            Powered by OpenAI LLMs, Pexels API, and Edge TTS • MIT License
          </p>
        </footer>
      </main>
    </div>
  );
}
