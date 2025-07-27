"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, FileText, Clock, TrendingUp, Users, Calendar, Target, Award } from "lucide-react"

const mockStats = {
  totalConsultations: 47,
  totalDocuments: 12,
  totalHours: 8.5,
  averageResponseTime: "2.3 min",
  monthlyGrowth: 23,
  favoriteCategory: "Laboral",
  consultationsByCategory: [
    { category: "Laboral", count: 18, percentage: 38 },
    { category: "Societario", count: 12, percentage: 26 },
    { category: "Tributario", count: 8, percentage: 17 },
    { category: "Contractual", count: 6, percentage: 13 },
    { category: "Propiedad Intelectual", count: 3, percentage: 6 },
  ],
  weeklyActivity: [
    { day: "Lun", consultations: 8 },
    { day: "Mar", consultations: 12 },
    { day: "Mié", consultations: 6 },
    { day: "Jue", consultations: 15 },
    { day: "Vie", consultations: 10 },
    { day: "Sáb", consultations: 3 },
    { day: "Dom", consultations: 2 },
  ],
  recentAchievements: [
    { title: "Primera consulta", description: "Completaste tu primera consulta legal", date: "2024-01-10" },
    { title: "Usuario activo", description: "10 consultas realizadas este mes", date: "2024-01-15" },
    { title: "Experto en laboral", description: "15 consultas en derecho laboral", date: "2024-01-18" },
  ],
}

export default function StatsPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex flex-1 flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            <div>
              <h1 className="text-3xl font-bold">Estadísticas</h1>
              <p className="text-muted-foreground">Analiza tu actividad y progreso en la plataforma</p>
            </div>

            {/* Métricas principales */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Consultas</CardTitle>
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mockStats.totalConsultations}</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600">+{mockStats.monthlyGrowth}%</span> vs mes anterior
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Documentos Generados</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mockStats.totalDocuments}</div>
                  <p className="text-xs text-muted-foreground">Documentos legales creados</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Tiempo Total</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mockStats.totalHours}h</div>
                  <p className="text-xs text-muted-foreground">Tiempo invertido en consultas</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Tiempo Promedio</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{mockStats.averageResponseTime}</div>
                  <p className="text-xs text-muted-foreground">Respuesta promedio por consulta</p>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Consultas por categoría */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Consultas por Categoría
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {mockStats.consultationsByCategory.map((item) => (
                    <div key={item.category} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">{item.category}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-muted-foreground">{item.count}</span>
                          <Badge variant="outline">{item.percentage}%</Badge>
                        </div>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-2">
                        <div
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Actividad semanal */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Actividad Semanal
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockStats.weeklyActivity.map((day) => (
                      <div key={day.day} className="flex items-center justify-between">
                        <span className="text-sm font-medium w-12">{day.day}</span>
                        <div className="flex-1 mx-4">
                          <div className="w-full bg-secondary rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full transition-all duration-300"
                              style={{ width: `${(day.consultations / 15) * 100}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-sm text-muted-foreground w-8 text-right">{day.consultations}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Logros recientes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="h-5 w-5" />
                  Logros Recientes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockStats.recentAchievements.map((achievement, index) => (
                    <div key={index} className="flex items-center gap-4 p-4 rounded-lg border">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                        <Award className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold">{achievement.title}</h4>
                        <p className="text-sm text-muted-foreground">{achievement.description}</p>
                      </div>
                      <div className="text-sm text-muted-foreground">{achievement.date}</div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Resumen del mes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Resumen del Mes
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{mockStats.totalConsultations}</div>
                    <p className="text-sm text-muted-foreground">Consultas realizadas</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{mockStats.favoriteCategory}</div>
                    <p className="text-sm text-muted-foreground">Categoría más consultada</p>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">{mockStats.averageResponseTime}</div>
                    <p className="text-sm text-muted-foreground">Tiempo promedio de respuesta</p>
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
