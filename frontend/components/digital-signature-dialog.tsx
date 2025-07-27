"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import {
  PenTool,
  Shield,
  CheckCircle,
  Clock,
  User,
  Mail,
  Phone,
  Download,
  Eye,
  AlertTriangle,
  Trash2,
  Plus,
  Send,
} from "lucide-react"
import SignatureCanvas from "react-signature-canvas"

interface Signatory {
  id: string
  name: string
  email: string
  phone?: string
  role: string
  status: "pending" | "signed" | "declined"
  signedAt?: string
  signature?: string
  ipAddress?: string
  location?: string
}

interface DigitalSignatureDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  document: string
  documentTitle: string
  onDocumentSigned: (signedDocument: any) => void
}

export function DigitalSignatureDialog({
  open,
  onOpenChange,
  document,
  documentTitle,
  onDocumentSigned,
}: DigitalSignatureDialogProps) {
  const { toast } = useToast()
  const signatureRef = useRef<SignatureCanvas>(null)
  const [activeTab, setActiveTab] = useState("signatories")
  const [isProcessing, setIsProcessing] = useState(false)

  // Signature data
  const [signatories, setSignatories] = useState<Signatory[]>([
    {
      id: "1",
      name: "Juan Pérez",
      email: "juan@empresa.com",
      phone: "+57 300 123 4567",
      role: "Empleador",
      status: "pending",
    },
  ])

  const [newSignatory, setNewSignatory] = useState({
    name: "",
    email: "",
    phone: "",
    role: "",
  })

  const [currentUserSignature, setCurrentUserSignature] = useState<string | null>(null)
  const [signatureMethod, setSignatureMethod] = useState<"draw" | "upload" | "type">("draw")
  const [typedSignature, setTypedSignature] = useState("")
  const [uploadedSignature, setUploadedSignature] = useState<string | null>(null)

  // Document signing process
  const [signingStep, setSigningStep] = useState<"setup" | "signing" | "completed">("setup")
  const [signedDocument, setSignedDocument] = useState<any>(null)

  const addSignatory = () => {
    if (!newSignatory.name || !newSignatory.email) {
      toast({
        title: "Campos requeridos",
        description: "Nombre y email son obligatorios",
        variant: "destructive",
      })
      return
    }

    const signatory: Signatory = {
      id: Date.now().toString(),
      ...newSignatory,
      status: "pending",
    }

    setSignatories([...signatories, signatory])
    setNewSignatory({ name: "", email: "", phone: "", role: "" })

    toast({
      title: "Firmante añadido",
      description: `${newSignatory.name} ha sido añadido a la lista de firmantes`,
    })
  }

  const removeSignatory = (id: string) => {
    setSignatories(signatories.filter((s) => s.id !== id))
    toast({
      title: "Firmante eliminado",
      description: "El firmante ha sido removido de la lista",
    })
  }

  const clearSignature = () => {
    if (signatureRef.current) {
      signatureRef.current.clear()
    }
    setCurrentUserSignature(null)
  }

  const saveSignature = () => {
    if (signatureMethod === "draw" && signatureRef.current) {
      if (signatureRef.current.isEmpty()) {
        toast({
          title: "Firma requerida",
          description: "Por favor dibuja tu firma",
          variant: "destructive",
        })
        return
      }
      setCurrentUserSignature(signatureRef.current.toDataURL())
    } else if (signatureMethod === "type" && typedSignature) {
      // Generate typed signature as canvas
      const canvas = document.createElement("canvas")
      const ctx = canvas.getContext("2d")
      if (ctx) {
        canvas.width = 400
        canvas.height = 100
        ctx.font = "30px cursive"
        ctx.fillStyle = "#000"
        ctx.fillText(typedSignature, 20, 60)
        setCurrentUserSignature(canvas.toDataURL())
      }
    } else if (signatureMethod === "upload" && uploadedSignature) {
      setCurrentUserSignature(uploadedSignature)
    }

    toast({
      title: "Firma guardada",
      description: "Tu firma ha sido guardada correctamente",
    })
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedSignature(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const sendForSignature = async () => {
    setIsProcessing(true)

    // Simulate sending emails to signatories
    await new Promise((resolve) => setTimeout(resolve, 2000))

    toast({
      title: "Invitaciones enviadas",
      description: `Se han enviado ${signatories.length} invitaciones para firmar el documento`,
    })

    setSigningStep("signing")
    setIsProcessing(false)
  }

  const signDocument = async () => {
    if (!currentUserSignature) {
      toast({
        title: "Firma requerida",
        description: "Por favor añade tu firma antes de continuar",
        variant: "destructive",
      })
      return
    }

    setIsProcessing(true)

    // Simulate document signing process
    await new Promise((resolve) => setTimeout(resolve, 3000))

    const signedDoc = {
      id: Date.now().toString(),
      originalDocument: document,
      title: documentTitle,
      signatures: [
        {
          signatory: "Usuario Actual",
          signature: currentUserSignature,
          timestamp: new Date().toISOString(),
          ipAddress: "192.168.1.1",
          location: "Bogotá, Colombia",
          verified: true,
        },
      ],
      status: "partially_signed",
      createdAt: new Date().toISOString(),
      certificateHash: "SHA256:a1b2c3d4e5f6...",
    }

    setSignedDocument(signedDoc)
    setSigningStep("completed")
    setIsProcessing(false)

    toast({
      title: "Documento firmado",
      description: "Tu firma ha sido añadida al documento exitosamente",
    })
  }

  const downloadSignedDocument = () => {
    if (!signedDocument) return

    const documentContent = `
${signedDocument.originalDocument}

═══════════════════════════════════════════════════════════════
FIRMAS DIGITALES
═══════════════════════════════════════════════════════════════

${signedDocument.signatures
  .map(
    (sig: any) => `
Firmante: ${sig.signatory}
Fecha y hora: ${new Date(sig.timestamp).toLocaleString("es-CO")}
Dirección IP: ${sig.ipAddress}
Ubicación: ${sig.location}
Estado: ${sig.verified ? "✓ Verificada" : "⚠ Pendiente de verificación"}
Hash de certificado: ${signedDocument.certificateHash}

[FIRMA DIGITAL ADJUNTA]
`,
  )
  .join("\n")}

═══════════════════════════════════════════════════════════════
Este documento ha sido firmado digitalmente usando LegalGPT Pro
Fecha de generación: ${new Date(signedDocument.createdAt).toLocaleString("es-CO")}
ID del documento: ${signedDocument.id}
═══════════════════════════════════════════════════════════════
    `

    const blob = new Blob([documentContent], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${documentTitle}_firmado.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Documento descargado",
      description: "El documento firmado ha sido guardado",
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "signed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "pending":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "declined":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "signed":
        return <CheckCircle className="h-4 w-4" />
      case "pending":
        return <Clock className="h-4 w-4" />
      case "declined":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <PenTool className="h-6 w-6" />
            Firma Digital del Documento
          </DialogTitle>
          <DialogDescription>
            Añade firmas digitales certificadas a tu documento para darle validez legal
          </DialogDescription>
        </DialogHeader>

        {signingStep === "setup" && (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="signatories">Firmantes</TabsTrigger>
              <TabsTrigger value="preview">Vista Previa</TabsTrigger>
              <TabsTrigger value="settings">Configuración</TabsTrigger>
            </TabsList>

            <TabsContent value="signatories" className="space-y-6">
              {/* Add Signatory */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Plus className="h-5 w-5" />
                    Añadir Firmante
                  </CardTitle>
                  <CardDescription>Agrega las personas que deben firmar este documento</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Nombre completo *</Label>
                      <Input
                        id="name"
                        placeholder="Ej: Juan Pérez"
                        value={newSignatory.name}
                        onChange={(e) => setNewSignatory({ ...newSignatory, name: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email *</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="juan@empresa.com"
                        value={newSignatory.email}
                        onChange={(e) => setNewSignatory({ ...newSignatory, email: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="phone">Teléfono</Label>
                      <Input
                        id="phone"
                        placeholder="+57 300 123 4567"
                        value={newSignatory.phone}
                        onChange={(e) => setNewSignatory({ ...newSignatory, phone: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="role">Rol en el documento</Label>
                      <Input
                        id="role"
                        placeholder="Ej: Empleador, Contratista"
                        value={newSignatory.role}
                        onChange={(e) => setNewSignatory({ ...newSignatory, role: e.target.value })}
                      />
                    </div>
                  </div>
                  <Button onClick={addSignatory} className="gap-2">
                    <Plus className="h-4 w-4" />
                    Añadir Firmante
                  </Button>
                </CardContent>
              </Card>

              {/* Signatories List */}
              <Card>
                <CardHeader>
                  <CardTitle>Lista de Firmantes ({signatories.length})</CardTitle>
                  <CardDescription>Personas que firmarán este documento</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {signatories.map((signatory) => (
                      <div key={signatory.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                            <User className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <h4 className="font-semibold">{signatory.name}</h4>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <Mail className="h-3 w-3" />
                                {signatory.email}
                              </span>
                              {signatory.phone && (
                                <span className="flex items-center gap-1">
                                  <Phone className="h-3 w-3" />
                                  {signatory.phone}
                                </span>
                              )}
                              {signatory.role && <span>• {signatory.role}</span>}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge className={getStatusColor(signatory.status)}>
                            {getStatusIcon(signatory.status)}
                            <span className="ml-1 capitalize">{signatory.status}</span>
                          </Badge>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeSignatory(signatory.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}

                    {signatories.length === 0 && (
                      <div className="text-center py-8 text-muted-foreground">
                        <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
                        <p>No hay firmantes añadidos</p>
                        <p className="text-sm">Añade al menos un firmante para continuar</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="preview" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5" />
                    Vista Previa del Documento
                  </CardTitle>
                  <CardDescription>Revisa el documento antes de enviarlo para firma</CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] w-full border rounded-lg p-4">
                    <pre className="text-sm whitespace-pre-wrap leading-relaxed">{document}</pre>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="settings" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Configuración de Seguridad
                  </CardTitle>
                  <CardDescription>Opciones de seguridad y validación para las firmas</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4">
                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-semibold">Verificación por email</h4>
                        <p className="text-sm text-muted-foreground">
                          Los firmantes deben verificar su email antes de firmar
                        </p>
                      </div>
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        Activado
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-semibold">Registro de IP y ubicación</h4>
                        <p className="text-sm text-muted-foreground">
                          Se registra la IP y ubicación de cada firma para auditoría
                        </p>
                      </div>
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        Activado
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-semibold">Certificado digital</h4>
                        <p className="text-sm text-muted-foreground">Cada firma incluye un certificado digital único</p>
                      </div>
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        Activado
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-semibold">Orden de firma</h4>
                        <p className="text-sm text-muted-foreground">Los firmantes deben firmar en orden específico</p>
                      </div>
                      <Badge variant="outline">Opcional</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}

        {signingStep === "signing" && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PenTool className="h-5 w-5" />
                  Tu Firma Digital
                </CardTitle>
                <CardDescription>Crea tu firma digital para este documento</CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={signatureMethod} onValueChange={(value) => setSignatureMethod(value as any)}>
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="draw">Dibujar</TabsTrigger>
                    <TabsTrigger value="type">Escribir</TabsTrigger>
                    <TabsTrigger value="upload">Subir</TabsTrigger>
                  </TabsList>

                  <TabsContent value="draw" className="space-y-4">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                      <SignatureCanvas
                        ref={signatureRef}
                        canvasProps={{
                          width: 500,
                          height: 200,
                          className: "signature-canvas w-full",
                          style: { border: "1px solid #ccc" },
                        }}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={clearSignature} variant="outline">
                        Limpiar
                      </Button>
                      <Button onClick={saveSignature}>Guardar Firma</Button>
                    </div>
                  </TabsContent>

                  <TabsContent value="type" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="typed-signature">Escribe tu nombre</Label>
                      <Input
                        id="typed-signature"
                        placeholder="Tu nombre completo"
                        value={typedSignature}
                        onChange={(e) => setTypedSignature(e.target.value)}
                        className="text-2xl font-cursive"
                        style={{ fontFamily: "cursive" }}
                      />
                    </div>
                    {typedSignature && (
                      <div className="p-4 border rounded-lg bg-gray-50 dark:bg-gray-900">
                        <p className="text-sm text-muted-foreground mb-2">Vista previa:</p>
                        <div
                          className="text-3xl"
                          style={{ fontFamily: "cursive", color: "#000", backgroundColor: "#fff", padding: "10px" }}
                        >
                          {typedSignature}
                        </div>
                      </div>
                    )}
                    <Button onClick={saveSignature} disabled={!typedSignature}>
                      Guardar Firma
                    </Button>
                  </TabsContent>

                  <TabsContent value="upload" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="signature-upload">Subir imagen de firma</Label>
                      <Input id="signature-upload" type="file" accept="image/*" onChange={handleFileUpload} />
                      <p className="text-xs text-muted-foreground">
                        Formatos soportados: PNG, JPG, GIF. Tamaño máximo: 2MB
                      </p>
                    </div>
                    {uploadedSignature && (
                      <div className="p-4 border rounded-lg">
                        <p className="text-sm text-muted-foreground mb-2">Vista previa:</p>
                        <img
                          src={uploadedSignature || "/placeholder.svg"}
                          alt="Firma subida"
                          className="max-h-32 border"
                        />
                      </div>
                    )}
                    <Button onClick={saveSignature} disabled={!uploadedSignature}>
                      Guardar Firma
                    </Button>
                  </TabsContent>
                </Tabs>

                {currentUserSignature && (
                  <div className="mt-6 p-4 border rounded-lg bg-green-50 dark:bg-green-900/20">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium text-green-600">Firma guardada</span>
                    </div>
                    <img src={currentUserSignature || "/placeholder.svg"} alt="Tu firma" className="max-h-20 border" />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Document Preview for Signing */}
            <Card>
              <CardHeader>
                <CardTitle>Documento a Firmar</CardTitle>
                <CardDescription>Revisa el documento antes de añadir tu firma</CardDescription>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px] w-full border rounded-lg p-4">
                  <pre className="text-sm whitespace-pre-wrap leading-relaxed">{document}</pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        )}

        {signingStep === "completed" && signedDocument && (
          <div className="space-y-6">
            <Card className="border-green-200 dark:border-green-800">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                    <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
                      ¡Documento Firmado Exitosamente!
                    </h3>
                    <p className="text-muted-foreground">
                      Tu firma digital ha sido añadida y el documento está listo para descargar
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Signature Details */}
            <Card>
              <CardHeader>
                <CardTitle>Detalles de la Firma</CardTitle>
                <CardDescription>Información de verificación y certificación</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {signedDocument.signatures.map((sig: any, index: number) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <h4 className="font-semibold">{sig.signatory}</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground">
                          <span>Fecha: {new Date(sig.timestamp).toLocaleString("es-CO")}</span>
                          <span>IP: {sig.ipAddress}</span>
                          <span>Ubicación: {sig.location}</span>
                          <span>Hash: {signedDocument.certificateHash}</span>
                        </div>
                      </div>
                      <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Verificada
                      </Badge>
                    </div>
                    <Separator className="my-3" />
                    <div>
                      <p className="text-xs text-muted-foreground mb-2">Firma digital:</p>
                      <img src={sig.signature || "/placeholder.svg"} alt="Firma" className="max-h-16 border" />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Pending Signatures */}
            {signatories.length > 1 && (
              <Card>
                <CardHeader>
                  <CardTitle>Estado de Otras Firmas</CardTitle>
                  <CardDescription>Progreso de firma de otros participantes</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {signatories.slice(1).map((signatory) => (
                      <div key={signatory.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <User className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{signatory.name}</p>
                            <p className="text-sm text-muted-foreground">{signatory.email}</p>
                          </div>
                        </div>
                        <Badge className={getStatusColor(signatory.status)}>
                          {getStatusIcon(signatory.status)}
                          <span className="ml-1">Pendiente</span>
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        <DialogFooter className="flex gap-2">
          {signingStep === "setup" && (
            <>
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancelar
              </Button>
              <Button onClick={sendForSignature} disabled={signatories.length === 0 || isProcessing} className="gap-2">
                <Send className="h-4 w-4" />
                {isProcessing ? "Enviando..." : "Enviar para Firma"}
              </Button>
            </>
          )}

          {signingStep === "signing" && (
            <>
              <Button variant="outline" onClick={() => setSigningStep("setup")}>
                Volver
              </Button>
              <Button onClick={signDocument} disabled={!currentUserSignature || isProcessing} className="gap-2">
                <PenTool className="h-4 w-4" />
                {isProcessing ? "Firmando..." : "Firmar Documento"}
              </Button>
            </>
          )}

          {signingStep === "completed" && (
            <>
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cerrar
              </Button>
              <Button onClick={downloadSignedDocument} className="gap-2">
                <Download className="h-4 w-4" />
                Descargar Documento Firmado
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
