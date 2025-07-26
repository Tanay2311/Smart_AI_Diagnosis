import { useState } from "react";

export default function SymptomInputForm({ onSubmit }) {
  const [input, setInput] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) {
      alert("Please enter your symptoms.");
      return;
    }
    onSubmit(input);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="w-full max-w-md mx-auto mt-10 px-4"
    >
      <label className="block mb-2 text-lg font-semibold text-blue-900 dark:text-blue-200">
        Describe your symptoms specifically:
      </label>
      <input
        type="text"
        className="w-full px-4 py-2 border border-blue-300 dark:border-blue-600 rounded-lg bg-white dark:bg-gray-800 text-gray-800 dark:text-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-400 dark:focus:ring-blue-300"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g., I have chest pain and fever"
      />
      <button
        type="submit"
        className="mt-4 px-6 py-2 bg-blue-500 dark:bg-blue-600 text-white font-semibold rounded-lg shadow hover:bg-blue-600 dark:hover:bg-blue-700 transition"
      >
        Submit
      </button>
    </form>
  );
}
