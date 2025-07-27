"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Send, Bot, Sparkles, FileText, Scale, Upload, Download } from "lucide-react"
import { useAuth } from "@/components/auth-provider"

interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: Date
  type?: "text" | "document" | "legal-advice"
  fileName?: string // Nuevo campo para el nombre del archivo
  fileUrl?: string // Nuevo campo para la URL del archivo
}

const suggestions = [
  {
    icon: Scale,
    title: "Consulta Laboral",
    description: "¿Cómo debo manejar la terminación de un contrato laboral?",
  },
  {
    icon: FileText,
    title: "Contrato Comercial",
    description: "Necesito revisar un contrato de prestación de servicios",
  },
  {
    icon: Bot,
    title: "Normativa Tributaria",
    description: "¿Qué obligaciones tributarias tiene mi PyME?",
  },
]

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null) // Ref para el input de archivo
  const { user } = useAuth()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (message?: string) => {
    const messageToSend = message || input
    if (!messageToSend.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageToSend,
      sender: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simular respuesta de IA
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `Basándome en la legislación colombiana vigente, te puedo ayudar con tu consulta sobre "${messageToSend}". 

Para las PyMEs en Colombia, es importante considerar:

1. **Marco Legal**: La normativa aplicable según el Código de Comercio y las regulaciones específicas del sector.

2. **Obligaciones**: Las responsabilidades legales que debe cumplir tu empresa.

3. **Recomendaciones**: Pasos específicos que puedes seguir para asegurar el cumplimiento.

¿Te gustaría que profundice en algún aspecto específico de tu consulta?`,
        sender: "assistant",
        timestamp: new Date(),
        type: "legal-advice",
      }

      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 2000)
  }

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion)
  }

  const handleFileUploadClick = () => {
    fileInputRef.current?.click() // Simula el click en el input de archivo oculto
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const fileMessage: Message = {
        id: Date.now().toString(),
        content: `Documento subido: ${file.name}`,
        sender: "user",
        timestamp: new Date(),
        type: "document",
        fileName: file.name,
        fileUrl: URL.createObjectURL(file), // Crea una URL temporal para la vista previa
      }
      setMessages((prev) => [...prev, fileMessage])
      setIsLoading(true)

      // Simular procesamiento del documento por la IA
      setTimeout(() => {
        const assistantResponse: Message = {
          id: (Date.now() + 1).toString(),
          content: `He recibido el documento "${file.name}". ¿En qué puedo ayudarte con él? Por ejemplo, puedo resumirlo, identificar cláusulas clave o revisar su conformidad legal.`,
          sender: "assistant",
          timestamp: new Date(),
          type: "legal-advice",
        }
        setMessages((prev) => [...prev, assistantResponse])
        setIsLoading(false)
        // Limpiar el input de archivo para permitir subir el mismo archivo de nuevo
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
      }, 2500)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto">
            <div className="flex items-center gap-2 mb-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Bot className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">¡Hola, {user?.name}!</h1>
                <p className="text-muted-foreground">¿En qué puedo ayudarte hoy?</p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4 w-full mb-8">
              {suggestions.map((suggestion, index) => (
                <Card
                  key={index}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => handleSuggestionClick(suggestion.description)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                        <suggestion.icon className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-sm mb-1">{suggestion.title}</h3>
                        <p className="text-xs text-muted-foreground">{suggestion.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="text-sm text-muted-foreground">
              <p className="flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Powered by AI especializada en legislación colombiana
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.sender === "assistant" && (
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <Bot className="h-4 w-4" />
                    </AvatarFallback>
                  </Avatar>
                )}

                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    message.sender === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}
                >
                  {message.type === "document" && message.fileName ? (
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      <a
                        href={message.fileUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="underline hover:no-underline"
                        download={message.fileName}
                      >
                        {message.fileName}
                      </a>
                      <Download className="h-4 w-4" />
                    </div>
                  ) : (
                    <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                  )}

                  {message.type === "legal-advice" && (
                    <Badge variant="secondary" className="mt-2">
                      <Scale className="h-3 w-3 mr-1" />
                      Asesoría Legal
                    </Badge>
                  )}
                  <div className="text-xs opacity-70 mt-1">{message.timestamp.toLocaleTimeString()}</div>
                </div>

                {message.sender === "user" && (
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/placeholder.svg" alt={user?.name} />
                    <AvatarFallback>{user?.name?.charAt(0)}</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3 justify-start">
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="h-4 w-4" />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-muted rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-primary rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-primary rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <span className="text-sm text-muted-foreground">Analizando tu consulta...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex gap-2 max-w-4xl mx-auto">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu consulta legal aquí..."
            onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            disabled={isLoading}
            className="flex-1"
          />
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            disabled={isLoading}
            accept=".pdf,.doc,.docx,.txt" // Tipos de archivo aceptados
          />
          <Button onClick={handleFileUploadClick} disabled={isLoading} variant="outline" size="icon">
            <Upload className="h-4 w-4" />
            <span className="sr-only">Subir documento</span>
          </Button>
          <Button onClick={() => handleSend()} disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-xs text-muted-foreground text-center mt-2">
          LegalGPT puede cometer errores. Considera verificar información importante.
        </div>
      </div>
    </div>
  )
}
