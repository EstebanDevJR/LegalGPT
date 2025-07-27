"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { BarChart3, TrendingUp, Clock, Target, MessageSquare, Star, Zap, Award } from "lucide-react"

const monthlyData = [
  { month: "Ene", consultas: 8, tokens: 2400, tiempo: 2.1 },
  { month: "Feb", consultas: 12, tokens: 3600, tiempo: 2.3 },
  { month: "Mar", consultas: 15, tokens: 4200, tiempo: 2.0 },
  { month: "Abr", consultas: 18, tokens: 5100, tiempo: 2.4 },
  { month: "May", consultas: 22, tokens: 6300, tiempo: 2.2 },
  { month: "Jun", consultas: 25, tokens: 7200, tiempo: 2.5 },
]

const categoryStats = [
  { category: "Tributario", count: 15, percentage: 32, color: "bg-blue-500" },
  { category: "Laboral", count: 12, percentage: 26, color: "bg-green-500" },
  { category: "Constitución Empresarial", count: 8, percentage: 17, color: "bg-purple-500" },
  { category: "Comercial", count: 6, percentage: 13, color: "bg-orange-500" },
  { category: "Propiedad Intelectual", count: 4, percentage: 8, color: "bg-pink-500" },
  { category: "Civil", count: 2, percentage: 4, color: "bg-gray-500" },
]

const topQueries = [
  { query: "¿Cómo registro mi empresa como SAS?", count: 3, category: "Constitución" },
  { query: "Obligaciones tributarias PyME", count: 2, category: "Tributario" },
  { query: "Contrato de trabajo indefinido", count: 2, category: "Laboral" },
  { query: "Protección de marca comercial", count: 2, category: "Propiedad Intelectual" },
  { query: "Régimen simple de tributación", count: 1, category: "Tributario" },
]

export default function StatsPage() {
  const { user } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [timeRange, setTimeRange] = useState("6m")

  if (!user) {
    return <AuthPage />
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
                <h1 className="text-3xl font-bold">Estadísticas</h1>
                <p className="text-muted-foreground">Analiza tu uso y rendimiento en LegalGPT</p>
              </div>
              <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Período" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1m">Último mes</SelectItem>
                  <SelectItem value="3m">Últimos 3 meses</SelectItem>
                  <SelectItem value="6m">Últimos 6 meses</SelectItem>
                  <SelectItem value="1y">Último año</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Consultas</p>
                      <p className="text-3xl font-bold">47</p>
                      <p className="text-xs text-green-600 flex items-center gap-1 mt-1">
                        <TrendingUp className="h-3 w-3" />
                        +12% vs mes anterior
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                      <MessageSquare className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Tiempo Promedio</p>
                      <p className="text-3xl font-bold">2.3 min</p>
                      <p className="text-xs text-green-600 flex items-center gap-1 mt-1">
                        <TrendingUp className="h-3 w-3" />
                        -8% más rápido
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                      <Clock className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Precisión Promedio</p>
                      <p className="text-3xl font-bold">94%</p>
                      <p className="text-xs text-green-600 flex items-center gap-1 mt-1">
                        <TrendingUp className="h-3 w-3" />
                        +2% mejora
                      </p>
                    </div>
                    <div className="h-12 w-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                      <Target className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Tokens Usados</p>
                      <p className="text-3xl font-bold">7.2K</p>
                      <p className="text-xs text-muted-foreground mt-1">de 10K disponibles</p>
                    </div>
                    <div className="h-12 w-12 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                      <Zap className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              {/* Usage Trends */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    Tendencia de Uso
                  </CardTitle>
                  <CardDescription>Consultas realizadas por mes</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {monthlyData.map((data, index) => (
                      <div key={data.month} className="flex items-center gap-4">
                        <div className="w-8 text-sm font-medium">{data.month}</div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm">{data.consultas} consultas</span>
                            <span className="text-xs text-muted-foreground">{data.tokens} tokens</span>
                          </div>
                          <Progress value={(data.consultas / 25) * 100} className="h-2" />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Category Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Distribución por Categoría</CardTitle>
                  <CardDescription>Tus consultas más frecuentes</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {categoryStats.map((stat) => (
                      <div key={stat.category} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">{stat.category}</span>
                          <span className="text-sm text-muted-foreground">{stat.count} consultas</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={stat.percentage} className="flex-1 h-2" />
                          <span className="text-xs text-muted-foreground w-10">{stat.percentage}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              {/* Top Queries */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="h-5 w-5" />
                    Consultas Más Frecuentes
                  </CardTitle>
                  <CardDescription>Tus preguntas más repetidas</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {topQueries.map((query, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-medium">
                          {index + 1}
                        </div>
                        <div className="flex-1 space-y-1">
                          <p className="text-sm font-medium leading-tight">{query.query}</p>
                          <div className="flex items-center gap-2">
                            <Badge variant="secondary" className="text-xs">
                              {query.category}
                            </Badge>
                            <span className="text-xs text-muted-foreground">{query.count} veces</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Performance Insights */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Insights de Rendimiento
                  </CardTitle>
                  <CardDescription>Análisis de tu actividad</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Eficiencia de consultas</span>
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                          Excelente
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Tus consultas son claras y específicas, lo que resulta en respuestas más precisas.
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Uso de tokens</span>
                        <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                          Moderado
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Estás utilizando el 72% de tus tokens mensuales. Considera optimizar tus consultas.
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Diversidad temática</span>
                        <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">Buena</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Consultas variadas en diferentes áreas legales, lo que indica un uso integral.
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Frecuencia de uso</span>
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                          Consistente
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Uso regular y constante, aprovechando bien la plataforma.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Usage Limits */}
            <Card>
              <CardHeader>
                <CardTitle>Límites de Uso</CardTitle>
                <CardDescription>Tu consumo actual vs límites del plan</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-3">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Consultas mensuales</span>
                      <span>47/100</span>
                    </div>
                    <Progress value={47} className="h-3" />
                    <p className="text-xs text-muted-foreground">53 consultas restantes</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Tokens mensuales</span>
                      <span>7.2K/10K</span>
                    </div>
                    <Progress value={72} className="h-3" />
                    <p className="text-xs text-muted-foreground">2.8K tokens restantes</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Documentos procesados</span>
                      <span>12/25</span>
                    </div>
                    <Progress value={48} className="h-3" />
                    <p className="text-xs text-muted-foreground">13 documentos restantes</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
