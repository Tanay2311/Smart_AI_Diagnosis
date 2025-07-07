import { useState } from "react";
import SymptomInputForm from "../components/symptominputform";
import ExtractedSymptoms from "../components/extractedsymptoms";
import FollowUpChat from "../components/followupchat";
import DiagnosisResult from "../components/DiagnosisResult";


function MedicalAssistant() {
  const [symptomText, setSymptomText] = useState("");
  const [step, setStep] = useState("input");
  const [extractedSymptoms, setExtractedSymptoms] = useState([]);
  const [followUpQA, setFollowUpQA] = useState([]);

  // Mock diagnosis data – replace with backend response later
  const mockDiagnosis = {
    disease: "Viral Infection",
    description: "Common viral illness causing fever and headache.",
    treatment: "Rest, fluids, and paracetamol.",
    risk_factors: "Low immunity, recent exposure to infected people."
  };

  const handleSymptomSubmit = (text) => {
    setSymptomText(text);

    // TODO: Replace this mock with backend call
    const mockSymptoms = ["headache", "fever"];
    setExtractedSymptoms(mockSymptoms);
    setStep("extracted");
  };

  const handleContinueToFollowUp = () => {
    setStep("followup");
  };

  const handleFollowUpComplete = (qaData) => {
    setFollowUpQA(qaData);
    setStep("diagnosis");
  };

  const handleRestart = () => {
    setSymptomText("");
    setExtractedSymptoms([]);
    setFollowUpQA([]);
    setStep("input");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-200 p-8">
      <h1 className="text-3xl font-bold text-center text-purple-700 mb-8">
        🩺 Smart AI Medical Assistant
      </h1>

      {step === "input" && (
        <SymptomInputForm onSubmit={handleSymptomSubmit} />
      )}

      {step === "extracted" && (
        <ExtractedSymptoms
          symptoms={extractedSymptoms}
          onContinue={handleContinueToFollowUp}
        />
      )}

      {step === "followup" && (
        <FollowUpChat
          symptoms={extractedSymptoms}
          onComplete={handleFollowUpComplete}
        />
      )}

      {step === "diagnosis" && (
        <DiagnosisResult result={mockDiagnosis} onRestart={handleRestart} />
      )}
    </div>
  );
}

export default MedicalAssistant;
