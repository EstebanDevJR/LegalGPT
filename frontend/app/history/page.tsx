"use client"

import { useState, useMemo } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, Filter, CalendarIcon, MessageSquare, FileText, Clock, X, Download, Eye } from "lucide-react"
import { cn } from "@/lib/utils"
import { format } from "@/lib/date-fns"

// Datos de ejemplo del historial
const historyData = [
  {
    id: "1",
    type: "consultation",
    title: "Consulta sobre contratos laborales",
    description: "¿Cuáles son los requisitos mínimos para un contrato de trabajo en Colombia?",
    date: "2024-01-15",
    time: "14:30",
    status: "completed",
    category: "Laboral",
    duration: "5 min",
  },
  {
    id: "2",
    type: "document",
    title: "Contrato de prestación de servicios",
    description: "Documento generado para servicios de consultoría",
    date: "2024-01-14",
    time: "10:15",
    status: "signed",
    category: "Contratos",
    duration: "2 min",
  },
  {
    id: "3",
    type: "consultation",
    title: "Normativa tributaria para PyMEs",
    description: "Información sobre beneficios tributarios para pequeñas empresas",
    date: "2024-01-13",
    time: "16:45",
    status: "completed",
    category: "Tributario",
    duration: "8 min",
  },
  {
    id: "4",
    type: "document",
    title: "Acuerdo de confidencialidad",
    description: "NDA para protección de información comercial",
    date: "2024-01-12",
    time: "09:20",
    status: "pending",
    category: "Contratos",
    duration: "3 min",
  },
  {
    id: "5",
    type: "consultation",
    title: "Derechos de autor y propiedad intelectual",
    description: "Consulta sobre registro de marca y protección de software",
    date: "2024-01-11",
    time: "11:30",
    status: "completed",
    category: "Propiedad Intelectual",
    duration: "12 min",
  },
]

const statusConfig = {
  completed: { label: "Completado", color: "bg-green-500" },
  pending: { label: "Pendiente", color: "bg-yellow-500" },
  signed: { label: "Firmado", color: "bg-blue-500" },
  cancelled: { label: "Cancelado", color: "bg-red-500" },
}

const typeConfig = {
  consultation: { label: "Consulta", icon: MessageSquare, color: "text-blue-600" },
  document: { label: "Documento", icon: FileText, color: "text-green-600" },
}

