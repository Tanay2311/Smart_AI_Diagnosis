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
    <div className="max-w-2xl mx-auto mt-10 bg-sky-50 dark:bg-gray-900 rounded-xl shadow-lg p-6 text-center border dark:border-gray-700">
      <h2 className="text-2xl font-bold text-sky-700 dark:text-sky-300 mb-6">
        🧠 Final Diagnosis
      </h2>

      {loading ? (
        <p className="text-gray-600 dark:text-gray-400 italic">
          Generating diagnosis...
        </p>
      ) : typeof diagnosis === "string" && diagnosis.startsWith("❌") ? (
        <p className="text-red-600 dark:text-red-400 font-semibold">
          {diagnosis}
        </p>
      ) : (
        parsedDiagnosis.map((cond, idx) => (
          <div
            key={idx}
            className="mb-6 p-4 border-l-4 border-sky-500 dark:border-sky-400 bg-white dark:bg-gray-800 rounded-md text-left shadow-sm"
          >
            <h3 className="text-lg font-semibold text-indigo-800 dark:text-indigo-300 mb-2">
              🩺 {cond.name}
            </h3>
            <p className="text-gray-800 dark:text-gray-300 whitespace-pre-line font-mono leading-relaxed">
              {cond.reason}
            </p>
          </div>
        ))
      )}

      {!loading && !diagnosis.startsWith("❌") && (
        <button
          onClick={handleSeeNextSteps}
          className="mt-6 px-6 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-lg transition font-semibold"
        >
          📋 What Should You Do Now?
        </button>
      )}
    </div>
  );
}
