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
  const [editingMessageId, setEditingMessageId] = useState(null);
  const [editText, setEditText] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Try to restore session from localStorage
    try {
      const savedSessionId = typeof localStorage !== 'undefined' ? localStorage.getItem('chatSessionId') : null;
      const savedMessages = typeof localStorage !== 'undefined' ? localStorage.getItem('chatMessages') : null;
      
      if (savedSessionId && savedMessages) {
        setSessionId(savedSessionId);
        try {
          const parsedMessages = JSON.parse(savedMessages);
          setMessages(parsedMessages);
        } catch (error) {
          console.error('Error parsing saved messages:', error);
          // Fallback to initial message if parsing fails
          initializeNewSession();
        }
      } else {
        initializeNewSession();
      }
    } catch (error) {
      console.error('Error accessing localStorage:', error);
      initializeNewSession();
    }
  }, []);

  const initializeNewSession = () => {
    try {
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('chatSessionId', newSessionId);
      }
      
      const initialMessages = [
        {
          id: `assistant_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          role: "assistant",
          message:
            "👋 Hi! I'm your RFP Assistant. I can help you scan tenders from tendersontime.com, analyze products, and generate pricing.\n\nTry: \"Scan for cable RFPs\" or \"Complete workflow for electrical tenders\"",
          timestamp: new Date().toISOString(),
        },
      ];
      setMessages(initialMessages);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('chatMessages', JSON.stringify(initialMessages));
      }
    } catch (error) {
      console.error('Error initializing new session:', error);
      // Set messages even if localStorage fails
      setMessages([{
        id: `assistant_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        message: "👋 Hi! I'm your RFP Assistant. How can I help you today?",
        timestamp: new Date().toISOString(),
      }]);
    }
  };

  // Save messages to localStorage whenever they change
  useEffect(() => {
    try {
      if (messages.length > 1) { // Don't save just the initial message
        localStorage.setItem('chatMessages', JSON.stringify(messages));
      }
    } catch (error) {
      console.warn('localStorage save error:', error);
    }
  }, [messages]);

  useEffect(() => {
    // Add a small delay to ensure DOM is ready
    const timeoutId = setTimeout(() => {
      try {
        if (messagesEndRef.current && messagesEndRef.current.scrollIntoView) {
          messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
      } catch (error) {
        console.warn('ScrollIntoView error:', error);
      }
    }, 100);
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      role: "user",
      message: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      const assistantMessage = {
        id: `assistant_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        message: data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        message: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
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

  const startEditMessage = (messageId, currentText) => {
    setEditingMessageId(messageId);
    setEditText(currentText);
    setInput(currentText);
  };

  const cancelEdit = () => {
    setEditingMessageId(null);
    setEditText("");
    setInput("");
  };

  const updateMessage = async () => {
    if (!editText.trim() || !editingMessageId) return;

    // Find the message to update
    const messageIndex = messages.findIndex(msg => msg.id === editingMessageId);
    if (messageIndex === -1) return;

    // Remove the original message and all messages after it (including AI response)
    const newMessages = messages.slice(0, messageIndex);
    setMessages(newMessages);

    // Send the updated message
    const userMessage = {
      id: editingMessageId,
      role: "user",
      message: editText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setEditingMessageId(null);
    setEditText("");
    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: editText,
          sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        message: data.response,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        role: "assistant",
        message: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('chatMessages');
        localStorage.removeItem('chatSessionId');
      }
      initializeNewSession();
    } catch (error) {
      console.warn('Clear chat error:', error);
      initializeNewSession();
    }
  };

  const startNewChat = () => {
    try {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('chatMessages');
        localStorage.removeItem('chatSessionId');
      }
      setMessages([]);
      setSessionId(null);
      setEditingMessageId(null);
      setEditText("");
      setInput("");
      setLoading(false);
      
      // Initialize with fresh welcome message
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('chatSessionId', newSessionId);
      }
      
      const initialMessages = [
        {
          id: `assistant_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          role: "assistant",
          message: "👋 Hi! I'm your RFP Assistant. I can help you scan tenders from tendersontime.com, analyze products, and generate pricing.\n\nTry: \"Scan for cable RFPs\" or \"Complete workflow for electrical tenders\"",
          timestamp: new Date().toISOString(),
        },
      ];
      setMessages(initialMessages);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('chatMessages', JSON.stringify(initialMessages));
      }
    } catch (error) {
      console.warn('New chat error:', error);
      // Fallback to basic initialization
      setMessages([{
        id: `assistant_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        role: "assistant",
        message: "👋 Hi! I'm your RFP Assistant. How can I help you today?",
        timestamp: new Date().toISOString(),
      }]);
    }
  };

  const quickActions = [
    { label: "Scan RFPs", message: "Scan for cable and wire RFPs" },
    { label: "Full Workflow", message: "Complete workflow for electrical tenders" },
    { label: "Show Status", message: "Show me the current status" },
    { label: "Pricing", message: "Calculate pricing for selected RFP" },
  ];

  return (
    <div className={styles.chatInterface}>
      <div className={styles.chatMessages}>
        {messages.map((msg, idx) => (
          <div key={idx} className={`${styles.message} ${msg.role}`}>
            <div className={styles.messageAvatar}>
              {msg.role === "user" ? "◆" : "◈"}
            </div>
            <div className={styles.messageContent}>
              {msg.role === "assistant" ? (
                <div className={styles.messageText}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.message || ""}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className={styles.messageText}>
                  {(msg.message || "").split("\n").map((line, i) => (
                    <React.Fragment key={i}>
                      {line}
                      {i < (msg.message || "").split("\n").length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
              )}
              <div className={styles.messageActions}>
                {msg.role === "user" && !loading && (
                  <button
                    className={styles.editButton}
                    onClick={() => startEditMessage(msg.id, msg.message)}
                    title="Edit message"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                  </button>
                )}
              </div>
              <div className={styles.messageTime}>
                {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ""}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <div className={styles.messageAvatar}>◈</div>
            <div className={styles.messageContent}>
              <div className={styles.typingIndicator}></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} style={{ height: '1px' }} />
      </div>

      <div className={styles.quickActionsBar}>
        <div className={styles.suggestedPrompts}>
          <span className={styles.suggestedLabel}>Try:</span>
          {quickActions.map((action, idx) => (
            <button
              key={idx}
              className={styles.suggestedPrompt}
              onClick={() => {
                setInput(action.message);
                setTimeout(() => sendMessage(), 100);
              }}
              type="button"
            >
              {action.label}
            </button>
          ))}
          <button
            className={styles.newChatBtn}
            onClick={startNewChat}
            title="Start new chat"
            type="button"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            New Chat
          </button>
        </div>
      </div>

      <div className={styles.modernInputContainer}>
        {editingMessageId && (
          <div className={styles.editModeBar}>
            <span className={styles.editModeLabel}>Editing message</span>
            <div className={styles.editModeActions}>
              <button
                className={styles.cancelEditBtn}
                onClick={cancelEdit}
                type="button"
              >
                Cancel
              </button>
              <button
                className={styles.updateEditBtn}
                onClick={updateMessage}
                disabled={!editText.trim()}
                type="button"
              >
                Update
              </button>
            </div>
          </div>
        )}
        <div className={styles.inputWrapper}>
          <div className={styles.inputArea}>
            <textarea
              className={styles.modernChatInput}
              placeholder={editingMessageId ? "Edit your message..." : "Ask me anything about RFP automation..."}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                if (editingMessageId) {
                  setEditText(e.target.value);
                }
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (editingMessageId) {
                    updateMessage();
                  } else {
                    sendMessage();
                  }
                }
              }}
              rows={1}
              style={{
                height: 'auto',
                minHeight: '24px',
                maxHeight: '120px',
                resize: 'none'
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = Math.min(target.scrollHeight, 120) + 'px';
              }}
            />
            <div className={styles.inputActions}>
              <button className={styles.attachBtn} type="button" title="Attach file">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                </svg>
              </button>
              <button 
                className={styles.modernSendBtn} 
                onClick={editingMessageId ? updateMessage : sendMessage} 
                disabled={loading || !input.trim()} 
                type="button"
              >
                {loading ? (
                  <div className={styles.loadingSpinner}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                    </svg>
                  </div>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                  </svg>
                )}
              </button>
            </div>
          </div>
          <div className={styles.inputFooter}>
            <span className={styles.inputHint}>
              Press <kbd>Enter</kbd> to {editingMessageId ? "update" : "send"}, <kbd>Shift+Enter</kbd> for new line
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
