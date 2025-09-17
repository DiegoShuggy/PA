import './App.css'; // Esta línea ya está, ¡perfecto!

function App() {
  return (
    <div className="bg-blue-500 text-white p-8 text-center min-h-screen">
      <h1 className="text-4xl font-bold mb-4">¡InA está funcionando!</h1>
      <p className="text-xl">Tailwind CSS está configurado correctamente ✅</p>
      <div className="mt-8">
        <button className="bg-white text-blue-500 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100">
          Botón de Prueba
        </button>
      </div>
    </div>
  );
}

export default App;