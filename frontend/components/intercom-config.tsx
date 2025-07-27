"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { useIntercom } from "@/hooks/use-intercom"
import { Settings, CheckCircle, AlertCircle, ExternalLink } from "lucide-react"

export function IntercomConfig() {
  const [appId, setAppId] = useState(process.env.NEXT_PUBLIC_INTERCOM_APP_ID || "")
  const [isConfiguring, setIsConfiguring] = useState(false)
  const { isLoaded, trackEvent } = useIntercom()
  const { toast } = useToast()

  const handleSaveConfig = async () => {
    setIsConfiguring(true)

    // Simular guardado de configuración
    await new Promise((resolve) => setTimeout(resolve, 1000))

    toast({
      title: "Configuración guardada",
      description: "La configuración de Intercom ha sido actualizada correctamente.",
    })

    trackEvent("intercom_config_updated", { app_id: appId })
    setIsConfiguring(false)
  }

  const testConnection = () => {
    if (isLoaded) {
      toast({
        title: "Conexión exitosa",
        description: "Intercom está funcionando correctamente.",
      })
      trackEvent("intercom_connection_tested", { status: "success" })
    } else {
      toast({
        title: "Error de conexión",
        description: "No se pudo conectar con Intercom. Verifica la configuración.",
        variant: "destructive",
      })
      trackEvent("intercom_connection_tested", { status: "failed" })
    }
  }

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Configuración de Intercom
        </CardTitle>
        <CardDescription>Configura la integración con Intercom para chat en vivo y soporte técnico.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Estado de Conexión */}
        <div className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center gap-3">
            {isLoaded ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
            <div>
              <p className="font-medium">Estado de Conexión</p>
              <p className="text-sm text-muted-foreground">
                {isLoaded ? "Conectado y funcionando" : "Desconectado o configuración incorrecta"}
              </p>
            </div>
          </div>
          <Badge variant={isLoaded ? "default" : "destructive"}>{isLoaded ? "Activo" : "Inactivo"}</Badge>
        </div>

        {/* Configuración */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="app-id">App ID de Intercom</Label>
            <Input
              id="app-id"
              value={appId}
              onChange={(e) => setAppId(e.target.value)}
              placeholder="Ej: abc123def"
              className="mt-1"
            />
            <p className="text-xs text-muted-foreground mt-1">Encuentra tu App ID en la configuración de Intercom</p>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleSaveConfig} disabled={isConfiguring || !appId} className="flex-1">
              {isConfiguring ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Guardando...
                </>
              ) : (
                "Guardar Configuración"
              )}
            </Button>
            <Button variant="outline" onClick={testConnection} disabled={!appId}>
              Probar Conexión
            </Button>
          </div>
        </div>

        {/* Información Adicional */}
        <div className="bg-blue-50 dark:bg-blue-950/20 p-4 rounded-lg">
          <h4 className="font-medium mb-2">📋 Pasos para Configurar Intercom</h4>
          <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
            <li>
              Crea una cuenta en{" "}
              <a
                href="https://intercom.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Intercom <ExternalLink className="h-3 w-3 inline" />
              </a>
            </li>
            <li>Ve a Settings → Installation en tu dashboard de Intercom</li>
            <li>Copia tu App ID (aparece en el código de instalación)</li>
            <li>Pégalo en el campo de arriba y guarda la configuración</li>
            <li>¡El chat en vivo estará disponible inmediatamente!</li>
          </ol>
        </div>

        {/* Características Incluidas */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3 border rounded-lg">
            <h5 className="font-medium mb-2">✅ Características Incluidas</h5>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Chat en vivo en tiempo real</li>
              <li>• Historial de conversaciones</li>
              <li>• Notificaciones de mensajes</li>
              <li>• Información del usuario automática</li>
            </ul>
          </div>
          <div className="p-3 border rounded-lg">
            <h5 className="font-medium mb-2">📊 Datos Enviados</h5>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Nombre y email del usuario</li>
              <li>• Plan de suscripción</li>
              <li>• Fecha de registro</li>
              <li>• Eventos de uso de la plataforma</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
