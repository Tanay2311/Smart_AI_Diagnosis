export default function ExtractedSymptoms({ symptoms, onContinue }) {
  return (
    <div className="text-center mt-10">
      <h2 className="text-2xl font-semibold text-purple-700 mb-4">
        Extracted Symptoms
      </h2>
      <ul className="flex flex-wrap justify-center gap-2 mb-6">
        {symptoms.map((symptom, index) => (
          <li
            key={index}
            className="px-4 py-2 bg-purple-100 text-purple-800 rounded-full shadow"
          >
            {symptom}
          </li>
        ))}
      </ul>
      <button
        onClick={onContinue}
        className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
      >
        Continue to Follow-Up Questions
      </button>
    </div>
  );
}
