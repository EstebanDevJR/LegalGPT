"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { useToast } from "@/hooks/use-toast"
import {
  Search,
  Plus,
  BookmarkPlus,
  Star,
  MoreHorizontal,
  Edit,
  Copy,
  Trash2,
  Play,
  Filter,
  Grid,
  List,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { CreateTemplateDialog } from "@/components/create-template-dialog"
import { EditTemplateDialog } from "@/components/edit-template-dialog"
import { TemplatePreviewDialog } from "@/components/template-preview-dialog"

interface Template {
  id: string
  title: string
  description: string
  content: string
  category: string
  tags: string[]
  isPublic: boolean
  isFavorite: boolean
  usageCount: number
  createdAt: string
  updatedAt: string
  variables?: { name: string; placeholder: string; required: boolean }[]
}

const mockTemplates: Template[] = [
  {
    id: "1",
    title: "Registro de SAS",
    description: "Plantilla para consultas sobre registro de Sociedad por Acciones Simplificada",
    content:
      "¿Cuáles son los pasos específicos para registrar una empresa como SAS en Colombia? Mi empresa se llama {{nombreEmpresa}} y se dedica a {{actividadEconomica}}. ¿Qué documentos necesito y cuáles son los costos aproximados?",
    category: "Constitución Empresarial",
    tags: ["SAS", "Registro", "Cámara de Comercio", "Constitución"],
    isPublic: false,
    isFavorite: true,
    usageCount: 12,
    createdAt: "2024-01-15T10:30:00Z",
    updatedAt: "2024-01-20T15:45:00Z",
    variables: [
      { name: "nombreEmpresa", placeholder: "Nombre de tu empresa", required: true },
      { name: "actividadEconomica", placeholder: "Actividad económica principal", required: true },
    ],
  },
  {
    id: "2",
    title: "Contrato Laboral Básico",
    description: "Plantilla para redactar contratos de trabajo indefinido",
    content:
      "Necesito redactar un contrato de trabajo indefinido para el cargo de {{cargo}} con un salario de {{salario}}. ¿Qué cláusulas son obligatorias y cuáles recomiendan incluir? La jornada será de {{tipoJornada}}.",
    category: "Laboral",
    tags: ["Contrato", "Laboral", "Indefinido", "Salario"],
    isPublic: true,
    isFavorite: false,
    usageCount: 8,
    createdAt: "2024-01-10T09:15:00Z",
    updatedAt: "2024-01-18T11:20:00Z",
    variables: [
      { name: "cargo", placeholder: "Cargo o posición", required: true },
      { name: "salario", placeholder: "Salario mensual", required: true },
      { name: "tipoJornada", placeholder: "Tiempo completo/medio tiempo", required: false },
    ],
  },
  {
    id: "3",
    title: "Consulta Tributaria PyME",
    description: "Plantilla para consultas sobre obligaciones tributarias",
    content:
      "Mi empresa {{nombreEmpresa}} es una {{tipoEmpresa}} con ingresos anuales de aproximadamente {{ingresos}}. ¿Cuáles son mis obligaciones tributarias específicas y qué régimen me conviene más?",
    category: "Tributario",
    tags: ["Impuestos", "PyME", "DIAN", "Régimen"],
    isPublic: false,
    isFavorite: true,
    usageCount: 15,
    createdAt: "2024-01-08T14:20:00Z",
    updatedAt: "2024-01-22T16:30:00Z",
    variables: [
      { name: "nombreEmpresa", placeholder: "Nombre de la empresa", required: true },
      { name: "tipoEmpresa", placeholder: "Micro/Pequeña/Mediana", required: true },
      { name: "ingresos", placeholder: "Ingresos anuales aproximados", required: false },
    ],
  },
  {
    id: "4",
    title: "Protección de Marca",
    description: "Consulta sobre registro y protección de marcas comerciales",
    content:
      "Quiero registrar la marca {{nombreMarca}} para mi empresa que se dedica a {{sector}}. ¿Cuál es el proceso ante la SIC y qué clases de productos/servicios debo registrar?",
    category: "Propiedad Intelectual",
    tags: ["Marca", "SIC", "Registro", "Protección"],
    isPublic: true,
    isFavorite: false,
    usageCount: 6,
    createdAt: "2024-01-05T11:45:00Z",
    updatedAt: "2024-01-15T13:10:00Z",
    variables: [
      { name: "nombreMarca", placeholder: "Nombre de la marca", required: true },
      { name: "sector", placeholder: "Sector o industria", required: true },
    ],
  },
  {
    id: "5",
    title: "Terminación de Contrato",
    description: "Plantilla para consultas sobre terminación laboral",
    content:
      "Necesito terminar el contrato laboral de un empleado por {{motivoTerminacion}}. El empleado lleva {{tiempoTrabajo}} en la empresa. ¿Cuál es el procedimiento correcto y qué indemnizaciones debo pagar?",
    category: "Laboral",
    tags: ["Terminación", "Indemnización", "Procedimiento"],
    isPublic: false,
    isFavorite: false,
    usageCount: 4,
    createdAt: "2024-01-03T16:00:00Z",
    updatedAt: "2024-01-12T10:25:00Z",
    variables: [
      { name: "motivoTerminacion", placeholder: "Motivo de terminación", required: true },
      { name: "tiempoTrabajo", placeholder: "Tiempo trabajado", required: true },
    ],
  },
]

const categories = [
  "Todas las categorías",
  "Constitución Empresarial",
  "Tributario",
  "Laboral",
  "Propiedad Intelectual",
  "Comercial",
  "Civil",
]

export default function TemplatesPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("Todas las categorías")
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)
  const [showPublicOnly, setShowPublicOnly] = useState(false)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [templates, setTemplates] = useState<Template[]>(mockTemplates)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<Template | null>(null)

  if (!user) {
    return <AuthPage />
  }

  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))

    const matchesCategory = selectedCategory === "Todas las categorías" || template.category === selectedCategory
    const matchesFavorites = !showFavoritesOnly || template.isFavorite
    const matchesPublic = !showPublicOnly || template.isPublic

    return matchesSearch && matchesCategory && matchesFavorites && matchesPublic
  })

  const handleToggleFavorite = (templateId: string) => {
    setTemplates((prev) =>
      prev.map((template) =>
        template.id === templateId ? { ...template, isFavorite: !template.isFavorite } : template,
      ),
    )
    toast({
      title: "Plantilla actualizada",
      description: "La plantilla ha sido añadida/removida de favoritos",
    })
  }

  const handleDuplicateTemplate = (template: Template) => {
    const newTemplate: Template = {
      ...template,
      id: Date.now().toString(),
      title: `${template.title} (Copia)`,
      usageCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    setTemplates((prev) => [newTemplate, ...prev])
    toast({
      title: "Plantilla duplicada",
      description: "Se ha creado una copia de la plantilla",
    })
  }

  const handleDeleteTemplate = (templateId: string) => {
    setTemplates((prev) => prev.filter((template) => template.id !== templateId))
    toast({
      title: "Plantilla eliminada",
      description: "La plantilla ha sido eliminada correctamente",
    })
  }

  const handleUseTemplate = (template: Template) => {
    // Aquí redirigirías al chat con la plantilla cargada
    toast({
      title: "Plantilla cargada",
      description: "La plantilla ha sido cargada en el chat",
    })
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
                <h1 className="text-3xl font-bold">Plantillas</h1>
                <p className="text-muted-foreground">Guarda y reutiliza tus consultas más frecuentes</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant={viewMode === "grid" ? "default" : "outline"}
                  size="icon"
                  onClick={() => setViewMode("grid")}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "default" : "outline"}
                  size="icon"
                  onClick={() => setViewMode("list")}
                >
                  <List className="h-4 w-4" />
                </Button>
                <Button onClick={() => setCreateDialogOpen(true)} className="gap-2">
                  <Plus className="h-4 w-4" />
                  Nueva Plantilla
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Plantillas</p>
                      <p className="text-2xl font-bold">{templates.length}</p>
                    </div>
                    <BookmarkPlus className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Favoritas</p>
                      <p className="text-2xl font-bold">{templates.filter((t) => t.isFavorite).length}</p>
                    </div>
                    <Star className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Más Usada</p>
                      <p className="text-2xl font-bold">{Math.max(...templates.map((t) => t.usageCount))}</p>
                    </div>
                    <Play className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Públicas</p>
                      <p className="text-2xl font-bold">{templates.filter((t) => t.isPublic).length}</p>
                    </div>
                    <Filter className="h-8 w-8 text-muted-foreground" />
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
                      placeholder="Buscar plantillas..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-full md:w-[200px]">
                      <SelectValue placeholder="Categoría" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <div className="flex gap-2">
                    <Button
                      variant={showFavoritesOnly ? "default" : "outline"}
                      onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
                      className="gap-2 bg-transparent"
                    >
                      <Star className={`h-4 w-4 ${showFavoritesOnly ? "fill-current" : ""}`} />
                      Favoritas
                    </Button>
                    <Button
                      variant={showPublicOnly ? "default" : "outline"}
                      onClick={() => setShowPublicOnly(!showPublicOnly)}
                      className="gap-2 bg-transparent"
                    >
                      Públicas
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Templates Grid/List */}
            <div className={viewMode === "grid" ? "grid gap-4 md:grid-cols-2 lg:grid-cols-3" : "space-y-4"}>
              {filteredTemplates.map((template) => (
                <Card key={template.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <CardTitle className="text-lg">{template.title}</CardTitle>
                          {template.isFavorite && <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />}
                        </div>
                        <CardDescription className="line-clamp-2">{template.description}</CardDescription>
                      </div>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleUseTemplate(template)}>
                            <Play className="h-4 w-4 mr-2" />
                            Usar plantilla
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => setPreviewTemplate(template)}>
                            <Search className="h-4 w-4 mr-2" />
                            Vista previa
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => setEditingTemplate(template)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Editar
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleDuplicateTemplate(template)}>
                            <Copy className="h-4 w-4 mr-2" />
                            Duplicar
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleToggleFavorite(template.id)}>
                            <Star className="h-4 w-4 mr-2" />
                            {template.isFavorite ? "Quitar de favoritos" : "Añadir a favoritos"}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={() => handleDeleteTemplate(template.id)} className="text-red-600">
                            <Trash2 className="h-4 w-4 mr-2" />
                            Eliminar
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="secondary">{template.category}</Badge>
                      {template.isPublic && <Badge variant="outline">Pública</Badge>}
                      {template.variables && template.variables.length > 0 && (
                        <Badge variant="outline">{template.variables.length} variables</Badge>
                      )}
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {template.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {template.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{template.tags.length - 3}
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span>Usada {template.usageCount} veces</span>
                      <span>{new Date(template.updatedAt).toLocaleDateString()}</span>
                    </div>

                    <div className="flex gap-2">
                      <Button onClick={() => handleUseTemplate(template)} className="flex-1 gap-2">
                        <Play className="h-4 w-4" />
                        Usar
                      </Button>
                      <Button variant="outline" onClick={() => setPreviewTemplate(template)}>
                        Vista previa
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Empty State */}
            {filteredTemplates.length === 0 && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <BookmarkPlus className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No se encontraron plantillas</h3>
                  <p className="text-muted-foreground mb-4 text-center">
                    {searchTerm || selectedCategory !== "Todas las categorías"
                      ? "Intenta ajustar los filtros de búsqueda"
                      : "Crea tu primera plantilla para reutilizar consultas frecuentes"}
                  </p>
                  <Button onClick={() => setCreateDialogOpen(true)} className="gap-2">
                    <Plus className="h-4 w-4" />
                    Crear Plantilla
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>

      {/* Dialogs */}
      <CreateTemplateDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onTemplateCreated={(template) => {
          setTemplates((prev) => [template, ...prev])
          toast({
            title: "Plantilla creada",
            description: "La plantilla ha sido creada correctamente",
          })
        }}
      />

      {editingTemplate && (
        <EditTemplateDialog
          template={editingTemplate}
          open={!!editingTemplate}
          onOpenChange={(open) => !open && setEditingTemplate(null)}
          onTemplateUpdated={(updatedTemplate) => {
            setTemplates((prev) =>
              prev.map((template) => (template.id === updatedTemplate.id ? updatedTemplate : template)),
            )
            setEditingTemplate(null)
            toast({
              title: "Plantilla actualizada",
              description: "Los cambios han sido guardados correctamente",
            })
          }}
        />
      )}

      {previewTemplate && (
        <TemplatePreviewDialog
          template={previewTemplate}
          open={!!previewTemplate}
          onOpenChange={(open) => !open && setPreviewTemplate(null)}
          onUseTemplate={() => {
            handleUseTemplate(previewTemplate)
            setPreviewTemplate(null)
          }}
        />
      )}
    </div>
  )
}
