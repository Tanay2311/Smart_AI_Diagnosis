import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function DemographicsForm() {
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [country, setCountry] = useState("");
  const [name, setName] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem(
      "user_demographics",
      JSON.stringify({ age, gender, country, name })
    );
    navigate("/assistant");
  };

  return (
    <div className="min-h-screen bg-sky-50 dark:bg-gray-900 flex items-center justify-center px-4 py-8 transition-colors">
      <form
        onSubmit={handleSubmit}
        className="bg-white dark:bg-gray-800 border border-purple-200 dark:border-gray-700 p-6 rounded-xl shadow-lg w-full max-w-sm"
      >
        <h2 className="text-xl font-bold text-sky-700 dark:text-sky-300 mb-5 text-center">
          👤 Tell Us About Yourself
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1 text-sm">
              Your Name
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., John"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1 text-sm">
              Age
            </label>
            <input
              type="number"
              className="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="e.g., 25"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1 text-sm">
              Gender
            </label>
            <select
              className="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
              required
            >
              <option value="">Select...</option>
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-700 dark:text-gray-300 font-medium mb-1 text-sm">
              Country
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              placeholder="e.g., India"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          className="mt-6 w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 text-white py-2 rounded-md text-sm font-semibold transition shadow-sm hover:shadow-md"
        >
          Continue to Assistant →
        </button>
      </form>
    </div>
  );
}
