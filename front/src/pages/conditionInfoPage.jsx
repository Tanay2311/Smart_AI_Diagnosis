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

  const handleContinue = () => {
    navigate("/post-diagnosis-chat", { state: { conditions } });
  };

  return (
    <div className="min-h-screen bg-sky-50 dark:bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border dark:border-gray-700">
        <h1 className="text-3xl font-bold text-sky-700 dark:text-sky-300 mb-6 text-center">
          📋 What Should I Do Now?
        </h1>

        <p className="text-sm text-gray-600 dark:text-gray-400 mb-6 text-center italic">
          ⚠️ This is not a substitute for professional medical advice. Always consult a licensed healthcare provider.
        </p>

        {infoList.map((item, idx) => (
          <div
            key={idx}
            className="mb-6 p-4 bg-white dark:bg-gray-700 border-l-4 border-sky-500 dark:border-sky-400 rounded-md shadow-sm"
          >
            <h2 className="text-xl font-semibold text-indigo-800 dark:text-indigo-300 mb-2">
              🩺 {item.name}
            </h2>
            <p className="text-gray-800 dark:text-gray-300 mb-3 leading-relaxed">
              {item.description}
            </p>

            <div className="text-gray-800 dark:text-gray-300 text-sm">
              <p className="font-semibold text-sky-700 dark:text-sky-300">Treatment:</p>
              <ul className="list-disc list-inside ml-2 mb-3">
                {item.treatments.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>

              <p className="font-semibold text-sky-700 dark:text-sky-300">Risk Factors:</p>
              <ul className="list-disc list-inside ml-2">
                {item.risks.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}

        <div className="text-center mt-10 flex flex-col gap-4">
          <button
            onClick={handleContinue}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white rounded-lg transition font-semibold"
          >
            💬 Chat About Next Steps
          </button>
          <button
            onClick={handleRestart}
            className="px-6 py-2 bg-gray-400 hover:bg-gray-500 dark:bg-gray-600 dark:hover:bg-gray-500 text-white rounded-lg transition font-medium"
          >
            🔁 Start New Session
          </button>
        </div>
      </div>
    </div>
  );
}
