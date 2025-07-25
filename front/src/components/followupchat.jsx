import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "react-hot-toast";

const API_URL = "http://127.0.0.1:8000";

const onsetOptions = [
  "Today",
  "Yesterday",
  "Couple of days ago",
  "More than a week ago",
];
const severityLevels = ["1", "2", "3", "4", "5"];
const patternOptions = ["Constant", "Comes and goes"];

export default function FollowUpChat({ symptoms, onComplete, onBack }) {
  const [followUps, setFollowUps] = useState({});
  const [answers, setAnswers] = useState({});
  const [currentSymptomIndex, setCurrentSymptomIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [extraInput, setExtraInput] = useState("");
  const [showExtraInput, setShowExtraInput] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchFollowUps = async () => {
      try {
        const cleanedSymptoms = symptoms.map((s) => s.toLowerCase().trim());
        const response = await axios.post(`${API_URL}/get_followups`, {
          symptoms: cleanedSymptoms,
        });

        setFollowUps(response.data);
      } catch (err) {
        console.error("Failed to fetch follow-up questions:", err);
      }
    };
    fetchFollowUps();
  }, [symptoms]);

  const handleNext = () => {
    const currentSymptom = symptoms[currentSymptomIndex];
    const currentQs = followUps[currentSymptom] || [];

    const updatedAnswers = { ...answers };
    if (!updatedAnswers[currentSymptom]) updatedAnswers[currentSymptom] = [];
    updatedAnswers[currentSymptom].push(currentAnswer);
    setAnswers(updatedAnswers);
    setCurrentAnswer("");

    if (currentQuestionIndex + 1 < currentQs.length) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else if (currentSymptomIndex + 1 < symptoms.length) {
      setCurrentSymptomIndex(currentSymptomIndex + 1);
      setCurrentQuestionIndex(0);
    } else {
      setShowExtraInput(true);
    }
  };

  const handleFinalSubmit = () => {
    setSubmitting(true);
    toast.success("✅ Response submitted! Generating diagnosis...");
    onComplete(answers, extraInput);
  };

  const currentSymptom = symptoms[currentSymptomIndex];
  const currentQuestion =
    followUps[currentSymptom]?.[currentQuestionIndex] || "";

  const baseInputStyles =
    "w-full px-4 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400";

  const renderInputField = () => {
    switch (currentQuestionIndex) {
      case 0:
        return (
          <select
            className={`${baseInputStyles} mb-4`}
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
          >
            <option value="">Select onset time</option>
            {onsetOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        );
      case 1:
        return (
          <div className="mb-6">
            <input
              type="range"
              min="0"
              max="4"
              value={severityLevels.indexOf(currentAnswer)}
              onChange={(e) => setCurrentAnswer(severityLevels[e.target.value])}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-1">
              {severityLevels.map((level, index) => (
                <span key={index}>{level}</span>
              ))}
            </div>
          </div>
        );
      case 2:
        return (
          <input
            type="text"
            className={`${baseInputStyles} mb-4`}
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder="Type your answer here"
          />
        );
      case 3:
        return (
          <select
            className={`${baseInputStyles} mb-4`}
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
          >
            <option value="">Select pattern</option>
            {patternOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 rounded-xl shadow-lg p-6 transition-colors">
      <h2 className="text-2xl font-bold text-indigo-600 dark:text-indigo-300 mb-6">
        🔍 Follow-Up Questions
      </h2>

      {!showExtraInput ? (
        <>
          <p className="text-base font-medium mb-2">
            Symptom:{" "}
            <span className="text-indigo-700 dark:text-indigo-400">
              {currentSymptom}
            </span>
          </p>
          <p className="mb-4">{currentQuestion}</p>

          {renderInputField()}

          <div className="flex justify-between mt-6">
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-300 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded hover:bg-gray-400 dark:hover:bg-gray-600 transition"
            >
              ← Back
            </button>

            <button
              onClick={handleNext}
              disabled={!currentAnswer.trim()}
              className={`px-6 py-2 rounded transition font-medium ${
                currentAnswer.trim()
                  ? "bg-indigo-600 dark:bg-indigo-500 text-white hover:bg-indigo-700 dark:hover:bg-indigo-600"
                  : "bg-gray-300 text-gray-500 cursor-not-allowed"
              }`}
            >
              Next →
            </button>
          </div>
        </>
      ) : (
        <>
          <p className="mb-4 font-medium">
            📝 Anything else you'd like to mention?
          </p>
          <textarea
            rows={3}
            value={extraInput}
            onChange={(e) => setExtraInput(e.target.value)}
            placeholder="Enter additional notes here..."
            className={`${baseInputStyles} mb-4 resize-none`}
          />
          <button
            onClick={handleFinalSubmit}
            disabled={submitting}
            className={`px-6 py-2 w-full rounded font-semibold transition ${
              submitting
                ? "bg-gray-400 text-white cursor-not-allowed"
                : "bg-emerald-600 hover:bg-emerald-700 text-white"
            }`}
          >
            {submitting ? "Submitting..." : "Submit for Diagnosis"}
          </button>
        </>
      )}
    </div>
  );
}
