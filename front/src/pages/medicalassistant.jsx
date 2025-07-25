import { useState } from "react";
import axios from "axios";

import SymptomInputForm from "../components/symptominputform";
import ExtractedSymptoms from "../components/extractedsymptoms";
import FollowUpChat from "../components/followupchat";
import DiagnosisResult from "../components/DiagnosisResult";
import ProgressTracker from "../components/ProgressTracker";

const API_URL = "http://127.0.0.1:8000";

function MedicalAssistant() {
  const [symptomText, setSymptomText] = useState("");
  const [step, setStep] = useState("input");
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [addedSymptoms, setAddedSymptoms] = useState([]);
  const [followUpQA, setFollowUpQA] = useState({});
  const [extraNotes, setExtraNotes] = useState("");
  const [diagnosisResult, setDiagnosisResult] = useState(null);

  const handleSymptomExtraction = async (text) => {
    setSymptomText(text);
    try {
      const response = await axios.post(`${API_URL}/extract_symptoms`, {
        text,
      });
      const symptoms = response.data.extracted_symptoms || [];
      setExtractedSymptoms(symptoms);
      setStep("extracted");
    } catch (error) {
      console.error("Symptom extraction failed:", error);
      alert("❌ Symptom extraction failed. Please try again.");
    }
  };

  const handleContinueToFollowUp = () => {
    setStep("followup");
  };

  const handleBackToExtracted = () => {
    setStep("extracted");
  };

  const handleBackToSymptoms = () => {
    setStep("input");
  };

  const handleAddSymptom = (symptom) => {
    if (!addedSymptoms.includes(symptom.toLowerCase())) {
      setAddedSymptoms([...addedSymptoms, symptom.toLowerCase()]);
    }
  };

  const handleRemoveSymptom = (symptom) => {
    setAddedSymptoms(addedSymptoms.filter((s) => s !== symptom.toLowerCase()));
  };

  const allSymptoms = [
    ...new Set([...extractedSymptoms, ...addedSymptoms]),
  ].map((s) => s.toLowerCase().trim());

  const demographics =
    JSON.parse(localStorage.getItem("user_demographics")) || {};
  const userName = demographics.name || "there";

  const handleFollowUpComplete = async (qaData, notes = "") => {
    setFollowUpQA(qaData);
    setExtraNotes(notes);

    const payload = {
      symptoms:allSymptoms.join(", "),
      followup_answers: qaData,
      extra_input: notes,
      name: demographics.name || null,
      age: demographics.age ? parseInt(demographics.age) : null,
      gender: demographics.gender || null,
      country: demographics.country || null,
    };

    console.log("📦 Sending payload:", payload);

    try {
      const response = await axios.post(`${API_URL}/diagnose`, payload);
      setDiagnosisResult(response.data.diagnosis);
      setStep("diagnosis");
    } catch (error) {
      console.error("Diagnosis failed:", error);
      alert("❌ Diagnosis generation failed. Please try again.");
    }
  };

  const handleRestart = () => {
    setSymptomText("");
    setExtractedSymptoms([]);
    setFollowUpQA({});
    setExtraNotes("");
    setDiagnosisResult(null);
    setStep("input");
  };

  return (
    <div className="min-h-screen bg-blue-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-900 shadow-xl rounded-2xl p-8 space-y-6 border border-gray-200 dark:border-gray-700">
        <h1 className="text-3xl font-bold text-center text-purple-700 dark:text-purple-400">
          🩺 Smart AI Medical Assistant
        </h1>
        <h2 className="text-lg text-center text-gray-700 dark:text-gray-300">
          Hello, {userName}! Let's get started with your diagnosis.
        </h2>

        <ProgressTracker
          step={
            step === "input"
              ? 0
              : step === "extracted"
              ? 1
              : step === "followup"
              ? 2
              : step === "diagnosis"
              ? 3
              : 0
          }
        />

        <div className="mt-4">
          {step === "input" && (
            <SymptomInputForm onSubmit={handleSymptomExtraction} />
          )}

          {step === "extracted" && (
            <ExtractedSymptoms
              symptoms={[...new Set([...extractedSymptoms, ...addedSymptoms])]} // merged
              onAddSymptom={handleAddSymptom}
              onRemoveSymptom={handleRemoveSymptom}
              onContinue={handleContinueToFollowUp}
              onBack={handleBackToSymptoms}
            />
          )}

          {step === "followup" && (
            <FollowUpChat
              symptoms={allSymptoms}
              onComplete={handleFollowUpComplete}
              onBack={handleBackToExtracted}
              onRestartFollowUp={() => setFollowUpQA({})}
            />
          )}

          {step === "diagnosis" && diagnosisResult && (
            <DiagnosisResult
              symptomText={allSymptoms.join(', ')}
              followUpAnswers={followUpQA}
              extraNotes={extraNotes}
              onRestart={handleRestart}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default MedicalAssistant;
