import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, AlertCircle, Lightbulb } from 'lucide-react';
import { ragAPI, type QueryRequest, type QueryResponse, type QuerySuggestion } from '../lib/api';
import { cn } from '../lib/utils';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  confidence?: number;
  sources?: Array<{
    title: string;
    content: string;
    relevance: number;
  }>;
  category?: string;
  suggestions?: string[];
}

interface ChatProps {
  className?: string;
}

export default function Chat({ className }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<QuerySuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Cargar sugerencias al montar el componente
    loadSuggestions();
  }, []);

  const loadSuggestions = async () => {
    try {
      const response = await ragAPI.getSuggestions();
      setSuggestions(response.suggestions.slice(0, 6)); // Mostrar solo 6 sugerencias
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const handleSendMessage = async (messageText?: string) => {
    const text = messageText || inputValue.trim();
    if (!text || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setShowSuggestions(false);

    try {
      const queryRequest: QueryRequest = {
        question: text,
        use_uploaded_docs: true, // Siempre intentar usar documentos si están disponibles
      };

      const response: QueryResponse = await ragAPI.query(queryRequest);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.answer,
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources,
        category: response.category,
        suggestions: response.suggestions,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error: unknown) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: `Lo siento, ocurrió un error al procesar tu consulta: ${
          error instanceof Error 
            ? error.message 
            : 'Error desconocido'
        }`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion: QuerySuggestion) => {
    handleSendMessage(suggestion.question);
  };

  const formatContent = (content: string) => {
    // Convertir markdown básico a HTML
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <div className={cn('flex flex-col h-full bg-white dark:bg-slate-900', className)}>
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-blue-600" />
          <h2 className="text-lg font-semibold">LegalGPT</h2>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            Asistente Legal para PyMEs
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && showSuggestions && (
          <div className="space-y-6">
            <div className="text-center">
              <Bot className="w-16 h-16 text-blue-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">
                ¡Hola! Soy tu asistente legal
              </h3>
              <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                Especializado en asesoría legal para PyMEs colombianas. 
                Pregúntame sobre constitución de empresas, derecho laboral, 
                obligaciones tributarias y más.
              </p>
            </div>

            {suggestions.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium">Consultas sugeridas:</span>
                </div>
                <div className="grid gap-2">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="text-left p-3 rounded-lg border hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    >
                      <div className="font-medium text-sm">{suggestion.question}</div>
                      <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {suggestion.category}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              'flex gap-3',
              message.type === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            {message.type === 'bot' && (
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              </div>
            )}

            <div
              className={cn(
                'max-w-[80%]',
                message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 dark:bg-gray-800',
                'rounded-lg p-3'
              )}
            >
              <div 
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ 
                  __html: formatContent(message.content) 
                }}
              />
              
              {/* Metadata para respuestas del bot */}
              {message.type === 'bot' && (
                <div className="mt-3 space-y-2">
                  {/* Confianza */}
                  {message.confidence && (
                    <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                      <span>Confianza: {Math.round(message.confidence * 100)}%</span>
                      {message.category && (
                        <span>• Categoría: {message.category}</span>
                      )}
                    </div>
                  )}

                  {/* Fuentes */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="text-xs">
                      <div className="font-medium mb-1">Fuentes consultadas:</div>
                      <div className="space-y-1">
                        {message.sources.slice(0, 3).map((source, index) => (
                          <div key={index} className="text-gray-600 dark:text-gray-400">
                            • {source.title} (Relevancia: {Math.round(source.relevance * 100)}%)
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Sugerencias de seguimiento */}
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="text-xs">
                      <div className="font-medium mb-1">Preguntas relacionadas:</div>
                      <div className="flex flex-wrap gap-1">
                        {message.suggestions.slice(0, 3).map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleSendMessage(suggestion)}
                            className="px-2 py-1 bg-white hover:bg-gray-50 dark:bg-gray-700 dark:hover:bg-gray-600 rounded text-xs transition-colors"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {message.type === 'user' && (
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                  <User className="w-4 h-4 text-gray-700 dark:text-gray-300" />
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
            </div>
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Procesando tu consulta...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Escribe tu consulta legal aquí... (Ej: ¿Cómo constituyo una SAS?)"
              className="input min-h-[44px] max-h-32 resize-none pr-12"
              rows={1}
              disabled={isLoading}
            />
            <div className="absolute right-2 bottom-2 text-xs text-gray-600 dark:text-gray-400">
              {inputValue.length}/1000
            </div>
          </div>
          <button
            onClick={() => handleSendMessage()}
            disabled={!inputValue.trim() || isLoading || inputValue.length > 1000}
            className="btn-primary px-3 py-2 disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center gap-2 mt-2 text-xs text-gray-600 dark:text-gray-400">
          <AlertCircle className="w-3 h-3" />
          <span>
            Presiona Enter para enviar, Shift+Enter para nueva línea
          </span>
        </div>
      </div>
    </div>
  );
} 