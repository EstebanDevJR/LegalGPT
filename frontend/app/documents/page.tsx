"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Upload, FileText, Download, Trash2, Search, Filter } from "lucide-react"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"

const mockDocuments = [
  {
    id: "1",
    name: "Contrato de Trabajo - Juan Pérez.pdf",
    type: "Contrato Laboral",
    uploadDate: "2024-01-15",
    status: "processed",
    size: "2.3 MB",
  },
  {
    id: "2",
    name: "Estatutos Empresa SAS.pdf",
    type: "Documento Constitutivo",
    uploadDate: "2024-01-10",
    status: "processing",
    size: "1.8 MB",
  },
  {
    id: "3",
    name: "Política de Privacidad.docx",
    type: "Política",
    uploadDate: "2024-01-08",
    status: "error",
    size: "856 KB",
  },
]

export default function DocumentsPage() {
  const { user } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")

  if (!user) {
    return <AuthPage />
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "processed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "processing":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "error":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "processed":
        return "Procesado"
      case "processing":
        return "Procesando"
      case "error":
        return "Error"
      default:
        return "Desconocido"
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Documentos</h1>
                <p className="text-muted-foreground">Gestiona y analiza tus documentos legales</p>
              </div>
              <Button className="gap-2">
                <Upload className="h-4 w-4" />
                Subir Documento
              </Button>
            </div>

            {/* Upload Area */}
            <Card className="border-2 border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Upload className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Arrastra y suelta tus documentos</h3>
                <p className="text-muted-foreground mb-4">Soportamos PDF, DOC, DOCX hasta 10MB</p>
                <Button variant="outline">Seleccionar archivos</Button>
              </CardContent>
            </Card>

            {/* Search and Filter */}
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar documentos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button variant="outline" className="gap-2 bg-transparent">
                <Filter className="h-4 w-4" />
                Filtros
              </Button>
            </div>

            {/* Documents List */}
            <div className="grid gap-4">
              {mockDocuments.map((doc) => (
                <Card key={doc.id}>
                  <CardContent className="flex items-center justify-between p-6">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                        <FileText className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{doc.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <span>{doc.type}</span>
                          <span>•</span>
                          <span>{doc.size}</span>
                          <span>•</span>
                          <span>{new Date(doc.uploadDate).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <Badge className={getStatusColor(doc.status)}>{getStatusText(doc.status)}</Badge>

                      <div className="flex gap-1">
                        <Button size="icon" variant="ghost">
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button size="icon" variant="ghost">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Empty State */}
            {mockDocuments.length === 0 && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No hay documentos</h3>
                  <p className="text-muted-foreground mb-4">Sube tu primer documento para comenzar</p>
                  <Button>
                    <Upload className="h-4 w-4 mr-2" />
                    Subir Documento
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
