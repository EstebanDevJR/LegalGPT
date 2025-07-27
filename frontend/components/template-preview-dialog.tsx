"use client"

import { useState } from "react"
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
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Play, Star, Eye } from "lucide-react"

interface Template {
  id: string
  title: string
  description: string
  content: string
  category: string
  tags: string[]
  isPublic: boolean
  isFavorite: boolean
  usageCount: number
  createdAt: string
  updatedAt: string
  variables?: { name: string; placeholder: string; required: boolean }[]
}

interface TemplatePreviewDialogProps {
  template: Template
  open: boolean
  onOpenChange: (open: boolean) => void
  onUseTemplate: () => void
}

export function TemplatePreviewDialog({ template, open, onOpenChange, onUseTemplate }: TemplatePreviewDialogProps) {
  const [variableValues, setVariableValues] = useState<Record<string, string>>({})

  const handleVariableChange = (variableName: string, value: string) => {
    setVariableValues((prev) => ({ ...prev, [variableName]: value }))
  }

  const generatePreview = () => {
    let preview = template.content
    template.variables?.forEach((variable) => {
      const value = variableValues[variable.name] || `{{${variable.name}}}`
      preview = preview.replace(new RegExp(`\\{\\{${variable.name}\\}\\}`, "g"), value)
    })
    return preview
  }

  const canUseTemplate = () => {
    if (!template.variables) return true
    return template.variables
      .filter((v) => v.required)
      .every((v) => variableValues[v.name] && variableValues[v.name].trim() !== "")
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Vista Previa de Plantilla
          </DialogTitle>
          <DialogDescription>Revisa y personaliza la plantilla antes de usarla</DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Template Info */}
          <Card>
            <CardContent className="p-4">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      {template.title}
                      {template.isFavorite && <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />}
                    </h3>
                    <p className="text-muted-foreground">{template.description}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">{template.category}</Badge>
                  {template.isPublic && <Badge variant="outline">Pública</Badge>}
                  <Badge variant="outline">Usada {template.usageCount} veces</Badge>
                </div>

                <div className="flex flex-wrap gap-1">
                  {template.tags.map((tag) => (
                    <Badge key={tag} variant="outline" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Variables */}
          {template.variables && template.variables.length > 0 && (
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-3">Personaliza las variables</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  {template.variables.map((variable) => (
                    <div key={variable.name} className="space-y-2">
                      <Label htmlFor={variable.name} className="flex items-center gap-1">
                        {variable.name}
                        {variable.required && <span className="text-red-500">*</span>}
                      </Label>
                      <Input
                        id={variable.name}
                        placeholder={variable.placeholder}
                        value={variableValues[variable.name] || ""}
                        onChange={(e) => handleVariableChange(variable.name, e.target.value)}
                        required={variable.required}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <Separator />

          {/* Preview */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium">Vista previa de la consulta</h4>
            <Card>
              <CardContent className="p-4">
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{generatePreview()}</div>
              </CardContent>
            </Card>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cerrar
          </Button>
          <Button onClick={onUseTemplate} disabled={!canUseTemplate()} className="gap-2">
            <Play className="h-4 w-4" />
            Usar Plantilla
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
