import { useState } from "react";

export default function SymptomInputForm({ onSubmit }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSubmit(input.trim());
      setInput("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto mt-10">
      <label className="block mb-2 text-lg font-medium text-gray-700">
        Describe your symptoms:
      </label>
      <input
        type="text"
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g., I have chest pain and fever"
      />
      <button
        type="submit"
        className="mt-4 px-6 py-2 bg-purple-600 text-white font-semibold rounded-lg shadow hover:bg-purple-700 transition"
      >
        Submit
      </button>
    </form>
  );
}
