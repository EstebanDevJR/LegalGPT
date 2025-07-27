"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Search, CalendarIcon, Filter, X, MessageSquare, Clock, User } from "lucide-react"
import { format } from "@/lib/date-fns"
import { cn } from "@/lib/utils"

const mockHistory = [
  {
    id: "1",
    title: "Consulta sobre contratos laborales",
    preview: "¿Cuáles son los requisitos mínimos para un contrato de trabajo en Colombia?",
    date: "2024-01-15",
    time: "14:30",
    status: "completed",
    category: "Laboral",
    tokens: 150,
  },
  {
    id: "2",
    title: "Registro de marca comercial",
    preview: "Necesito información sobre el proceso de registro de marca en la SIC",
    date: "2024-01-14",
    time: "09:15",
    status: "completed",
    category: "Propiedad Intelectual",
    tokens: 200,
  },
  {
    id: "3",
    title: "Constitución de SAS",
    preview: "¿Qué documentos necesito para constituir una SAS?",
    date: "2024-01-13",
    time: "16:45",
    status: "completed",
    category: "Societario",
    tokens: 180,
  },
  {
    id: "4",
    title: "Consulta tributaria",
    preview: "Dudas sobre declaración de renta para personas jurídicas",
    date: "2024-01-12",
    time: "11:20",
    status: "completed",
    category: "Tributario",
    tokens: 220,
  },
]

export default function HistoryPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedDate, setSelectedDate] = useState<Date>()
  const [selectedStatus, setSelectedStatus] = useState<string>("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")

  const filteredHistory = mockHistory.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.preview.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDate = !selectedDate || item.date === format(selectedDate, "yyyy-MM-dd")
    const matchesStatus = !selectedStatus || item.status === selectedStatus
    const matchesCategory = !selectedCategory || item.category === selectedCategory

    return matchesSearch && matchesDate && matchesStatus && matchesCategory
  })

  const clearFilters = () => {
    setSearchTerm("")
    setSelectedDate(undefined)
    setSelectedStatus("")
    setSelectedCategory("")
  }

  const hasActiveFilters = searchTerm || selectedDate || selectedStatus || selectedCategory

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex flex-1 flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Historial de Consultas</h1>
                <p className="text-muted-foreground">Revisa todas tus consultas anteriores</p>
              </div>
            </div>

            {/* Filtros */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Filtros
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {/* Búsqueda */}
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar consultas..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* Fecha */}
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn("justify-start text-left font-normal", !selectedDate && "text-muted-foreground")}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {selectedDate ? format(selectedDate, "dd/MM/yyyy") : "Seleccionar fecha"}
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

                  {/* Estado */}
                  <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                    <SelectTrigger>
                      <SelectValue placeholder="Estado" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="completed">Completada</SelectItem>
                      <SelectItem value="pending">Pendiente</SelectItem>
                      <SelectItem value="in-progress">En progreso</SelectItem>
                    </SelectContent>
                  </Select>

                  {/* Categoría */}
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="Categoría" />
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

                {/* Filtros activos */}
                {hasActiveFilters && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm text-muted-foreground">Filtros activos:</span>
                    {searchTerm && (
                      <Badge variant="secondary" className="gap-1">
                        Búsqueda: {searchTerm}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSearchTerm("")} />
                      </Badge>
                    )}
                    {selectedDate && (
                      <Badge variant="secondary" className="gap-1">
                        Fecha: {format(selectedDate, "dd/MM/yyyy")}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedDate(undefined)} />
                      </Badge>
                    )}
                    {selectedStatus && (
                      <Badge variant="secondary" className="gap-1">
                        Estado: {selectedStatus}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedStatus("")} />
                      </Badge>
                    )}
                    {selectedCategory && (
                      <Badge variant="secondary" className="gap-1">
                        Categoría: {selectedCategory}
                        <X className="h-3 w-3 cursor-pointer" onClick={() => setSelectedCategory("")} />
                      </Badge>
                    )}
                    <Button variant="ghost" size="sm" onClick={clearFilters}>
                      Limpiar filtros
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Lista de consultas */}
            <div className="space-y-4">
              {filteredHistory.length === 0 ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No se encontraron consultas</h3>
                    <p className="text-muted-foreground text-center">
                      {hasActiveFilters
                        ? "No hay consultas que coincidan con los filtros aplicados."
                        : "Aún no has realizado ninguna consulta."}
                    </p>
                  </CardContent>
                </Card>
              ) : (
                filteredHistory.map((item) => (
                  <Card key={item.id} className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-semibold text-lg">{item.title}</h3>
                            <Badge variant="outline">{item.category}</Badge>
                            <Badge variant="secondary">Completada</Badge>
                          </div>
                          <p className="text-muted-foreground mb-4">{item.preview}</p>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="h-4 w-4" />
                              {format(new Date(item.date + "T" + item.time), "dd/MM/yyyy HH:mm")}
                            </div>
                            <div className="flex items-center gap-1">
                              <User className="h-4 w-4" />
                              {item.tokens} tokens usados
                            </div>
                          </div>
                        </div>
                        <Button variant="outline" size="sm">
                          Ver detalles
                        </Button>
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
