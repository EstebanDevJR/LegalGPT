"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { useToast } from "@/hooks/use-toast"
import {
  SettingsIcon,
  Bell,
  Shield,
  Palette,
  Globe,
  Download,
  Trash2,
  Key,
  CreditCard,
  HelpCircle,
  AlertTriangle,
} from "lucide-react"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function SettingsPage() {
  const { user, logout } = useAuth()
  const { toast } = useToast()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Settings state
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    marketing: false,
    security: true,
  })

  const [preferences, setPreferences] = useState({
    language: "es",
    timezone: "America/Bogota",
    theme: "system",
    autoSave: true,
    showConfidence: true,
    showSources: true,
  })

  const [privacy, setPrivacy] = useState({
    dataCollection: true,
    analytics: false,
    shareUsage: false,
  })

  if (!user) {
    return <AuthPage />
  }

  const handleSaveSettings = () => {
    toast({
      title: "Configuración guardada",
      description: "Tus preferencias han sido actualizadas correctamente.",
    })
  }

  const handleExportData = () => {
    toast({
      title: "Exportación iniciada",
      description: "Recibirás un email con tus datos en los próximos minutos.",
    })
  }

  const handleDeleteAccount = () => {
    toast({
      title: "Cuenta eliminada",
      description: "Tu cuenta y todos los datos han sido eliminados permanentemente.",
      variant: "destructive",
    })
    logout()
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col">
        <Header onMenuClick={() => setSidebarOpen(true)} />

        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div>
              <h1 className="text-3xl font-bold">Configuración</h1>
              <p className="text-muted-foreground">Personaliza tu experiencia en LegalGPT</p>
            </div>

            {/* Account Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <SettingsIcon className="h-5 w-5" />
                  Configuración de Cuenta
                </CardTitle>
                <CardDescription>Gestiona tu información personal y de empresa</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="displayName">Nombre para mostrar</Label>
                    <Input id="displayName" defaultValue={user.name} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Correo electrónico</Label>
                    <Input id="email" type="email" defaultValue={user.email} />
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="company">Empresa</Label>
                    <Input id="company" defaultValue={user.company} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="position">Cargo</Label>
                    <Input id="position" placeholder="Ej: Gerente General" />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Descripción de la empresa</Label>
                  <Textarea
                    id="bio"
                    placeholder="Describe brevemente tu empresa y sector..."
                    className="min-h-[100px]"
                  />
                </div>

                <Button onClick={handleSaveSettings}>Guardar cambios</Button>
              </CardContent>
            </Card>

            {/* Notifications */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notificaciones
                </CardTitle>
                <CardDescription>Configura cómo y cuándo recibir notificaciones</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Notificaciones por email</Label>
                      <p className="text-sm text-muted-foreground">Recibe actualizaciones importantes por correo</p>
                    </div>
                    <Switch
                      checked={notifications.email}
                      onCheckedChange={(checked) => setNotifications((prev) => ({ ...prev, email: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Notificaciones push</Label>
                      <p className="text-sm text-muted-foreground">
                        Recibe notificaciones en tiempo real en el navegador
                      </p>
                    </div>
                    <Switch
                      checked={notifications.push}
                      onCheckedChange={(checked) => setNotifications((prev) => ({ ...prev, push: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Emails de marketing</Label>
                      <p className="text-sm text-muted-foreground">
                        Recibe noticias, tips y actualizaciones del producto
                      </p>
                    </div>
                    <Switch
                      checked={notifications.marketing}
                      onCheckedChange={(checked) => setNotifications((prev) => ({ ...prev, marketing: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Alertas de seguridad</Label>
                      <p className="text-sm text-muted-foreground">
                        Notificaciones sobre actividad sospechosa en tu cuenta
                      </p>
                    </div>
                    <Switch
                      checked={notifications.security}
                      onCheckedChange={(checked) => setNotifications((prev) => ({ ...prev, security: checked }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Preferences */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  Preferencias de la Aplicación
                </CardTitle>
                <CardDescription>Personaliza la interfaz y comportamiento</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="language">Idioma</Label>
                    <Select
                      value={preferences.language}
                      onValueChange={(value) => setPreferences((prev) => ({ ...prev, language: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="es">Español</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timezone">Zona horaria</Label>
                    <Select
                      value={preferences.timezone}
                      onValueChange={(value) => setPreferences((prev) => ({ ...prev, timezone: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="America/Bogota">Bogotá (GMT-5)</SelectItem>
                        <SelectItem value="America/New_York">Nueva York (GMT-5)</SelectItem>
                        <SelectItem value="Europe/Madrid">Madrid (GMT+1)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Guardado automático</Label>
                      <p className="text-sm text-muted-foreground">
                        Guarda automáticamente tus consultas en el historial
                      </p>
                    </div>
                    <Switch
                      checked={preferences.autoSave}
                      onCheckedChange={(checked) => setPreferences((prev) => ({ ...prev, autoSave: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Mostrar nivel de confianza</Label>
                      <p className="text-sm text-muted-foreground">
                        Muestra el porcentaje de confianza en las respuestas
                      </p>
                    </div>
                    <Switch
                      checked={preferences.showConfidence}
                      onCheckedChange={(checked) => setPreferences((prev) => ({ ...prev, showConfidence: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Mostrar fuentes legales</Label>
                      <p className="text-sm text-muted-foreground">
                        Incluye referencias a leyes y normativas en las respuestas
                      </p>
                    </div>
                    <Switch
                      checked={preferences.showSources}
                      onCheckedChange={(checked) => setPreferences((prev) => ({ ...prev, showSources: checked }))}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Seguridad
                </CardTitle>
                <CardDescription>Protege tu cuenta y datos</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Contraseña</Label>
                      <p className="text-sm text-muted-foreground">Última actualización: hace 3 meses</p>
                    </div>
                    <Button variant="outline" className="gap-2 bg-transparent">
                      <Key className="h-4 w-4" />
                      Cambiar contraseña
                    </Button>
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Autenticación de dos factores</Label>
                      <p className="text-sm text-muted-foreground">Añade una capa extra de seguridad a tu cuenta</p>
                    </div>
                    <Badge variant="outline">No configurado</Badge>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Sesiones activas</Label>
                      <p className="text-sm text-muted-foreground">Gestiona los dispositivos con acceso a tu cuenta</p>
                    </div>
                    <Button variant="outline">Ver sesiones</Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Privacy */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Privacidad y Datos
                </CardTitle>
                <CardDescription>Controla cómo se usan tus datos</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Recopilación de datos de uso</Label>
                      <p className="text-sm text-muted-foreground">
                        Ayúdanos a mejorar el producto compartiendo datos anónimos de uso
                      </p>
                    </div>
                    <Switch
                      checked={privacy.dataCollection}
                      onCheckedChange={(checked) => setPrivacy((prev) => ({ ...prev, dataCollection: checked }))}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Analytics y métricas</Label>
                      <p className="text-sm text-muted-foreground">
                        Permite el análisis de patrones de uso para mejorar el servicio
                      </p>
                    </div>
                    <Switch
                      checked={privacy.analytics}
                      onCheckedChange={(checked) => setPrivacy((prev) => ({ ...prev, analytics: checked }))}
                    />
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label>Exportar mis datos</Label>
                      <p className="text-sm text-muted-foreground">Descarga una copia de todos tus datos</p>
                    </div>
                    <Button variant="outline" onClick={handleExportData} className="gap-2 bg-transparent">
                      <Download className="h-4 w-4" />
                      Exportar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Billing */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Facturación y Plan
                </CardTitle>
                <CardDescription>Gestiona tu suscripción y métodos de pago</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h3 className="font-semibold">Plan PyME Básico</h3>
                    <p className="text-sm text-muted-foreground">100 consultas/mes • 10K tokens • 25 documentos</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">$29.900 COP/mes</p>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">Activo</Badge>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline">Cambiar plan</Button>
                  <Button variant="outline">Métodos de pago</Button>
                  <Button variant="outline">Historial de facturación</Button>
                </div>
              </CardContent>
            </Card>

            {/* Support */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HelpCircle className="h-5 w-5" />
                  Soporte y Ayuda
                </CardTitle>
                <CardDescription>Obtén ayuda y contacta con nuestro equipo</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-2 md:grid-cols-3">
                  <Button variant="outline" className="justify-start bg-transparent">
                    Centro de ayuda
                  </Button>
                  <Button variant="outline" className="justify-start bg-transparent">
                    Contactar soporte
                  </Button>
                  <Button variant="outline" className="justify-start bg-transparent">
                    Reportar problema
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Danger Zone */}
            <Card className="border-red-200 dark:border-red-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertTriangle className="h-5 w-5" />
                  Zona de Peligro
                </CardTitle>
                <CardDescription>Acciones irreversibles para tu cuenta</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-red-200 dark:border-red-800 rounded-lg">
                  <div>
                    <h3 className="font-semibold text-red-600 dark:text-red-400">Eliminar cuenta</h3>
                    <p className="text-sm text-muted-foreground">
                      Elimina permanentemente tu cuenta y todos los datos asociados
                    </p>
                  </div>

                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive" className="gap-2">
                        <Trash2 className="h-4 w-4" />
                        Eliminar cuenta
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>¿Estás completamente seguro?</AlertDialogTitle>
                        <AlertDialogDescription>
                          Esta acción no se puede deshacer. Esto eliminará permanentemente tu cuenta y todos los datos
                          asociados de nuestros servidores.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancelar</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDeleteAccount} className="bg-red-600 hover:bg-red-700">
                          Sí, eliminar cuenta
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
