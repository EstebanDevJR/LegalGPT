"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, FileText, Download, Share2, Eye, Trash2, Upload } from "lucide-react"

const mockDocuments = [
  {
    id: "1",
    name: "Contrato de Trabajo - Juan Pérez",
    type: "Contrato Laboral",
    size: "245 KB",
    createdAt: "2024-01-15",
    status: "completed",
    category: "Laboral",
  },
  {
    id: "2",
    name: "Estatutos SAS - TechCorp",
    type: "Documento Societario",
    size: "512 KB",
    createdAt: "2024-01-14",
    status: "draft",
    category: "Societario",
  },
  {
    id: "3",
    name: "Solicitud Registro de Marca",
    type: "Formulario SIC",
    size: "128 KB",
    createdAt: "2024-01-13",
    status: "completed",
    category: "Propiedad Intelectual",
  },
  {
    id: "4",
    name: "Contrato de Prestación de Servicios",
    type: "Contrato Comercial",
    size: "189 KB",
    createdAt: "2024-01-12",
    status: "review",
    category: "Contractual",
  },
]

export default function DocumentsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")

  const filteredDocuments = mockDocuments.filter((doc) => {
    const matchesSearch =
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.type.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || doc.category === selectedCategory
    const matchesStatus = selectedStatus === "all" || doc.status === selectedStatus

    return matchesSearch && matchesCategory && matchesStatus
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Completado</Badge>
      case "draft":
        return <Badge variant="secondary">Borrador</Badge>
      case "review":
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">En revisión</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex flex-1 flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Mis Documentos</h1>
                <p className="text-muted-foreground">Gestiona todos tus documentos legales</p>
              </div>
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Subir Documento
              </Button>
            </div>

            {/* Filtros */}
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar documentos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Todas las categorías" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas las categorías</SelectItem>
                  <SelectItem value="Laboral">Laboral</SelectItem>
                  <SelectItem value="Societario">Societario</SelectItem>
                  <SelectItem value="Tributario">Tributario</SelectItem>
                  <SelectItem value="Propiedad Intelectual">Propiedad Intelectual</SelectItem>
                  <SelectItem value="Contractual">Contractual</SelectItem>
                </SelectContent>
              </Select>
              <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Estado" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="completed">Completado</SelectItem>
                  <SelectItem value="draft">Borrador</SelectItem>
                  <SelectItem value="review">En revisión</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Lista de documentos */}
            <div className="space-y-4">
              {filteredDocuments.length === 0 ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No se encontraron documentos</h3>
                    <p className="text-muted-foreground text-center">
                      {searchTerm || selectedCategory !== "all" || selectedStatus !== "all"
                        ? "No hay documentos que coincidan con los filtros aplicados."
                        : "Aún no tienes documentos. Sube tu primer documento para comenzar."}
                    </p>
                  </CardContent>
                </Card>
              ) : (
                filteredDocuments.map((doc) => (
                  <Card key={doc.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                            <FileText className="h-6 w-6 text-primary" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-lg">{doc.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-sm text-muted-foreground">{doc.type}</span>
                              <span className="text-sm text-muted-foreground">•</span>
                              <span className="text-sm text-muted-foreground">{doc.size}</span>
                              <span className="text-sm text-muted-foreground">•</span>
                              <span className="text-sm text-muted-foreground">{doc.createdAt}</span>
                            </div>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge variant="outline">{doc.category}</Badge>
                              {getStatusBadge(doc.status)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            Ver
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            Descargar
                          </Button>
                          <Button variant="outline" size="sm">
                            <Share2 className="h-4 w-4 mr-1" />
                            Compartir
                          </Button>
                          <Button variant="outline" size="sm">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
