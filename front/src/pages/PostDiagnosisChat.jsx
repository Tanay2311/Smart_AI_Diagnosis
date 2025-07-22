import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import ProgressTracker from "../components/ProgressTracker";

// ✅ Button component with dark/light mode styling
function Button({ children, onClick, variant = "primary" }) {
  const baseStyle = "px-4 py-2 rounded font-semibold transition-colors";
  const primaryStyle =
    "bg-indigo-600 text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600";
  const secondaryStyle =
    "bg-gray-300 text-black hover:bg-gray-400 dark:bg-gray-700 dark:text-white";

  const finalStyle =
    variant === "secondary"
      ? `${baseStyle} ${secondaryStyle}`
      : `${baseStyle} ${primaryStyle}`;

  return (
    <button onClick={onClick} className={finalStyle}>
      {children}
    </button>
  );
}

// ✅ Beautify LLM response to bullet points
function beautifyResponse(text) {
  const lines = text
    .split(/(?<=[.?!])\s+|\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  return lines.map((line) => `• ${line}`).join("\n\n");
}

export default function PostDiagnosisChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState("");
  const chatBoxRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat_llm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          messages: updatedMessages,
        }),
      });

      const data = await res.json();
      const assistantMessage = { role: "assistant", content: data.reply };
      setMessages([...updatedMessages, assistantMessage]);
    } catch (error) {
      console.error("❌ LLM chat error:", error);
    }
  };

  const handleNewSession = () => {
    navigate("/");
  };

  return (
    <div className="p-4 max-w-3xl mx-auto text-gray-900 dark:text-gray-100">
      <ProgressTracker step={4} />

      <h2 className="text-2xl font-bold mb-6 text-center text-indigo-700 dark:text-indigo-300">
        🧠 Ask Anything Else About Your Diagnosis
      </h2>

      {/* Chat messages */}
      <div
        ref={chatBoxRef}
        className="bg-gray-100 dark:bg-gray-900 rounded-lg p-4 h-[400px] overflow-y-auto mb-4 shadow-inner"
      >
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-3 flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`px-4 py-2 rounded-xl max-w-[75%] whitespace-pre-line break-words text-sm shadow ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white"
              }`}
            >
              {msg.role === "assistant"
                ? beautifyResponse(msg.content)
                : msg.content}
            </div>
          </div>
        ))}
      </div>

      {/* Input field + Send */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          className="flex-grow px-4 py-2 rounded border bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          placeholder="Ask anything related to your diagnosis..."
        />
        <Button onClick={handleSend}>Send</Button>
      </div>

      {/* New session button */}
      <div className="mt-6 text-center">
        <Button variant="secondary" onClick={handleNewSession}>
          🔄 Start New Session
        </Button>
      </div>
    </div>
  );
}
