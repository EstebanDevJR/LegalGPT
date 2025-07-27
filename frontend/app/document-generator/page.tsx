"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { useToast } from "@/hooks/use-toast"
import {
  FileText,
  Crown,
  Sparkles,
  Download,
  Eye,
  Save,
  Wand2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Shield,
  PenTool,
} from "lucide-react"
import { PlanUpgradeDialog } from "@/components/plan-upgrade-dialog"
import { DocumentPreviewDialog } from "@/components/document-preview-dialog"
import { LoadingSpinner } from "@/components/loading-spinner"
import { DigitalSignatureDialog } from "@/components/digital-signature-dialog"

interface DocumentTemplate {
  id: string
  name: string
  description: string
  category: string
  complexity: "Básico" | "Intermedio" | "Avanzado"
  estimatedTime: string
  requiredPlan: "básico" | "profesional" | "empresarial"
  fields: DocumentField[]
  preview: string
}

interface DocumentField {
  id: string
  name: string
  label: string
  type: "text" | "textarea" | "select" | "date" | "number"
  required: boolean
  placeholder?: string
  options?: string[]
  description?: string
}

const documentTemplates: DocumentTemplate[] = [
  {
    id: "contrato-trabajo",
    name: "Contrato de Trabajo",
    description: "Contrato laboral completo con todas las cláusulas legales requeridas",
    category: "Laboral",
    complexity: "Intermedio",
    estimatedTime: "15-20 min",
    requiredPlan: "profesional",
    fields: [
      { id: "empleador", name: "empleador", label: "Nombre del Empleador", type: "text", required: true },
      { id: "empleado", name: "empleado", label: "Nombre del Empleado", type: "text", required: true },
      { id: "cargo", name: "cargo", label: "Cargo", type: "text", required: true },
      { id: "salario", name: "salario", label: "Salario Mensual", type: "number", required: true },
      {
        id: "tipoContrato",
        name: "tipoContrato",
        label: "Tipo de Contrato",
        type: "select",
        required: true,
        options: ["Indefinido", "Fijo", "Por obra o labor"],
      },
      { id: "fechaInicio", name: "fechaInicio", label: "Fecha de Inicio", type: "date", required: true },
      {
        id: "funciones",
        name: "funciones",
        label: "Funciones del Cargo",
        type: "textarea",
        required: true,
        placeholder: "Describe las principales funciones...",
      },
    ],
    preview: "Contrato de trabajo entre {{empleador}} y {{empleado}} para el cargo de {{cargo}}...",
  },
  {
    id: "acta-constitucion",
    name: "Acta de Constitución SAS",
    description: "Documento de constitución para Sociedad por Acciones Simplificada",
    category: "Constitución Empresarial",
    complexity: "Avanzado",
    estimatedTime: "30-45 min",
    requiredPlan: "empresarial",
    fields: [
      { id: "nombreSociedad", name: "nombreSociedad", label: "Nombre de la Sociedad", type: "text", required: true },
      { id: "domicilio", name: "domicilio", label: "Domicilio Principal", type: "text", required: true },
      { id: "objetoSocial", name: "objetoSocial", label: "Objeto Social", type: "textarea", required: true },
      {
        id: "capitalAutorizado",
        name: "capitalAutorizado",
        label: "Capital Autorizado",
        type: "number",
        required: true,
      },
      {
        id: "representanteLegal",
        name: "representanteLegal",
        label: "Representante Legal",
        type: "text",
        required: true,
      },
      { id: "cedula", name: "cedula", label: "Cédula del Representante", type: "text", required: true },
    ],
    preview: "Acta de constitución de {{nombreSociedad}} con domicilio en {{domicilio}}...",
  },
  {
    id: "politica-privacidad",
    name: "Política de Privacidad",
    description: "Política de tratamiento de datos personales conforme a la ley colombiana",
    category: "Protección de Datos",
    complexity: "Intermedio",
    estimatedTime: "20-25 min",
    requiredPlan: "profesional",
    fields: [
      { id: "empresa", name: "empresa", label: "Nombre de la Empresa", type: "text", required: true },
      { id: "nit", name: "nit", label: "NIT", type: "text", required: true },
      { id: "direccion", name: "direccion", label: "Dirección", type: "text", required: true },
      { id: "email", name: "email", label: "Email de Contacto", type: "text", required: true },
      { id: "telefono", name: "telefono", label: "Teléfono", type: "text", required: true },
      {
        id: "tiposDatos",
        name: "tiposDatos",
        label: "Tipos de Datos que Recolecta",
        type: "textarea",
        required: true,
        placeholder: "Ej: nombres, emails, teléfonos...",
      },
    ],
    preview: "Política de privacidad de {{empresa}} para el tratamiento de datos personales...",
  },
  {
    id: "contrato-prestacion",
    name: "Contrato de Prestación de Servicios",
    description: "Contrato para servicios profesionales independientes",
    category: "Comercial",
    complexity: "Básico",
    estimatedTime: "10-15 min",
    requiredPlan: "básico",
    fields: [
      { id: "contratante", name: "contratante", label: "Nombre del Contratante", type: "text", required: true },
      { id: "contratista", name: "contratista", label: "Nombre del Contratista", type: "text", required: true },
      { id: "servicios", name: "servicios", label: "Descripción de Servicios", type: "textarea", required: true },
      { id: "valor", name: "valor", label: "Valor del Contrato", type: "number", required: true },
      { id: "plazo", name: "plazo", label: "Plazo de Ejecución", type: "text", required: true },
      { id: "formaPago", name: "formaPago", label: "Forma de Pago", type: "textarea", required: true },
    ],
    preview: "Contrato de prestación de servicios entre {{contratante}} y {{contratista}}...",
  },
]

