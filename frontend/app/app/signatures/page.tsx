"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { SignatureStatusCard } from "@/components/signature-status-card"
import { PenTool, Search, Filter, Plus, FileText, Clock, CheckCircle, AlertTriangle, XCircle, Send } from "lucide-react"
import { LoadingSpinner } from "@/components/loading-spinner"
import { AlertCircle } from "lucide-react" // Import AlertCircle

interface SignatureDocument {
  id: string
  name: string
  type: string
  status: "completed" | "partial" | "sent" | "expired"
  createdAt: string
  signers: Array<{
    name: string
    email: string
    status: "signed" | "pending" | "declined"
    signedAt?: string
  }>
  expiresAt: string
}

const mockSignatureDocuments = [
  {
    id: "1",
    title: "Contrato de Trabajo - Juan Pérez",
    status: "completed" as const,
    signatories: [
      { name: "María García", email: "maria@empresa.com", status: "signed" as const, signedAt: "2024-01-20T10:30:00Z" },
      { name: "Juan Pérez", email: "juan@email.com", status: "signed" as const, signedAt: "2024-01-20T14:15:00Z" },
    ],
    createdAt: "2024-01-19T09:00:00Z",
    expiresAt: "2024-02-19T09:00:00Z",
  },
  {
    id: "2",
    title: "Acta de Constitución - TechStart SAS",
    status: "partially_signed" as const,
    signatories: [
      {
        name: "Carlos Rodríguez",
        email: "carlos@techstart.com",
        status: "signed" as const,
        signedAt: "2024-01-21T11:20:00Z",
      },
      { name: "Ana López", email: "ana@techstart.com", status: "pending" as const },
      { name: "Luis Martínez", email: "luis@techstart.com", status: "pending" as const },
    ],
    createdAt: "2024-01-21T08:00:00Z",
    expiresAt: "2024-02-21T08:00:00Z",
  },
  {
    id: "3",
    title: "Política de Privacidad - DataCorp",
    status: "sent" as const,
    signatories: [
      { name: "Roberto Silva", email: "roberto@datacorp.com", status: "pending" as const },
      { name: "Carmen Ruiz", email: "carmen@datacorp.com", status: "pending" as const },
    ],
    createdAt: "2024-01-22T16:30:00Z",
    expiresAt: "2024-02-22T16:30:00Z",
  },
  {
    id: "4",
    title: "Contrato de Prestación de Servicios",
    status: "expired" as const,
    signatories: [{ name: "Diego Morales", email: "diego@freelance.com", status: "declined" as const }],
    createdAt: "2024-01-10T12:00:00Z",
    expiresAt: "2024-01-25T12:00:00Z",
  },
]

const getStatusIcon = (status: string) => {
  switch (status) {
    case "completed":
      return <CheckCircle className="h-4 w-4 text-green-500" />
    case "partial":
    case "partially_signed":
      return <Clock className="h-4 w-4 text-yellow-500" />
    case "sent":
      return <Send className="h-4 w-4 text-blue-500" />
    case "expired":
      return <XCircle className="h-4 w-4 text-red-500" />
    default:
      return <AlertCircle className="h-4 w-4 text-gray-500" />
  }
}

const getStatusLabel = (status: string) => {
  switch (status) {
    case "completed":
      return "Completado"
    case "partial":
    case "partially_signed":
      return "Parcial"
    case "sent":
      return "Enviado"
    case "expired":
      return "Expirado"
    default:
      return "Desconocido"
  }
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed":
      return "bg-green-100 text-green-800 border-green-200"
    case "partial":
    case "partially_signed":
      return "bg-yellow-100 text-yellow-800 border-yellow-200"
    case "sent":
      return "bg-blue-100 text-blue-800 border-blue-200"
    case "expired":
      return "bg-red-100 text-red-800 border-red-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

export default function SignaturesPage() {
  const { user, loading } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  const filteredDocuments = mockSignatureDocuments.filter((doc) => {
    const matchesSearch = doc.title.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || doc.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const stats = {
    total: mockSignatureDocuments.length,
    completed: mockSignatureDocuments.filter((d) => d.status === "completed").length,
    pending: mockSignatureDocuments.filter((d) => d.status === "sent" || d.status === "partially_signed").length,
    expired: mockSignatureDocuments.filter((d) => d.status === "expired").length,
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold flex items-center gap-2">
                  <PenTool className="h-8 w-8" />
                  Gestión de Firmas
                </h1>
                <p className="text-muted-foreground">Administra y monitorea el estado de tus documentos firmados</p>
              </div>
              <Button className="gap-2">
                <Plus className="h-4 w-4" />
                Nuevo Documento
              </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Documentos</p>
                      <p className="text-2xl font-bold">{stats.total}</p>
                    </div>
                    <FileText className="h-8 w-8 text-blue-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Completados</p>
                      <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Pendientes</p>
                      <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
                    </div>
                    <Clock className="h-8 w-8 text-yellow-500" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Expirados</p>
                      <p className="text-2xl font-bold text-red-600">{stats.expired}</p>
                    </div>
                    <AlertTriangle className="h-8 w-8 text-red-500" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar documentos..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-full md:w-[200px]">
                      <SelectValue placeholder="Estado" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Todos los estados</SelectItem>
                      <SelectItem value="completed">Completados</SelectItem>
                      <SelectItem value="partially_signed">Parcialmente firmados</SelectItem>
                      <SelectItem value="sent">Enviados</SelectItem>
                      <SelectItem value="expired">Expirados</SelectItem>
                    </SelectContent>
                  </Select>

                  <Button variant="outline" className="gap-2 bg-transparent">
                    <Filter className="h-4 w-4" />
                    Más filtros
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Documents Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredDocuments.map((document) => (
                <SignatureStatusCard
                  key={document.id}
                  document={document}
                  onViewDocument={() => console.log("View document", document.id)}
                  onDownload={() => console.log("Download document", document.id)}
                  onResend={() => console.log("Resend document", document.id)}
                />
              ))}
            </div>

            {/* Empty State */}
            {filteredDocuments.length === 0 && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <PenTool className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No se encontraron documentos</h3>
                  <p className="text-muted-foreground mb-4 text-center">
                    {searchTerm || statusFilter !== "all"
                      ? "Intenta ajustar los filtros de búsqueda"
                      : "Aún no has creado documentos para firma"}
                  </p>
                  <Button className="gap-2">
                    <Plus className="h-4 w-4" />
                    Crear Primer Documento
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
