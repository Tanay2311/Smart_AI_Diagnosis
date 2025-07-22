// components/ProgressTracker.jsx
export default function ProgressTracker({ step }) {
  const steps = [
  "What's Wrong?",     // input
  "We Spotted This",   // extracted
  "More Info Please",  // followup
  "Your Diagnosis",    // diagnosis
  "Need More Help?",   // post-diagnosis
];



  return (
    <div className="flex justify-between items-center text-sm sm:text-base font-medium text-gray-500 mb-6 px-4 sm:px-10">
      {steps.map((label, idx) => {
        const isActive = idx === step;
        const isCompleted = idx < step;

        return (
          <div key={label} className="flex-1 text-center">
            <div
              className={`rounded-full w-8 h-8 mx-auto mb-1 flex items-center justify-center 
                ${isActive ? "bg-purple-600 text-white" : isCompleted ? "bg-green-400 text-white" : "bg-gray-300 text-gray-700"}`}
            >
              {idx + 1}
            </div>
            <div className={isActive ? "text-purple-700" : ""}>{label}</div>
          </div>
        );
      })}
    </div>
  );
}