export default function HistoryPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedDate, setSelectedDate] = useState<Date>()
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [selectedType, setSelectedType] = useState<string>("all")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // Obtener categorías únicas
  const categories = useMemo(() => {
    const cats = [...new Set(historyData.map((item) => item.category))]
    return cats.sort()
  }, [])

  // Filtrar datos
  const filteredData = useMemo(() => {
    return historyData.filter((item) => {
      const matchesSearch =
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.description.toLowerCase().includes(searchQuery.toLowerCase())

      const matchesDate = !selectedDate || item.date === format(selectedDate, "yyyy-MM-dd")
      const matchesStatus = selectedStatus === "all" || item.status === selectedStatus
      const matchesType = selectedType === "all" || item.type === selectedType
      const matchesCategory = selectedCategory === "all" || item.category === selectedCategory

      return matchesSearch && matchesDate && matchesStatus && matchesType && matchesCategory
    })
  }, [searchQuery, selectedDate, selectedStatus, selectedType, selectedCategory])

  // Contar filtros activos
  const activeFiltersCount = [
    selectedDate,
    selectedStatus !== "all",
    selectedType !== "all",
    selectedCategory !== "all",
  ].filter(Boolean).length

  // Limpiar todos los filtros
  const clearAllFilters = () => {
    setSearchQuery("")
    setSelectedDate(undefined)
    setSelectedStatus("all")
    setSelectedType("all")
    setSelectedCategory("all")
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar Desktop */}
      <div className="hidden md:flex md:w-64 md:flex-col">
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setIsMobileMenuOpen(true)} />

        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold mb-2">Historial</h1>
              <p className="text-muted-foreground">Revisa todas tus consultas y documentos anteriores</p>
            </div>

            {/* Filtros */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Filtros
                  {activeFiltersCount > 0 && <Badge variant="secondary">{activeFiltersCount}</Badge>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
                  {/* Búsqueda */}
                  <div className="lg:col-span-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Buscar en historial..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  {/* Fecha */}
                  <div>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !selectedDate && "text-muted-foreground",
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {selectedDate ? format(selectedDate, "dd/MM/yyyy") : "Fecha"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={selectedDate}
                          onSelect={setSelectedDate}
                          initialFocus
                          className="rounded-md border"
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  {/* Estado */}
                  <div>
                    <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                      <SelectTrigger>
                        <SelectValue placeholder="Estado" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Todos los estados</SelectItem>
                        {Object.entries(statusConfig).map(([key, config]) => (
                          <SelectItem key={key} value={key}>
                            {config.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Tipo */}
                  <div>
                    <Select value={selectedType} onValueChange={setSelectedType}>
                      <SelectTrigger>
                        <SelectValue placeholder="Tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Todos los tipos</SelectItem>
                        {Object.entries(typeConfig).map(([key, config]) => (
                          <SelectItem key={key} value={key}>
                            {config.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Categoría */}
                  <div>
                    <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                      <SelectTrigger>
                        <SelectValue placeholder="Categoría" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Todas las categorías</SelectItem>
                        {categories.map((category) => (
                          <SelectItem key={category} value={category}>
                            {category}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Filtros activos */}
                {activeFiltersCount > 0 && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    {selectedDate && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        Fecha: {format(selectedDate, "dd/MM/yyyy")}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedDate(undefined)} />
                      </Badge>
                    )}
                    {selectedStatus !== "all" && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        Estado: {statusConfig[selectedStatus as keyof typeof statusConfig]?.label}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedStatus("all")} />
                      </Badge>
                    )}
                    {selectedType !== "all" && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        Tipo: {typeConfig[selectedType as keyof typeof typeConfig]?.label}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedType("all")} />
                      </Badge>
                    )}
                    {selectedCategory !== "all" && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        Categoría: {selectedCategory}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedCategory("all")} />
                      </Badge>
                    )}
                    <Button variant="ghost" size="sm" onClick={clearAllFilters} className="h-6 px-2 text-xs">
                      Limpiar todo
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Resultados */}
            <div className="space-y-4">
              {filteredData.length === 0 ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <div className="text-muted-foreground text-center">
                      <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <h3 className="text-lg font-medium mb-2">No se encontraron resultados</h3>
                      <p>Intenta ajustar los filtros o realizar una nueva búsqueda</p>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                filteredData.map((item) => {
                  const TypeIcon = typeConfig[item.type as keyof typeof typeConfig].icon
                  const statusInfo = statusConfig[item.status as keyof typeof statusConfig]

                  return (
                    <Card key={item.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-4 flex-1">
                            <div
                              className={cn(
                                "p-2 rounded-lg",
                                item.type === "consultation"
                                  ? "bg-blue-100 dark:bg-blue-900/20"
                                  : "bg-green-100 dark:bg-green-900/20",
                              )}
                            >
                              <TypeIcon
                                className={cn("h-5 w-5", typeConfig[item.type as keyof typeof typeConfig].color)}
                              />
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <h3 className="font-semibold text-lg">{item.title}</h3>
                                <Badge variant="outline">{item.category}</Badge>
                                <div className="flex items-center gap-1">
                                  <div className={cn("w-2 h-2 rounded-full", statusInfo.color)} />
                                  <span className="text-sm text-muted-foreground">{statusInfo.label}</span>
                                </div>
                              </div>

                              <p className="text-muted-foreground mb-3 line-clamp-2">{item.description}</p>

                              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                <span>{format(new Date(item.date + "T" + item.time), "dd/MM/yyyy HH:mm")}</span>
                                <span>•</span>
                                <span>{item.duration}</span>
                                <span>•</span>
                                <span>{typeConfig[item.type as keyof typeof typeConfig].label}</span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-2 ml-4">
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })
              )}
            </div>

            {/* Paginación */}
            {filteredData.length > 0 && (
              <div className="flex justify-center mt-8">
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" disabled>
                    Anterior
                  </Button>
                  <Button variant="outline" size="sm" className="bg-primary text-primary-foreground">
                    1
                  </Button>
                  <Button variant="outline" size="sm">
                    2
                  </Button>
                  <Button variant="outline" size="sm">
                    3
                  </Button>
                  <Button variant="outline" size="sm">
                    Siguiente
                  </Button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Mobile Sidebar */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setIsMobileMenuOpen(false)} />
          <div className="fixed left-0 top-0 h-full w-64 bg-background border-r">
            <Sidebar />
          </div>
        </div>
      )}
    </div>
  )
}
