import { useState } from "react";

// const API_URL = import.meta.env.VITE_API_URL || "http://136.117.84.232:8000/infer";
const API_URL = "http://136.117.84.232:8000/infer";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input, max_tokens: 200 }),
      });

      const data = await res.json();
      const botMessage = {
        sender: "bot",
        text: data.response || "(No response)",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error contacting server." },
      ]);
    }

    setInput("");
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: "700px", margin: "0 auto", padding: "20px" }}>
      <h1>CounselGPT</h1>

      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: "8px",
          padding: "10px",
          height: "60vh",
          overflowY: "scroll",
          marginBottom: "20px",
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              margin: "10px 0",
              textAlign: m.sender === "user" ? "right" : "left",
            }}
          >
            <strong>{m.sender === "user" ? "You" : "CounselGPT"}:</strong>{" "}
            {m.text}
          </div>
        ))}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <input
          style={{ flex: 1, padding: "10px" }}
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage} disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default App;
