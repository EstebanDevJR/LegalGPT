"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Plus, Edit, Trash2, Eye, BookmarkPlus, Star } from "lucide-react"

const mockTemplates = [
  {
    id: "1",
    title: "Consulta sobre contratos laborales",
    description: "Plantilla para consultas relacionadas con contratos de trabajo",
    content:
      "Necesito información sobre {tipo_contrato} en Colombia. Específicamente sobre {aspecto_especifico}. Mi empresa es {tipo_empresa} y tenemos {numero_empleados} empleados.",
    category: "Laboral",
    variables: ["tipo_contrato", "aspecto_especifico", "tipo_empresa", "numero_empleados"],
    isPublic: true,
    isFavorite: true,
    createdAt: "2024-01-15",
    usageCount: 15,
  },
  {
    id: "2",
    title: "Constitución de empresa",
    description: "Plantilla para consultas sobre constitución de sociedades",
    content:
      "Quiero constituir una {tipo_sociedad} en Colombia. Mi actividad económica será {actividad}. Tengo {numero_socios} socios y un capital inicial de {capital}.",
    category: "Societario",
    variables: ["tipo_sociedad", "actividad", "numero_socios", "capital"],
    isPublic: false,
    isFavorite: false,
    createdAt: "2024-01-14",
    usageCount: 8,
  },
  {
    id: "3",
    title: "Registro de marca",
    description: "Plantilla para consultas sobre propiedad intelectual",
    content:
      "Necesito registrar la marca {nombre_marca} en la clase {clase_niza}. Mi producto/servicio es {descripcion_producto}.",
    category: "Propiedad Intelectual",
    variables: ["nombre_marca", "clase_niza", "descripcion_producto"],
    isPublic: true,
    isFavorite: true,
    createdAt: "2024-01-13",
    usageCount: 12,
  },
]

export default function TemplatesPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newTemplate, setNewTemplate] = useState({
    title: "",
    description: "",
    content: "",
    category: "",
  })

  const filteredTemplates = mockTemplates.filter((template) => {
    const matchesSearch =
      template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = !selectedCategory || template.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  const handleCreateTemplate = () => {
    console.log("Crear plantilla:", newTemplate)
    setShowCreateDialog(false)
    setNewTemplate({ title: "", description: "", content: "", category: "" })
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
                <h1 className="text-3xl font-bold">Plantillas de Consulta</h1>
                <p className="text-muted-foreground">Crea y gestiona plantillas reutilizables para tus consultas</p>
              </div>
              <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Nueva Plantilla
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>Crear Nueva Plantilla</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="title">Título</Label>
                      <Input
                        id="title"
                        value={newTemplate.title}
                        onChange={(e) => setNewTemplate({ ...newTemplate, title: e.target.value })}
                        placeholder="Nombre de la plantilla"
                      />
                    </div>
                    <div>
                      <Label htmlFor="description">Descripción</Label>
                      <Input
                        id="description"
                        value={newTemplate.description}
                        onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                        placeholder="Breve descripción de la plantilla"
                      />
                    </div>
                    <div>
                      <Label htmlFor="category">Categoría</Label>
                      <Select
                        value={newTemplate.category}
                        onValueChange={(value) => setNewTemplate({ ...newTemplate, category: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Seleccionar categoría" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Laboral">Laboral</SelectItem>
                          <SelectItem value="Societario">Societario</SelectItem>
                          <SelectItem value="Tributario">Tributario</SelectItem>
                          <SelectItem value="Propiedad Intelectual">Propiedad Intelectual</SelectItem>
                          <SelectItem value="Contractual">Contractual</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="content">Contenido de la Plantilla</Label>
                      <Textarea
                        id="content"
                        value={newTemplate.content}
                        onChange={(e) => setNewTemplate({ ...newTemplate, content: e.target.value })}
                        placeholder="Escribe tu plantilla aquí. Usa {variable} para crear variables dinámicas."
                        rows={6}
                      />
                      <p className="text-sm text-muted-foreground mt-1">
                        Tip: Usa llaves para crear variables, por ejemplo: {"{nombre_empresa}"}
                      </p>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                        Cancelar
                      </Button>
                      <Button onClick={handleCreateTemplate}>Crear Plantilla</Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            {/* Filtros */}
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar plantillas..."
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
            </div>

            {/* Lista de plantillas */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTemplates.length === 0 ? (
                <div className="col-span-full">
                  <Card>
                    <CardContent className="flex flex-col items-center justify-center py-12">
                      <BookmarkPlus className="h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No se encontraron plantillas</h3>
                      <p className="text-muted-foreground text-center">
                        {searchTerm || selectedCategory
                          ? "No hay plantillas que coincidan con los filtros aplicados."
                          : "Crea tu primera plantilla para comenzar."}
                      </p>
                    </CardContent>
                  </Card>
                </div>
              ) : (
                filteredTemplates.map((template) => (
                  <Card key={template.id} className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg flex items-center gap-2">
                            {template.title}
                            {template.isFavorite && <Star className="h-4 w-4 text-yellow-500 fill-current" />}
                          </CardTitle>
                          <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{template.category}</Badge>
                        {template.isPublic && <Badge variant="secondary">Pública</Badge>}
                      </div>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-muted-foreground">Variables:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {template.variables.map((variable) => (
                              <Badge key={variable} variant="outline" className="text-xs">
                                {variable}
                              </Badge>
                            ))}
                          </div>
                        </div>
                        <div className="text-xs text-muted-foreground">Usada {template.usageCount} veces</div>
                        <div className="flex gap-2">
                          <Button size="sm" variant="outline" className="flex-1 bg-transparent">
                            <Eye className="h-3 w-3 mr-1" />
                            Ver
                          </Button>
                          <Button size="sm" variant="outline">
                            <Edit className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Trash2 className="h-3 w-3" />
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
