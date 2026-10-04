import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertTriangle, Lightbulb, ChevronRight, FileText } from 'lucide-react';
import styles from './Copilot.module.css';
import { copilotService } from '../services/copilot';
import type { CopilotResponse } from '../types/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: CopilotResponse;
  isError?: boolean;
}

const Copilot = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (!query.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: query.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await copilotService.query({ query: userMessage.content });
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        response
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: error.message || 'Failed to connect to AI Copilot service.',
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    // Let the user edit or just submit immediately
    // For immediate submit:
    // setTimeout(() => handleSubmit(), 10);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}><Bot size={28} /> EKATVA Copilot</h1>
        <p className={styles.subtitle}>Ask questions about your material data, check inventory, or analyze national material coverage.</p>
      </div>

      <div className={styles.chatWindow}>
        <div className={styles.messageArea}>
          {messages.length === 0 ? (
            <div className={styles.emptyState}>
              <Bot size={64} className={styles.emptyIcon} />
              <h2>How can I help you today?</h2>
              <p>I can analyze material data, check vendor supplies, or summarize catalog metrics.</p>
              
              <div className={styles.suggestions}>
                <button 
                  className={styles.suggestionBtn}
                  onClick={() => handleSuggestionClick("Show me the materials mapping summary for IOCL")}
                >
                  "Show me the materials mapping summary for IOCL"
                </button>
                <button 
                  className={styles.suggestionBtn}
                  onClick={() => handleSuggestionClick("What is the current inventory for Pipe 10 Inch Schedule 40?")}
                >
                  "What is the current inventory for Pipe 10 Inch Schedule 40?"
                </button>
                <button 
                  className={styles.suggestionBtn}
                  onClick={() => handleSuggestionClick("Identify unreviewed material conflicts")}
                >
                  "Identify unreviewed material conflicts"
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`${styles.message} ${styles[msg.role]}`}>
                <div className={`${styles.avatar} ${styles[msg.role]}`}>
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                
                <div className={styles.messageContentWrapper}>
                  <div className={styles.messageContent}>
                    {msg.isError ? (
                      <div className={styles.messageText} style={{ color: 'var(--color-danger)' }}>
                        <AlertTriangle size={16} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'text-bottom' }}/>
                        {msg.content}
                      </div>
                    ) : (
                      <div className={styles.messageText}>{msg.content}</div>
                    )}
                  </div>
                  
                  {msg.response && (
                    <>
                      {msg.response.key_findings && msg.response.key_findings.length > 0 && (
                        <div className={styles.findingsBox}>
                          <div className={styles.findingsTitle}>
                            <Lightbulb size={16} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} /> 
                            Key Findings
                          </div>
                          {msg.response.key_findings.map((finding, idx) => (
                            <div key={idx} className={styles.findingItem}>
                              <ChevronRight size={14} style={{ marginTop: '2px', flexShrink: 0 }} />
                              <span>{finding}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {msg.response.data_limitation && (
                        <div className={styles.limitationBox}>
                          <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                          <span>{msg.response.data_limitation}</span>
                        </div>
                      )}
                      
                      {msg.response.sources && msg.response.sources.length > 0 && (
                        <div className={styles.sourcesBox}>
                          <div className={styles.sourcesTitle}>Data Sources Used</div>
                          <div className={styles.sourceList}>
                            {msg.response.sources.map((source, idx) => (
                              <div key={idx} className={styles.sourceItem}>
                                <FileText size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }} />
                                {source}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className={`${styles.message} ${styles.assistant}`}>
              <div className={`${styles.avatar} ${styles.assistant}`}>
                <Bot size={20} />
              </div>
              <div className={styles.messageContent}>
                <div className={styles.loadingBubble}>
                  <div className={styles.loadingDot}></div>
                  <div className={styles.loadingDot}></div>
                  <div className={styles.loadingDot}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputArea}>
          <form className={styles.inputForm} onSubmit={handleSubmit}>
            <textarea
              className={styles.inputField}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Copilot a question..."
              rows={1}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className={styles.sendBtn}
              disabled={!query.trim() || isLoading}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Copilot;
