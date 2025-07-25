import { useState } from 'react';

export default function ExtractedSymptoms({
  symptoms,
  onContinue,
  onBack,
  onAddSymptom,
  onRemoveSymptom,
}) {
  const [newSymptom, setNewSymptom] = useState('');

  const handleAddClick = () => {
    if (newSymptom.trim()) {
      onAddSymptom(newSymptom.trim());
      setNewSymptom(''); // Clear input after adding
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddClick();
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 bg-blue-50 dark:bg-gray-900 rounded-xl shadow-md p-6 border border-blue-200 dark:border-gray-700">
      <h2 className="text-2xl font-bold text-blue-700 dark:text-blue-300 mb-4 text-center">
        ✅ Extracted Symptoms
      </h2>

      {symptoms.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-400 italic text-center">
          No symptoms were automatically extracted. Please add them manually.
        </p>
      ) : (
        <ul className="text-gray-800 dark:text-gray-200 mb-4 space-y-2">
          {symptoms.map((sym, idx) => (
            <li
              key={idx}
              className="flex justify-between items-center bg-white dark:bg-gray-800 p-2 rounded-md"
            >
              <span className="capitalize">{sym}</span>
              <button
                onClick={() => onRemoveSymptom(sym)}
                className="text-red-500 hover:text-red-700 font-bold text-xl px-2"
                aria-label={`Remove ${sym}`}
              >
                &times;
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* --- Section to Add New Symptoms --- */}
      <div className="mt-6 border-t border-blue-200 dark:border-gray-700 pt-4">
        <label
          htmlFor="add-symptom"
          className="block text-lg font-semibold text-gray-700 dark:text-gray-300 text-center mb-2"
        >
          Anything you'd like to add?
        </label>
        <div className="flex gap-2">
          <input
            id="add-symptom"
            type="text"
            value={newSymptom}
            onChange={(e) => setNewSymptom(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a symptom to add..."
            className="flex-grow px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleAddClick}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition"
          >
            ➕ Add
          </button>
        </div>
      </div>

      <div className="flex justify-center gap-4 mt-8">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
          ✏️ Go Back & Edit
        </button>

        <button
          onClick={onContinue}
          disabled={symptoms.length === 0}
          className="px-6 py-2 rounded-lg bg-teal-600 text-white hover:bg-teal-700 transition disabled:bg-teal-800 disabled:cursor-not-allowed"
        >
          👉 Proceed to Follow-Up
        </button>
      </div>
    </div>
  );
}