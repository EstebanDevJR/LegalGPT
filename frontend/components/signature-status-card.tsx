"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { CheckCircle, Clock, AlertTriangle, Users, Download, Eye, Send } from "lucide-react"

interface SignatureStatusCardProps {
  document: {
    id: string
    title: string
    status: "draft" | "sent" | "partially_signed" | "completed" | "expired"
    signatories: Array<{
      name: string
      email: string
      status: "pending" | "signed" | "declined"
      signedAt?: string
    }>
    createdAt: string
    expiresAt?: string
  }
  onViewDocument: () => void
  onDownload: () => void
  onResend?: () => void
}

export function SignatureStatusCard({ document, onViewDocument, onDownload, onResend }: SignatureStatusCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "partially_signed":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
      case "sent":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "expired":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4" />
      case "partially_signed":
        return <Clock className="h-4 w-4" />
      case "sent":
        return <Clock className="h-4 w-4" />
      case "expired":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "Completado"
      case "partially_signed":
        return "Parcialmente Firmado"
      case "sent":
        return "Enviado"
      case "expired":
        return "Expirado"
      default:
        return "Borrador"
    }
  }

  const signedCount = document.signatories.filter((s) => s.status === "signed").length
  const totalCount = document.signatories.length
  const progress = totalCount > 0 ? (signedCount / totalCount) * 100 : 0

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{document.title}</CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <Users className="h-4 w-4" />
              {totalCount} firmante{totalCount !== 1 ? "s" : ""}
            </CardDescription>
          </div>
          <Badge className={getStatusColor(document.status)}>
            {getStatusIcon(document.status)}
            <span className="ml-1">{getStatusText(document.status)}</span>
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progreso de firmas</span>
            <span>
              {signedCount}/{totalCount}
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Signatories Status */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Estado de firmantes:</h4>
          <div className="space-y-1">
            {document.signatories.map((signatory, index) => (
              <div key={index} className="flex items-center justify-between text-sm">
                <span className="truncate">{signatory.name}</span>
                <Badge
                  variant="outline"
                  className={
                    signatory.status === "signed"
                      ? "bg-green-50 text-green-700 border-green-200"
                      : signatory.status === "declined"
                        ? "bg-red-50 text-red-700 border-red-200"
                        : "bg-yellow-50 text-yellow-700 border-yellow-200"
                  }
                >
                  {signatory.status === "signed" && <CheckCircle className="h-3 w-3 mr-1" />}
                  {signatory.status === "pending" && <Clock className="h-3 w-3 mr-1" />}
                  {signatory.status === "declined" && <AlertTriangle className="h-3 w-3 mr-1" />}
                  {signatory.status === "signed"
                    ? "Firmado"
                    : signatory.status === "declined"
                      ? "Rechazado"
                      : "Pendiente"}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Dates */}
        <div className="text-xs text-muted-foreground space-y-1">
          <div>Creado: {new Date(document.createdAt).toLocaleDateString("es-CO")}</div>
          {document.expiresAt && <div>Expira: {new Date(document.expiresAt).toLocaleDateString("es-CO")}</div>}
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button variant="outline" size="sm" onClick={onViewDocument} className="gap-1 bg-transparent">
            <Eye className="h-3 w-3" />
            Ver
          </Button>

          {document.status === "completed" && (
            <Button variant="outline" size="sm" onClick={onDownload} className="gap-1 bg-transparent">
              <Download className="h-3 w-3" />
              Descargar
            </Button>
          )}

          {(document.status === "sent" || document.status === "partially_signed") && onResend && (
            <Button variant="outline" size="sm" onClick={onResend} className="gap-1 bg-transparent">
              <Send className="h-3 w-3" />
              Reenviar
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
