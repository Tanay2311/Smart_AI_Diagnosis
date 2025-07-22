export default function ExtractedSymptoms({ symptoms, onContinue, onBack }) {
  return (
    <div className="max-w-xl mx-auto mt-10 bg-blue-50 dark:bg-gray-900 rounded-xl shadow-md p-6 text-center border border-blue-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-blue-700 dark:text-blue-300 mb-4">✅ Extracted Symptoms</h2>

      {symptoms.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400 italic">No symptoms were extracted.</p>
      ) : (
        <ul className="text-left list-disc list-inside text-gray-800 dark:text-gray-200 mb-4">
          {symptoms.map((sym, idx) => (
            <li key={idx}>{sym}</li>
          ))}
        </ul>
      )}

      <div className="flex justify-center gap-4 mt-6">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
          ✏️ Edit Symptoms
        </button>

        <button
          onClick={onContinue}
          className="px-6 py-2 rounded-lg bg-teal-600 text-white hover:bg-teal-700 transition"
        >
          👉 Proceed to Follow-Up
        </button>
      </div>
    </div>
  );
}
