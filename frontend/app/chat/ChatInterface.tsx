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
          "Hello! I'm your RFP Assistant. I can help you scan tenders, analyze products, and generate pricing. How can I assist you today?",
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
    { label: "Scan RFPs", message: "Scan for cable and wire RFPs", icon: "🔍" },
    { label: "Full Workflow", message: "Complete workflow for electrical tenders", icon: "⚡" },
    { label: "Show Status", message: "Show me the current status", icon: "📊" },
    { label: "Get Pricing", message: "Calculate pricing for selected RFP", icon: "💰" },
  ];

  return (
    <div className={styles.chatInterface}>
      <header className={styles.chatHeader}>
        <div className={styles.headerContent}>
          <div className={styles.headerInfo}>
            <h1>RFP Assistant</h1>
            <p>AI-powered automation for your tender needs</p>
          </div>
          <div className={styles.sessionInfo}>
            {sessionId && (
              <span className={styles.sessionBadge}>Session {sessionId.slice(-6).toUpperCase()}</span>
            )}
          </div>
        </div>
      </header>

      <div className={styles.chatMessages}>
        <div className={styles.welcomeMessage}>
          <div className={styles.assistantBubble}>
            <div className={styles.bubbleContent}>
              <p>Hello! I'm your RFP Assistant. I can help you scan tenders, analyze products, and generate pricing. How can I assist you today?</p>
            </div>
            <div className={styles.bubbleTime}>Just now</div>
          </div>
        </div>

        {messages.slice(1).map((msg, idx) => (
          <div key={idx} className={`${styles.messageWrapper} ${msg.role === "user" ? styles.userWrapper : styles.assistantWrapper}`}>
            <div className={`${styles.messageBubble} ${msg.role === "user" ? styles.userBubble : styles.assistantBubble}`}>
              <div className={styles.bubbleContent}>
                {msg.role === "assistant" ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.message || ""}
                  </ReactMarkdown>
                ) : (
                  <p>{msg.message}</p>
                )}
              </div>
              <div className={styles.bubbleTime}>
                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ""}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className={styles.messageWrapper}>
            <div className={`${styles.messageBubble} ${styles.assistantBubble}`}>
              <div className={styles.typingIndicator}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.quickActions}>
        <div className={styles.quickActionsHeader}>
          <span>Quick Actions</span>
        </div>
        <div className={styles.quickActionsGrid}>
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              className={styles.quickActionCard}
              onClick={() => {
                setInput(action.message);
                setTimeout(() => sendMessage(), 100);
              }}
              type="button"
            >
              <span className={styles.actionIcon}>{action.icon}</span>
              <span className={styles.actionLabel}>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className={styles.chatInputContainer}>
        <div className={styles.inputWrapper}>
          <textarea
            className={styles.chatInput}
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            rows={1}
          />
          <button 
            className={styles.sendButton} 
            onClick={sendMessage} 
            disabled={loading || !input.trim()} 
            type="button"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 2L11 13M22 2l-7 20-4-9-9 4 20 7z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
