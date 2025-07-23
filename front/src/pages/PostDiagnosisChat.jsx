import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { v4 as uuidv4 } from "uuid";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import ProgressTracker from "../components/ProgressTracker";
import remarkGfm from "remark-gfm";

// ✅ Button component
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
    <div className="min-h-screen bg-blue-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 text-gray-900 dark:text-gray-100">
      <div className="max-w-3xl mx-auto">
        <ProgressTracker step={4} />

        <h2 className="text-2xl font-bold mb-6 text-center text-indigo-700 dark:text-indigo-300">
          🧠 Ask Anything Else About Your Diagnosis
        </h2>

        {/* Chat Messages */}
        <div
          ref={chatBoxRef}
          className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 h-[400px] overflow-y-auto mb-4 shadow-inner space-y-4"
        >
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`mb-2 flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-xl max-w-[75%] whitespace-pre-wrap break-words text-sm shadow ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white"
                }`}
              >
                {msg.role === "assistant" ? (
                  <details
                    open
                    className="bg-gray-100 dark:bg-gray-600 rounded-lg p-3 transition-all"
                  >
                    <summary className="font-semibold cursor-pointer mb-2 text-indigo-700 dark:text-indigo-200">
                      Assistant Response
                    </summary>
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeRaw]}
                      components={{
                        p: ({ children }) => <p className="mb-2">{children}</p>,
                        strong: ({ children }) => (
                          <strong className="font-semibold">{children}</strong>
                        ),
                        ul: ({ children }) => (
                          <ul className="list-disc list-inside mb-2">
                            {children}
                          </ul>
                        ),
                        ol: ({ children }) => (
                          <ol className="list-decimal list-inside mb-2">
                            {children}
                          </ol>
                        ),
                        li: ({ children }) => (
                          <li className="ml-4">{children}</li>
                        ),
                        h1: ({ children }) => (
                          <h1 className="text-xl font-bold mt-4 mb-2">
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2 className="text-lg font-semibold mt-3 mb-2">
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3 className="text-base font-semibold mt-2 mb-1">
                            {children}
                          </h3>
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </details>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Input + Send */}
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

        {/* New Session */}
        <div className="mt-6 text-center">
          <Button variant="secondary" onClick={handleNewSession}>
            🔄 Start New Session
          </Button>
        </div>
      </div>
    </div>
  );
}