// Mock user plan - en producción vendría del contexto de auth
const mockUserPlan = "básico" // "básico" | "profesional" | "empresarial"

export default function DocumentGeneratorPage() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedDocument, setGeneratedDocument] = useState<string | null>(null)
  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false)
  const [showPreviewDialog, setShowPreviewDialog] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [showSignatureDialog, setShowSignatureDialog] = useState(false)

  if (!user) {
    return <AuthPage />
  }

  const userPlan = mockUserPlan

  const canAccessTemplate = (template: DocumentTemplate) => {
    const planHierarchy = { básico: 1, profesional: 2, empresarial: 3 }
    return planHierarchy[userPlan] >= planHierarchy[template.requiredPlan]
  }

  const getAvailableTemplates = () => {
    return documentTemplates.filter((template) => canAccessTemplate(template))
  }

  const getLockedTemplates = () => {
    return documentTemplates.filter((template) => !canAccessTemplate(template))
  }

  const handleTemplateSelect = (template: DocumentTemplate) => {
    if (!canAccessTemplate(template)) {
      setShowUpgradeDialog(true)
      return
    }
    setSelectedTemplate(template)
    setFormData({})
    setGeneratedDocument(null)
  }

  const handleFieldChange = (fieldName: string, value: string) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }))
  }

  const handleGenerateDocument = async () => {
    if (!selectedTemplate) return

    // Validate required fields
    const missingFields = selectedTemplate.fields
      .filter((field) => field.required && !formData[field.name]?.trim())
      .map((field) => field.label)

    if (missingFields.length > 0) {
      toast({
        title: "Campos requeridos",
        description: `Por favor completa: ${missingFields.join(", ")}`,
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    setGenerationProgress(0)

    // Simulate document generation with progress
    const progressInterval = setInterval(() => {
      setGenerationProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    // Simulate API call
    setTimeout(() => {
      clearInterval(progressInterval)
      setGenerationProgress(100)

      // Generate mock document
      let document = selectedTemplate.preview
      selectedTemplate.fields.forEach((field) => {
        const value = formData[field.name] || `[${field.label}]`
        document = document.replace(new RegExp(`\\{\\{${field.name}\\}\\}`, "g"), value)
      })

      const fullDocument = `
# ${selectedTemplate.name}

${document}

## Cláusulas Generales

Este documento ha sido generado automáticamente por LegalGPT y cumple con la legislación colombiana vigente.

**Fecha de generación:** ${new Date().toLocaleDateString("es-CO")}
**Generado por:** LegalGPT Pro

---

*Este documento es una plantilla base. Se recomienda revisión legal antes de su uso.*
      `

      setGeneratedDocument(fullDocument)
      setIsGenerating(false)
      setGenerationProgress(0)

      toast({
        title: "Documento generado",
        description: "Tu documento ha sido creado exitosamente",
      })
    }, 3000)
  }

  const handleDownloadDocument = () => {
    if (!generatedDocument || !selectedTemplate) return

    const blob = new Blob([generatedDocument], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${selectedTemplate.name.replace(/\s+/g, "_")}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Documento descargado",
      description: "El archivo ha sido guardado en tu dispositivo",
    })
  }

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case "básico":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
      case "profesional":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
      case "empresarial":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "Básico":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "Intermedio":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300"
      case "Avanzado":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300"
    }
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
                <h1 className="text-3xl font-bold flex items-center gap-2">
                  <FileText className="h-8 w-8" />
                  Generador de Documentos
                  <Crown className="h-6 w-6 text-yellow-500" />
                </h1>
                <p className="text-muted-foreground">
                  Crea documentos legales profesionales con IA - Exclusivo para planes pagados
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge className={getPlanBadgeColor(userPlan)}>Plan {userPlan}</Badge>
                {userPlan === "básico" && (
                  <Button onClick={() => setShowUpgradeDialog(true)} className="gap-2">
                    <Crown className="h-4 w-4" />
                    Mejorar Plan
                  </Button>
                )}
              </div>
            </div>

            {/* Plan Benefits */}
            <Card className="border-primary/20 bg-primary/5">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Sparkles className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-2">Funcionalidad Premium</h3>
                    <p className="text-muted-foreground mb-4">
                      El generador de documentos utiliza IA avanzada para crear documentos legales personalizados y
                      conformes a la legislación colombiana.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm">Documentos personalizados</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-green-600" />
                        <span className="text-sm">Cumplimiento legal</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-green-600" />
                        <span className="text-sm">Generación instantánea</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid gap-6 lg:grid-cols-3">
              {/* Template Selection */}
              <div className="lg:col-span-1 space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Plantillas Disponibles</CardTitle>
                    <CardDescription>Selecciona el tipo de documento que deseas crear</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {getAvailableTemplates().map((template) => (
                      <Card
                        key={template.id}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          selectedTemplate?.id === template.id ? "ring-2 ring-primary" : ""
                        }`}
                        onClick={() => handleTemplateSelect(template)}
                      >
                        <CardContent className="p-4">
                          <div className="space-y-2">
                            <div className="flex items-start justify-between">
                              <h4 className="font-semibold text-sm">{template.name}</h4>
                              <Badge className={getPlanBadgeColor(template.requiredPlan)} variant="outline">
                                {template.requiredPlan}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground line-clamp-2">{template.description}</p>
                            <div className="flex items-center justify-between">
                              <Badge className={getComplexityColor(template.complexity)} variant="outline">
                                {template.complexity}
                              </Badge>
                              <span className="text-xs text-muted-foreground flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {template.estimatedTime}
                              </span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </CardContent>
                </Card>

                {/* Locked Templates */}
                {getLockedTemplates().length > 0 && (
                  <Card className="border-orange-200 dark:border-orange-800">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-orange-600 dark:text-orange-400">
                        <Crown className="h-5 w-5" />
                        Plantillas Premium
                      </CardTitle>
                      <CardDescription>Mejora tu plan para acceder a estas plantillas</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {getLockedTemplates().map((template) => (
                        <Card
                          key={template.id}
                          className="cursor-pointer opacity-60 hover:opacity-80 transition-opacity"
                          onClick={() => setShowUpgradeDialog(true)}
                        >
                          <CardContent className="p-4">
                            <div className="space-y-2">
                              <div className="flex items-start justify-between">
                                <h4 className="font-semibold text-sm flex items-center gap-2">
                                  {template.name}
                                  <Crown className="h-3 w-3 text-yellow-500" />
                                </h4>
                                <Badge className={getPlanBadgeColor(template.requiredPlan)} variant="outline">
                                  {template.requiredPlan}
                                </Badge>
                              </div>
                              <p className="text-xs text-muted-foreground line-clamp-2">{template.description}</p>
                              <div className="flex items-center justify-between">
                                <Badge className={getComplexityColor(template.complexity)} variant="outline">
                                  {template.complexity}
                                </Badge>
                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  {template.estimatedTime}
                                </span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Document Form */}
              <div className="lg:col-span-2">
                {!selectedTemplate ? (
                  <Card>
                    <CardContent className="flex flex-col items-center justify-center py-12">
                      <FileText className="h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">Selecciona una Plantilla</h3>
                      <p className="text-muted-foreground text-center">
                        Elige el tipo de documento que deseas crear para comenzar
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-6">
                    {/* Template Info */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <FileText className="h-5 w-5" />
                          {selectedTemplate.name}
                        </CardTitle>
                        <CardDescription>{selectedTemplate.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          <Badge variant="secondary">{selectedTemplate.category}</Badge>
                          <Badge className={getComplexityColor(selectedTemplate.complexity)}>
                            {selectedTemplate.complexity}
                          </Badge>
                          <Badge variant="outline" className="gap-1">
                            <Clock className="h-3 w-3" />
                            {selectedTemplate.estimatedTime}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Form Fields */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Información del Documento</CardTitle>
                        <CardDescription>Completa los campos para personalizar tu documento</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {selectedTemplate.fields.map((field) => (
                          <div key={field.id} className="space-y-2">
                            <Label htmlFor={field.id} className="flex items-center gap-1">
                              {field.label}
                              {field.required && <span className="text-red-500">*</span>}
                            </Label>
                            {field.description && <p className="text-xs text-muted-foreground">{field.description}</p>}

                            {field.type === "text" && (
                              <Input
                                id={field.id}
                                placeholder={field.placeholder}
                                value={formData[field.name] || ""}
                                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                                required={field.required}
                              />
                            )}

                            {field.type === "textarea" && (
                              <Textarea
                                id={field.id}
                                placeholder={field.placeholder}
                                value={formData[field.name] || ""}
                                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                                required={field.required}
                                className="min-h-[100px]"
                              />
                            )}

                            {field.type === "select" && (
                              <Select
                                value={formData[field.name] || ""}
                                onValueChange={(value) => handleFieldChange(field.name, value)}
                              >
                                <SelectTrigger>
                                  <SelectValue placeholder={`Selecciona ${field.label.toLowerCase()}`} />
                                </SelectTrigger>
                                <SelectContent>
                                  {field.options?.map((option) => (
                                    <SelectItem key={option} value={option}>
                                      {option}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            )}

                            {field.type === "date" && (
                              <Input
                                id={field.id}
                                type="date"
                                value={formData[field.name] || ""}
                                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                                required={field.required}
                              />
                            )}

                            {field.type === "number" && (
                              <Input
                                id={field.id}
                                type="number"
                                placeholder={field.placeholder}
                                value={formData[field.name] || ""}
                                onChange={(e) => handleFieldChange(field.name, e.target.value)}
                                required={field.required}
                              />
                            )}
                          </div>
                        ))}
                      </CardContent>
                    </Card>

                    {/* Generation Progress */}
                    {isGenerating && (
                      <Card>
                        <CardContent className="p-6">
                          <div className="space-y-4">
                            <div className="flex items-center gap-2">
                              <LoadingSpinner size="sm" />
                              <span className="text-sm font-medium">Generando documento...</span>
                            </div>
                            <Progress value={generationProgress} className="h-2" />
                            <p className="text-xs text-muted-foreground">
                              Procesando información y aplicando plantillas legales
                            </p>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Generated Document */}
                    {generatedDocument && (
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2">
                            <CheckCircle className="h-5 w-5 text-green-600" />
                            Documento Generado
                          </CardTitle>
                          <CardDescription>Tu documento ha sido creado exitosamente</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="bg-muted p-4 rounded-lg max-h-60 overflow-y-auto">
                            <pre className="text-sm whitespace-pre-wrap">{generatedDocument.substring(0, 500)}...</pre>
                          </div>
                          <div className="flex gap-2">
                            <Button onClick={() => setShowPreviewDialog(true)} variant="outline" className="gap-2">
                              <Eye className="h-4 w-4" />
                              Vista Completa
                            </Button>
                            <Button onClick={handleDownloadDocument} className="gap-2">
                              <Download className="h-4 w-4" />
                              Descargar
                            </Button>
                            <Button
                              onClick={() => setShowSignatureDialog(true)}
                              variant="outline"
                              className="gap-2 bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/20"
                            >
                              <PenTool className="h-4 w-4" />
                              Firmar Digitalmente
                            </Button>
                            <Button variant="outline" className="gap-2 bg-transparent">
                              <Save className="h-4 w-4" />
                              Guardar
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Action Buttons */}
                    {!generatedDocument && (
                      <Card>
                        <CardContent className="p-6">
                          <div className="flex justify-between items-center">
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <AlertTriangle className="h-4 w-4" />
                              Revisa todos los campos antes de generar
                            </div>
                            <Button
                              onClick={handleGenerateDocument}
                              disabled={isGenerating}
                              className="gap-2"
                              size="lg"
                            >
                              <Wand2 className="h-4 w-4" />
                              {isGenerating ? "Generando..." : "Generar Documento"}
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Dialogs */}
      <PlanUpgradeDialog open={showUpgradeDialog} onOpenChange={setShowUpgradeDialog} currentPlan={userPlan} />

      {generatedDocument && (
        <DocumentPreviewDialog
          open={showPreviewDialog}
          onOpenChange={setShowPreviewDialog}
          document={generatedDocument}
          title={selectedTemplate?.name || "Documento"}
          onDownload={handleDownloadDocument}
        />
      )}

      {generatedDocument && (
        <DigitalSignatureDialog
          open={showSignatureDialog}
          onOpenChange={setShowSignatureDialog}
          document={generatedDocument}
          documentTitle={selectedTemplate?.name || "Documento"}
          onDocumentSigned={(signedDoc) => {
            console.log("Document signed:", signedDoc)
            toast({
              title: "Documento firmado",
              description: "El documento ha sido firmado digitalmente",
            })
          }}
        />
      )}
    </div>
  )
}
