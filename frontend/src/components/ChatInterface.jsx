import React, { useState, useRef, useEffect } from 'react'
import { api } from '../services/api'
import './ChatInterface.css'

function ChatInterface() {
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            content: "Hello! I'm your Publix Expansion Assistant. I can help you explore store locations, parcels, demographics, and expansion predictions. What would you like to know?",
        },
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || loading) return

        const userMessage = input.trim()
        setInput('')
        setLoading(true)
        setError(null)

        // Add user message
        const newMessages = [...messages, { role: 'user', content: userMessage }]
        setMessages(newMessages)

        try {
            // Prepare conversation history (last 10 messages)
            const conversationHistory = newMessages
                .slice(-10)
                .map((msg) => ({
                    role: msg.role,
                    content: msg.content,
                }))

            const response = await api.chat(userMessage, conversationHistory)

            // Add assistant response
            setMessages([
                ...newMessages,
                {
                    role: 'assistant',
                    content: response.data?.response || response.data?.message || 'No response received',
                    data: response.data?.data,
                    queryType: response.data?.query_type,
                },
            ])
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to get response')
            setMessages([
                ...newMessages,
                {
                    role: 'assistant',
                    content: 'Sorry, I encountered an error. Please try again.',
                    error: true,
                },
            ])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const exampleQuestions = [
        "How many Publix stores are in Florida?",
        "Show me parcels available in Georgia",
        "What are the demographics for cities in Kentucky?",
        "What are the top expansion predictions?",
    ]

    return (
        <div className="chat-interface">
            <div className="chat-header">
                <h2>Publix Expansion Assistant</h2>
                <p>Ask me about stores, parcels, demographics, or expansion opportunities</p>
            </div>

            <div className="chat-messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                        <div className="message-content">
                            <div className="message-text">{msg.content}</div>
                            {msg.data && msg.data.length > 0 && (
                                <div className="message-data">
                                    <strong>Data found:</strong>
                                    <ul>
                                        {msg.data.slice(0, 5).map((item, i) => (
                                            <li key={i}>
                                                {item.address || item.city || JSON.stringify(item)}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="message assistant">
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
            </div>

            {error && <div className="chat-error">{error}</div>}

            <div className="example-questions">
                <p>Try asking:</p>
                <div className="example-buttons">
                    {exampleQuestions.map((q, idx) => (
                        <button
                            key={idx}
                            className="example-btn"
                            onClick={() => {
                                setInput(q)
                                setTimeout(() => handleSend(), 100)
                            }}
                            disabled={loading}
                        >
                            {q}
                        </button>
                    ))}
                </div>
            </div>

            <div className="chat-input-container">
                <textarea
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about Publix expansion..."
                    rows={2}
                    disabled={loading}
                />
                <button
                    className="send-button"
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                >
                    {loading ? 'Sending...' : 'Send'}
                </button>
            </div>
        </div>
    )
}

export default ChatInterface

