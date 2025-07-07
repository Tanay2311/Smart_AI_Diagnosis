import { useState, useEffect } from "react";

export default function FollowUpChat({ symptoms, onComplete }) {
  const mockQuestions = {
    headache: ["When did your headache start?", "How severe is it?", "Does it come and go?", "Any sensitivity to light?"],
    fever: ["How high is your temperature?", "Since when do you have a fever?", "Any chills or sweating?", "Are you taking any meds?"],
    cough: ["Is your cough dry or wet?", "How long have you had it?", "Any blood in cough?", "Do you have chest pain?"]
  };

  const [qaPairs, setQaPairs] = useState([]);
  const [currentSymptomIndex, setCurrentSymptomIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswer, setUserAnswer] = useState("");

  const symptom = symptoms[currentSymptomIndex];
  const questions = mockQuestions[symptom] || ["Describe it more."];

  const handleAnswerSubmit = (e) => {
    e.preventDefault();
    const updatedQA = [...qaPairs, {
      symptom,
      question: questions[currentQuestionIndex],
      answer: userAnswer,
    }];
    setQaPairs(updatedQA);
    setUserAnswer("");

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else if (currentSymptomIndex < symptoms.length - 1) {
      setCurrentSymptomIndex(currentSymptomIndex + 1);
      setCurrentQuestionIndex(0);
    } else {
      onComplete(updatedQA); // Done
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-xl font-bold mb-4 text-purple-700">
        🤖 Follow-up for "{symptom}"
      </h2>
      <p className="mb-4 text-gray-800">{questions[currentQuestionIndex]}</p>
      <form onSubmit={handleAnswerSubmit}>
        <input
          type="text"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4"
          value={userAnswer}
          onChange={(e) => setUserAnswer(e.target.value)}
          required
        />
        <button
          type="submit"
          className="px-6 py-2 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition"
        >
          Submit Answer
        </button>
      </form>
    </div>
  );
}
