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

  const demographics =
    JSON.parse(localStorage.getItem("user_demographics")) || {};
  const userName = demographics.name || "there";

  const handleFollowUpComplete = async (qaData, notes = "") => {
    setFollowUpQA(qaData);
    setExtraNotes(notes);

    const payload = {
      symptoms: symptomText,
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
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-200 p-8">
      <h1 className="text-3xl font-bold text-center text-purple-700 mb-8">
        🩺 Smart AI Medical Assistant
      </h1>
      <h2 className="text-xl text-center text-gray-800 mb-6">
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

      {step === "input" && (
        <SymptomInputForm onSubmit={handleSymptomExtraction} />
      )}

      {step === "extracted" && (
        <ExtractedSymptoms
          symptoms={extractedSymptoms}
          onContinue={handleContinueToFollowUp}
          onBack={handleBackToSymptoms}
        />
      )}

      {step === "followup" && (
        <FollowUpChat
          symptoms={extractedSymptoms}
          onComplete={handleFollowUpComplete}
          onBack={handleBackToExtracted}
          onRestartFollowUp={() => setFollowUpQA({})}
        />
      )}

      {step === "diagnosis" && diagnosisResult && (
        <DiagnosisResult
          symptomText={symptomText}
          followUpAnswers={followUpQA}
          extraNotes={extraNotes}
          onRestart={handleRestart}
        />
      )}
    </div>
  );
}

export default MedicalAssistant;
