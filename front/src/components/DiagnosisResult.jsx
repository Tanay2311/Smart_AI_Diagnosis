import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";

const API_URL = "http://127.0.0.1:8000";

function parseDiagnosis(diagnosisText) {
  const conditions = diagnosisText
    .split(/\d+\.\s*Condition Name:/)
    .filter(Boolean)
    .map((chunk) => {
      const [nameLine, ...rest] = chunk.split("\n");
      const name = nameLine.trim();
      const reason = rest.join("\n").replace("Reason:", "").trim();
      return { name, reason };
    });
  return conditions;
}

export default function DiagnosisResult({
  symptomText,
  followUpAnswers,
  extraNotes,
}) {
  const [diagnosis, setDiagnosis] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const handleDiagnosisSubmit = async () => {
      try {
        toast.loading("Submitting details for diagnosis...", { id: "diag" });

        const demographics =
          JSON.parse(localStorage.getItem("user_demographics")) || {};

        const payload = {
          symptoms: symptomText?.trim(),
          followup_answers: followUpAnswers,
          extra_input: extraNotes || "",
          age: demographics.age ? parseInt(demographics.age) : null,
          gender: demographics.gender || null,
          country: demographics.country || null,
        };

        console.log("📦 Payload being sent:", payload);

        const response = await axios.post(`${API_URL}/diagnose`, payload);
        setDiagnosis(response.data.diagnosis);
        toast.success("Diagnosis ready!", { id: "diag" });
      } catch (error) {
        console.error("Diagnosis API failed:", error);
        setDiagnosis("❌ Failed to generate diagnosis. Please try again.");
        toast.error("Diagnosis generation failed.", { id: "diag" });
      } finally {
        setLoading(false);
      }
    };

    handleDiagnosisSubmit();
  }, [symptomText, followUpAnswers, extraNotes]);

  const parsedDiagnosis = parseDiagnosis(diagnosis);

  const handleSeeNextSteps = () => {
    const conditionNames = parsedDiagnosis.map((c) => c.name);
    navigate("/condition-info", { state: { conditions: conditionNames } });
  };

  return (
    <div className="max-w-2xl mx-auto mt-10 bg-white rounded-xl shadow-md p-6 text-center">
      <h2 className="text-2xl font-bold text-purple-700 mb-6">
        🧠 Final Diagnosis
      </h2>

      {loading ? (
        <p className="text-gray-600 italic">Generating diagnosis...</p>
      ) : typeof diagnosis === "string" && diagnosis.startsWith("❌") ? (
        <p className="text-red-600 font-semibold">{diagnosis}</p>
      ) : (
        parsedDiagnosis.map((cond, idx) => (
          <div
            key={idx}
            className="mb-6 p-4 border-l-4 border-purple-600 bg-purple-50 rounded-md text-left"
          >
            <h3 className="text-xl font-semibold text-purple-800 mb-2">
              🩺 {cond.name}
            </h3>
            <p className="text-gray-700 whitespace-pre-line">{cond.reason}</p>
          </div>
        ))
      )}

      {!loading && !diagnosis.startsWith("❌") && (
        <button
          onClick={handleSeeNextSteps}
          className="mt-6 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          📋 What Should I Do Now?
        </button>
      )}
    </div>
  );
}
