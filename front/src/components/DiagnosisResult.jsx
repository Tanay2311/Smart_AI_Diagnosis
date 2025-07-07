export default function DiagnosisResult({ result, onRestart }) {
  return (
    <div className="max-w-2xl mx-auto mt-10 bg-white rounded-xl shadow-md p-6 text-center">
      <h2 className="text-2xl font-bold text-purple-700 mb-4">🧠 Final Diagnosis</h2>
      <p className="text-xl text-gray-800 font-medium mb-2">{result.disease}</p>
      <p className="text-gray-600 mb-4 italic">"{result.description}"</p>

      <div className="text-left mt-4">
        <p><span className="font-semibold text-purple-600">Treatment:</span> {result.treatment}</p>
        <p className="mt-2"><span className="font-semibold text-purple-600">Risk Factors:</span> {result.risk_factors}</p>
      </div>

      <button
        onClick={onRestart}
        className="mt-6 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
      >
        🔁 Start New Session
      </button>
    </div>
  );
}
