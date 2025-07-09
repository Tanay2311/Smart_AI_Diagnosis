import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "react-hot-toast";

const API_URL = "http://127.0.0.1:8000";

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
        const response = await axios.post(`${API_URL}/get_followups`, symptoms);
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
  const currentQuestion = followUps[currentSymptom]?.[currentQuestionIndex] || "";

  return (
    <div className="max-w-xl mx-auto mt-10 bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold text-purple-700 mb-4">🔍 Follow-Up Questions</h2>

      {!showExtraInput ? (
        <>
          <p className="text-lg font-medium mb-2">
            Symptom: <span className="text-purple-600">{currentSymptom}</span>
          </p>
          <p className="mb-4 text-gray-800">{currentQuestion}</p>

          <input
            type="text"
            className="w-full px-4 py-2 border border-gray-300 rounded mb-4"
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder="Type your answer here"
          />

          <div className="flex justify-between">
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition"
            >
              ← Back
            </button>

            <button
              onClick={handleNext}
              disabled={!currentAnswer.trim()}
              className={`px-6 py-2 rounded transition ${
                currentAnswer.trim()
                  ? "bg-purple-600 text-white hover:bg-purple-700"
                  : "bg-gray-300 text-gray-600 cursor-not-allowed"
              }`}
            >
              Next
            </button>
          </div>
        </>
      ) : (
        <>
          <p className="mb-4 text-gray-700 font-medium">
            📝 Anything else you'd like to mention?
          </p>
          <textarea
            rows={3}
            value={extraInput}
            onChange={(e) => setExtraInput(e.target.value)}
            placeholder="Enter additional notes here..."
            className="w-full px-4 py-2 border border-gray-300 rounded mb-4"
          />
          <button
            onClick={handleFinalSubmit}
            disabled={submitting}
            className={`px-6 py-2 w-full rounded transition ${
              submitting
                ? "bg-gray-400 text-white cursor-not-allowed"
                : "bg-green-600 text-white hover:bg-green-700"
            }`}
          >
            {submitting ? "Submitting..." : "Submit for Diagnosis"}
          </button>
        </>
      )}
    </div>
  );
}
