import React, { useState, useRef, useEffect } from 'react';
import './ChatPage.css';

const API_BASE_URL = 'http://localhost:8000';

function ChatPage() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // 메시지 목록을 자동으로 스크롤
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // 초기 환영 메시지
    useEffect(() => {
        setMessages([
            {
                role: 'ai',
                content: '안녕하세요! 명지전문대학 학사챗봇입니다. 무엇을 도와드릴까요?',
                timestamp: new Date()
            }
        ]);
    }, []);

    const sendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            role: 'user',
            content: inputMessage.trim(),
            timestamp: new Date()
        };

        // 사용자 메시지 추가
        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            // 채팅 히스토리 준비 (API용)
            const chatHistory = messages.map(msg => ({
                role: msg.role === 'user' ? 'user' : 'assistant',
                content: msg.content
            }));

            const response = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: inputMessage.trim(),
                    chat_history: chatHistory
                })
            });

            const data = await response.json();

            if (data.success) {
                const aiMessage = {
                    role: 'ai',
                    content: data.response,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, aiMessage]);
            } else {
                const errorMessage = {
                    role: 'ai',
                    content: `오류: ${data.response}`,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, errorMessage]);
            }
        } catch (error) {
            console.error('채팅 오류:', error);
            const errorMessage = {
                role: 'ai',
                content: '죄송합니다. 서버와 연결할 수 없습니다. 잠시 후 다시 시도해주세요.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const clearChat = () => {
        setMessages([
            {
                role: 'ai',
                content: '채팅이 초기화되었습니다. 새로운 대화를 시작해보세요!',
                timestamp: new Date()
            }
        ]);
    };

    return (
        <div className="chat-container">
            {/* 헤더 */}
            <div className="chat-header">
                <h1>MJC AI Chat</h1>
                <button className="clear-btn" onClick={clearChat}>
                    🗑️ 초기화
                </button>
            </div>

            {/* 메시지 영역 */}
            <div className="messages-container">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`message ${message.role === 'user' ? 'user-message' : 'ai-message'}`}
                    >
                        <div className="message-content">
                            <div className="message-text">{message.content}</div>
                            <div className="message-time">
                                {message.timestamp.toLocaleTimeString()}
                            </div>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message ai-message">
                        <div className="message-content">
                            <div className="typing-indicator">
                                <div className="typing-dot"></div>
                                <div className="typing-dot"></div>
                                <div className="typing-dot"></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* 입력 영역 */}
            <div className="input-container">
                <div className="input-wrapper">
                    <textarea
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
                        className="message-input"
                        rows="2"
                        disabled={isLoading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!inputMessage.trim() || isLoading}
                        className="send-btn"
                    >
                        📤
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ChatPage; 