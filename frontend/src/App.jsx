import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

// Parse models from environment variable or use defaults
const parseModels = () => {
  try {
    const modelsEnv = import.meta.env.VITE_MODELS;
    if (modelsEnv) {
      return JSON.parse(modelsEnv);
    }
  } catch (error) {
    console.error("Error parsing VITE_MODELS:", error);
  }
  // Default models if parsing fails
  return [
    { id: "qwen2.5-7b-legal", name: "Qwen2.5-7B Legal (LoRA)" },
    { id: "qwen2.5-7b-base", name: "Qwen2.5-7B Base" },
  ];
};

const MODELS = parseModels();
const DEFAULT_MODEL = import.meta.env.VITE_DEFAULT_MODEL || MODELS[0].id;

function App() {
  const [conversations, setConversations] = useState([
    { id: 1, title: "New Chat", messages: [] }
  ]);
  const [currentConvId, setCurrentConvId] = useState(1);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [healthStatus, setHealthStatus] = useState({ status: 'checking', message: 'Checking server...' });
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const currentConv = conversations.find(c => c.id === currentConvId);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentConv?.messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [input]);

  // Health check
  const checkHealth = async () => {
    if (!API_URL) {
      setHealthStatus({ 
        status: 'error', 
        message: 'API URL not configured'
      });
      return;
    }

    try {
      const healthUrl = `${API_URL}/health`;
      const response = await fetch(healthUrl);
      
      if (response.ok) {
        const data = await response.json();
        setHealthStatus({ 
          status: 'healthy', 
          message: 'Connected',
          modelLoaded: data.model_loaded
        });
      } else {
        setHealthStatus({ 
          status: 'error', 
          message: `Server error: ${response.status}`
        });
      }
    } catch (error) {
      setHealthStatus({ 
        status: 'error', 
        message: 'Cannot reach server'
      });
    }
  };

  // Check health on mount and every 30 seconds
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = { 
      sender: "user", 
      text: input,
      timestamp: new Date().toISOString()
    };

    // Update conversation with user message
    const updatedConversations = conversations.map(conv => {
      if (conv.id === currentConvId) {
        const newMessages = [...conv.messages, userMessage];
        const newTitle = conv.messages.length === 0 ? input.slice(0, 30) + (input.length > 30 ? '...' : '') : conv.title;
        return { ...conv, messages: newMessages, title: newTitle };
      }
      return conv;
    });
    setConversations(updatedConversations);
    setInput("");
    setLoading(true);

    try {
      if (!API_URL) {
        throw new Error("API URL not configured. Please set VITE_API_URL in your .env file.");
      }

      // Map frontend model IDs to backend model names
      const modelMapping = {
        "qwen2.5-7b-legal": "qwen",
        "qwen2.5-7b-base": "qwen",
        "qwen": "qwen",
        "llama": "llama"
      };
      
      const backendModelName = modelMapping[selectedModel] || "qwen";

      const res = await fetch(`${API_URL}/infer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          prompt: input, 
          max_tokens: 400,  // Balanced: fast but detailed (300 words)
          model_name: backendModelName,
          use_gpu: true,
          use_cache: true
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      const botMessage = {
        sender: "bot",
        text: data.response || "(No response)",
        timestamp: new Date().toISOString(),
        cached: data.cached || false,
        responseLength: data.response_length || 0
      };

      setConversations(prev => prev.map(conv => {
        if (conv.id === currentConvId) {
          return { ...conv, messages: [...conv.messages, botMessage] };
        }
        return conv;
      }));
    } catch (err) {
      console.error("API Error:", err);
      
      // Provide more helpful error messages
      let errorMessage = "Unable to connect to the server.";
      
      if (err.message.includes("API URL not configured")) {
        errorMessage = "⚙️ API URL not configured. Please set VITE_API_URL in your .env file and restart the server.";
      } else if (err.message.includes("Failed to fetch") || err.name === "TypeError") {
        errorMessage = "🔌 Cannot reach the server. Please check:\n• Is the backend server running?\n• Is the API URL correct in your .env file?\n• Are you experiencing network issues?";
      } else if (err.message.includes("Unexpected end of JSON")) {
        errorMessage = "📡 Server sent an invalid response. The backend may be misconfigured or experiencing issues.";
      } else if (err.message.includes("Server returned")) {
        errorMessage = `❌ ${err.message}\n\nThe backend server is reachable but returned an error.`;
      } else {
        errorMessage = `⚠️ ${err.message}`;
      }

      setConversations(prev => prev.map(conv => {
        if (conv.id === currentConvId) {
          return { 
            ...conv, 
            messages: [...conv.messages, { 
              sender: "bot", 
              text: errorMessage,
              timestamp: new Date().toISOString(),
              error: true
            }] 
          };
        }
        return conv;
      }));
    }

    setLoading(false);
  }

  const newChat = () => {
    const newId = Math.max(...conversations.map(c => c.id)) + 1;
    setConversations([...conversations, { id: newId, title: "New Chat", messages: [] }]);
    setCurrentConvId(newId);
  };

  const deleteChat = (id) => {
    if (conversations.length === 1) return;
    const filtered = conversations.filter(c => c.id !== id);
    setConversations(filtered);
    if (currentConvId === id) {
      setCurrentConvId(filtered[0].id);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={newChat}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            New chat
          </button>
        </div>

        <div className="conversations-list">
          {conversations.map(conv => (
            <div 
              key={conv.id}
              className={`conversation-item ${conv.id === currentConvId ? 'active' : ''}`}
              onClick={() => setCurrentConvId(conv.id)}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <span className="conversation-title">{conv.title}</span>
              {conversations.length > 1 && (
                <button 
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteChat(conv.id);
                  }}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="sidebar-footer">
          <div className="health-status">
            <div className={`health-indicator ${healthStatus.status}`}>
              <div className="health-dot"></div>
              <div className="health-info">
                <div className="health-message">{healthStatus.message}</div>
              </div>
            </div>
            <button 
              className="refresh-health" 
              onClick={checkHealth}
              title="Check connection"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 4v6h-6M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </button>
          </div>
          
          <div className="model-selector">
            <label>Model</label>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
            >
              {MODELS.map(model => (
                <option key={model.id} value={model.id}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="main-content">
        <div className="header">
          <button 
            className="toggle-sidebar-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
          <div className="header-title">
            <svg className="logo-icon" width="28" height="28" viewBox="0 0 100 100">
              <defs>
                <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{stopColor:"#10a37f", stopOpacity:1}} />
                  <stop offset="100%" style={{stopColor:"#0d8c6c", stopOpacity:1}} />
                </linearGradient>
              </defs>
              <rect width="100" height="100" rx="20" fill="url(#logoGrad)"/>
              <path d="M30 35 L30 65 L45 65 L45 45 L55 45 L55 65 L70 65 L70 35 Z" fill="white" opacity="0.9"/>
              <circle cx="40" cy="40" r="3" fill="white"/>
              <circle cx="60" cy="40" r="3" fill="white"/>
            </svg>
            <h1>CounselGPT</h1>
          </div>
        </div>

        <div className="messages-container">
          {currentConv?.messages.length === 0 ? (
            <div className="empty-state">
              <div className="logo-container">
                <svg width="80" height="80" viewBox="0 0 100 100">
                  <defs>
                    <linearGradient id="emptyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" style={{stopColor:"#10a37f", stopOpacity:1}} />
                      <stop offset="100%" style={{stopColor:"#0d8c6c", stopOpacity:1}} />
                    </linearGradient>
                  </defs>
                  <rect width="100" height="100" rx="20" fill="url(#emptyGrad)"/>
                  <path d="M30 35 L30 65 L45 65 L45 45 L55 45 L55 65 L70 65 L70 35 Z" fill="white" opacity="0.9"/>
                  <circle cx="40" cy="40" r="3" fill="white"/>
                  <circle cx="60" cy="40" r="3" fill="white"/>
                </svg>
              </div>
              <h2>How can I help you today?</h2>
              <div className="model-info-tags">
                <span className="model-tag">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="9" y1="9" x2="15" y2="9"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                  </svg>
                  {MODELS.find(m => m.id === selectedModel)?.name}
                </span>
                <span className="model-tag">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  ctx: 8,192
                </span>
              </div>
            </div>
          ) : (
            <>
              {currentConv?.messages.map((msg, i) => (
                <div key={i} className={`message ${msg.sender}`}>
                  <div className="message-avatar">
                    {msg.sender === 'user' ? (
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                      </svg>
                    ) : (
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <line x1="9" y1="9" x2="15" y2="9"/>
                        <line x1="9" y1="15" x2="15" y2="15"/>
                      </svg>
                    )}
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      {msg.sender === 'bot' ? (
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      ) : (
                        msg.text
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message bot">
                  <div className="message-avatar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                      <line x1="9" y1="9" x2="15" y2="9"/>
                      <line x1="9" y1="15" x2="15" y2="15"/>
                    </svg>
                  </div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <button className="attach-btn" title="Attach file" disabled>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
              </svg>
            </button>
            <textarea
              ref={textareaRef}
              className="message-input"
              placeholder="Ask anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={loading}
            />
            <button 
              className="mic-btn" 
              title="Voice input"
              disabled
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </button>
            <button 
              className="send-btn" 
              onClick={sendMessage} 
              disabled={loading || !input.trim()}
            >
              {loading ? (
                <svg className="spinner" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              )}
        </button>
          </div>
          <div className="input-footer">
            <span>Press <kbd>Enter</kbd> to send, <kbd>Shift</kbd> + <kbd>Enter</kbd> for new line</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
