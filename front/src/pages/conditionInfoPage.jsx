// src/pages/ConditionInfoPage.jsx

import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "react-hot-toast";

const API_URL = "http://127.0.0.1:8000";

export default function ConditionInfoPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [infoList, setInfoList] = useState([]);

  const conditions = location.state?.conditions || [];

  useEffect(() => {
    const fetchConditionInfo = async () => {
      if (!conditions.length) {
        toast.error("No conditions provided.");
        return;
      }

      try {
        const response = await axios.post(`${API_URL}/condition_info`, {
          conditions,
        });
        setInfoList(response.data);
      } catch (error) {
        console.error("Failed to fetch condition info:", error);
        toast.error("Failed to load condition details.");
      }
    };

    fetchConditionInfo();
  }, [conditions]);

  const handleRestart = () => {
    navigate("/");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-200 p-6">
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-md p-6">
        <h1 className="text-3xl font-bold text-purple-700 mb-6 text-center">
          📋 What Should I Do Now?
        </h1>

        <p className="text-sm text-gray-600 mb-6 text-center italic">
          ⚠️ Please note: This is not a substitute for professional medical advice.
          Always consult a licensed healthcare provider for a proper diagnosis and treatment plan.
        </p>

        {infoList.map((item, idx) => (
          <div
            key={idx}
            className="mb-6 p-4 bg-purple-50 border-l-4 border-purple-600 rounded-md"
          >
            <h2 className="text-xl font-semibold text-purple-800 mb-1">
              🩺 {item.name}
            </h2>
            <p className="text-gray-700 mb-2">{item.description}</p>

            <div className="text-gray-800 text-sm">
              <p className="font-semibold text-purple-700">Treatment:</p>
              <ul className="list-disc list-inside ml-2 mb-2">
                {item.treatments.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>

              <p className="font-semibold text-purple-700">Risk Factors:</p>
              <ul className="list-disc list-inside ml-2">
                {item.risks.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}

        <div className="text-center mt-8">
          <button
            onClick={handleRestart}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            🔁 Start New Session
          </button>
        </div>
      </div>
    </div>
  );
}
