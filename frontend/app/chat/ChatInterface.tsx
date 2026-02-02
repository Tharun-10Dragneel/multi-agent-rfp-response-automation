"use client";

import React, { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import styles from "./ChatInterface.module.css";

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    setSessionId(`session_${Date.now()}`);
    setMessages([
      {
        role: "assistant",
        message:
          `� RFP-ASSISTANT v2.1.0 [INITIALIZED]
🔹 System Status: ONLINE
🔹 Capabilities: Tender scanning, Product analysis, Pricing calculation

┌─ Available Commands ───────────────────────┐
│ scan for cable RFPs                        │
│ complete workflow for electrical tenders    │
│ show current status                         │
│ calculate pricing for selected RFP          │
└─────────────────────────────────────────────┘

Ready for input >`,
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      role: "user",
      message: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input;
    setInput("");
    setLoading(true);

    try {
      if (!sessionId) {
        throw new Error("Session not ready");
      }
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userInput,
          session_id: sessionId,
        }),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const errorMessage = data?.detail || data?.message || "Request failed.";
        throw new Error(errorMessage);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          message: data.response || "No response received from the backend.",
          timestamp: data.timestamp,
          workflow_state: data.workflow_state,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          message: "❌ Error: Failed to process message. Please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    { label: "[SCAN] RFPs", message: "scan for cable and wire RFPs" },
    { label: "[WORKFLOW] Full", message: "complete workflow for electrical tenders" },
    { label: "[STATUS] System", message: "show current status" },
    { label: "[PRICE] Calc", message: "calculate pricing for selected RFP" },
  ];

  return (
    <div className={styles.chatInterface}>
      <header className={styles.chatHeader}>
        <div className={styles.terminalHeader}>
          <div className={styles.terminalTitle}>
            <span className={styles.terminalGreen}>root@rfp-system:~$</span>
            <span className={styles.terminalBlue}> ./rfp-assistant --mode=interactive</span>
          </div>
          <div className={styles.terminalStatus}>
            <span className={styles.terminalGreen}>●</span>
            <span>ONLINE</span>
          </div>
        </div>
        <div className={styles.sessionInfo}>
          {sessionId && (
            <span className={styles.sessionBadge}>SESSION: {sessionId.slice(-8).toUpperCase()}</span>
          )}
        </div>
      </header>

      <div className={styles.chatMessages}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`${styles.message} ${msg.role === "user" ? styles.user : styles.assistant}`}>
            <div className={styles.terminalLine}>
              {msg.role === "user" ? (
                <>
                  <span className={styles.terminalPrompt}>
                    <span className={styles.terminalGreen}>user@rfp-system:~$</span>
                    <span className={styles.terminalWhite}> {msg.message}</span>
                  </span>
                </>
              ) : (
                <div className={styles.terminalOutput}>
                  <pre className={styles.terminalText}>{msg.message}</pre>
                </div>
              )}
            </div>
            <div className={styles.messageTime}>
              [{msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ""}]
            </div>
          </div>
        ))}

        {loading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={styles.terminalOutput}>
              <div className={styles.terminalTyping}>
                <span className={styles.terminalGreen}>$</span>
                <span className={styles.terminalCaret}>Processing</span>
                <span className={styles.typingIndicator}>
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.quickActionsBar}>
        <div className={styles.terminalCommands}>
          <span className={styles.terminalGray}># Quick Commands:</span>
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              className={styles.terminalCommandBtn}
              onClick={() => {
                setInput(action.message);
                setTimeout(() => sendMessage(), 100);
              }}
              type="button"
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.chatInputContainer}>
        <div className={styles.terminalInputLine}>
          <span className={styles.terminalPromptSymbol}>user@rfp-system:~$</span>
          <textarea
            className={styles.terminalInput}
            placeholder="Enter command..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            rows={1}
          />
          <button className={styles.terminalSendBtn} onClick={sendMessage} disabled={loading || !input.trim()} type="button">
            {loading ? "⏳" : "▶"}
          </button>
        </div>
      </div>
    </div>
  );
}
