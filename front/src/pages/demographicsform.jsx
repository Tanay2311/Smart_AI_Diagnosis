import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function DemographicsForm() {
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [country, setCountry] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Store locally or in context (later)
    localStorage.setItem("user_demographics", JSON.stringify({ age, gender, country }));
    navigate("/assistant");
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-purple-50 p-8 rounded-xl shadow-xl max-w-md w-full"
      >
        <h2 className="text-2xl font-bold text-purple-700 mb-6 text-center">
          👤 Your Information
        </h2>

        <label className="block text-gray-700 mb-2">Age</label>
        <input
          type="number"
          className="w-full mb-4 px-4 py-2 rounded border border-gray-300"
          value={age}
          onChange={(e) => setAge(e.target.value)}
          required
        />

        <label className="block text-gray-700 mb-2">Gender</label>
        <select
          className="w-full mb-6 px-4 py-2 rounded border border-gray-300"
          value={gender}
          onChange={(e) => setGender(e.target.value)}
          required
        >
          <option value="">Select...</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
          <option value="other">Other</option>
        </select>

        <label className="block text-gray-700 mb-2">Country you live in?</label>
        <input
          type="text"
          className="w-full mb-4 px-4 py-2 rounded border border-gray-300"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          required
        />


        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 transition"
        >
          Continue to Assistant →
        </button>
      </form>
    </div>
  );
}
