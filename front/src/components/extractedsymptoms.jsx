export default function ExtractedSymptoms({ symptoms, onContinue, onBack }) {
  return (
    <div className="max-w-xl mx-auto mt-10 bg-white rounded-xl shadow-md p-6 text-center">
      <h2 className="text-2xl font-bold text-purple-700 mb-4">✅ Extracted Symptoms</h2>

      {symptoms.length === 0 ? (
        <p className="text-gray-600 italic">No symptoms were extracted.</p>
      ) : (
        <ul className="text-left list-disc list-inside text-gray-800 mb-4">
          {symptoms.map((sym, idx) => (
            <li key={idx}>{sym}</li>
          ))}
        </ul>
      )}

      <div className="flex justify-center gap-4 mt-6">
        <button
          onClick={onBack}
          className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
        >
          ✏️ Edit Symptoms
        </button>

        <button
          onClick={onContinue}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
        >
          👉 Proceed to Follow-Up
        </button>
      </div>
    </div>
  );
}
