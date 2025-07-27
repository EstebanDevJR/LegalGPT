"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { User, Building, BarChart3, Clock, FileText, MessageSquare } from "lucide-react"

export default function ProfilePage() {
  const { user } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  if (!user) {
    return <AuthPage />
  }

  const stats = [
    {
      title: "Consultas realizadas",
      value: "47",
      icon: MessageSquare,
      description: "Este mes",
    },
    {
      title: "Documentos analizados",
      value: "12",
      icon: FileText,
      description: "Total",
    },
    {
      title: "Tiempo promedio",
      value: "2.3 min",
      icon: Clock,
      description: "Por consulta",
    },
    {
      title: "Precisión",
      value: "94%",
      icon: BarChart3,
      description: "Promedio",
    },
  ]

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold">Perfil</h1>
              <p className="text-muted-foreground">Gestiona tu información personal y configuración de cuenta</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {stats.map((stat, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                        <p className="text-2xl font-bold">{stat.value}</p>
                        <p className="text-xs text-muted-foreground">{stat.description}</p>
                      </div>
                      <stat.icon className="h-8 w-8 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              {/* Personal Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Información Personal
                  </CardTitle>
                  <CardDescription>Actualiza tu información personal</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nombre completo</Label>
                    <Input id="name" defaultValue={user.name} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Correo electrónico</Label>
                    <Input id="email" type="email" defaultValue={user.email} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Teléfono</Label>
                    <Input id="phone" placeholder="+57 300 123 4567" />
                  </div>

                  <Button className="w-full">Actualizar información</Button>
                </CardContent>
              </Card>

              {/* Company Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building className="h-5 w-5" />
                    Información de la Empresa
                  </CardTitle>
                  <CardDescription>Detalles de tu empresa</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="company">Nombre de la empresa</Label>
                    <Input id="company" defaultValue={user.company} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="companyType">Tipo de empresa</Label>
                    <Select defaultValue={user.companyType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="micro">Microempresa</SelectItem>
                        <SelectItem value="pequeña">Pequeña empresa</SelectItem>
                        <SelectItem value="mediana">Mediana empresa</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="nit">NIT</Label>
                    <Input id="nit" placeholder="123456789-0" />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="sector">Sector económico</Label>
                    <Input id="sector" placeholder="Ej: Comercio, Servicios, Manufactura" />
                  </div>

                  <Button className="w-full">Actualizar empresa</Button>
                </CardContent>
              </Card>
            </div>

            {/* Usage & Limits */}
            <Card>
              <CardHeader>
                <CardTitle>Uso y Límites</CardTitle>
                <CardDescription>Tu uso actual y límites del plan</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Consultas este mes</span>
                    <span>47/100</span>
                  </div>
                  <Progress value={47} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Tokens utilizados</span>
                    <span>7,250/10,000</span>
                  </div>
                  <Progress value={72.5} className="h-2" />
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Documentos procesados</span>
                    <span>12/25</span>
                  </div>
                  <Progress value={48} className="h-2" />
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <div>
                    <p className="font-medium">Plan Actual</p>
                    <p className="text-sm text-muted-foreground">PyME Básico</p>
                  </div>
                  <Badge variant="secondary">Activo</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
