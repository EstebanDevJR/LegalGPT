"use client"

import type React from "react"

import { useState, useEffect } from "react"
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
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Plus, X, HelpCircle } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

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

interface EditTemplateDialogProps {
  template: Template
  open: boolean
  onOpenChange: (open: boolean) => void
  onTemplateUpdated: (template: Template) => void
}

const categories = ["Constitución Empresarial", "Tributario", "Laboral", "Propiedad Intelectual", "Comercial", "Civil"]

export function EditTemplateDialog({ template, open, onOpenChange, onTemplateUpdated }: EditTemplateDialogProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    content: "",
    category: "",
    isPublic: false,
  })
  const [tags, setTags] = useState<string[]>([])
  const [newTag, setNewTag] = useState("")
  const [variables, setVariables] = useState<{ name: string; placeholder: string; required: boolean }[]>([])

  useEffect(() => {
    if (template) {
      setFormData({
        title: template.title,
        description: template.description,
        content: template.content,
        category: template.category,
        isPublic: template.isPublic,
      })
      setTags(template.tags)
      setVariables(template.variables || [])
    }
  }, [template])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const updatedTemplate: Template = {
      ...template,
      ...formData,
      tags,
      variables,
      updatedAt: new Date().toISOString(),
    }

    onTemplateUpdated(updatedTemplate)
  }

  const addTag = () => {
    if (newTag.trim() && !tags.includes(newTag.trim())) {
      setTags([...tags, newTag.trim()])
      setNewTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove))
  }

  const addVariable = () => {
    setVariables([...variables, { name: "", placeholder: "", required: false }])
  }

  const updateVariable = (index: number, field: string, value: string | boolean) => {
    const updated = [...variables]
    updated[index] = { ...updated[index], [field]: value }
    setVariables(updated)
  }

  const removeVariable = (index: number) => {
    setVariables(variables.filter((_, i) => i !== index))
  }

  const detectVariables = () => {
    const variableRegex = /\{\{(\w+)\}\}/g
    const matches = formData.content.match(variableRegex)
    if (matches) {
      const detectedVars = matches.map((match) => match.replace(/[{}]/g, ""))
      const uniqueVars = [...new Set(detectedVars)]
      const newVariables = uniqueVars
        .filter((varName) => !variables.some((v) => v.name === varName))
        .map((varName) => ({
          name: varName,
          placeholder: `Ingresa ${varName}`,
          required: true,
        }))
      setVariables([...variables, ...newVariables])
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Editar Plantilla</DialogTitle>
          <DialogDescription>Modifica los detalles de tu plantilla</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Título de la plantilla</Label>
              <Input
                id="title"
                placeholder="Ej: Registro de SAS"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descripción</Label>
              <Textarea
                id="description"
                placeholder="Describe brevemente para qué sirve esta plantilla..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Categoría</Label>
              <Select
                value={formData.category}
                onValueChange={(value) => setFormData({ ...formData, category: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona una categoría" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Content */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="content">Contenido de la consulta</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <HelpCircle className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Usa {`{{nombreVariable}}`} para crear campos personalizables</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Textarea
              id="content"
              placeholder="Escribe tu consulta aquí. Usa {{nombreVariable}} para campos personalizables..."
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              className="min-h-[120px]"
              required
            />
            <Button type="button" variant="outline" size="sm" onClick={detectVariables}>
              Detectar variables automáticamente
            </Button>
          </div>

          {/* Variables */}
          {variables.length > 0 && (
            <div className="space-y-4">
              <Label>Variables</Label>
              <div className="space-y-3">
                {variables.map((variable, index) => (
                  <Card key={index}>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 grid grid-cols-2 gap-3">
                          <div>
                            <Label className="text-xs">Nombre</Label>
                            <Input
                              value={variable.name}
                              onChange={(e) => updateVariable(index, "name", e.target.value)}
                              placeholder="nombreVariable"
                              className="h-8"
                            />
                          </div>
                          <div>
                            <Label className="text-xs">Placeholder</Label>
                            <Input
                              value={variable.placeholder}
                              onChange={(e) => updateVariable(index, "placeholder", e.target.value)}
                              placeholder="Texto de ayuda"
                              className="h-8"
                            />
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={variable.required}
                            onCheckedChange={(checked) => updateVariable(index, "required", checked)}
                          />
                          <Label className="text-xs">Requerido</Label>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => removeVariable(index)}
                          className="h-8 w-8"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              <Button type="button" variant="outline" onClick={addVariable} className="gap-2 bg-transparent">
                <Plus className="h-4 w-4" />
                Añadir variable
              </Button>
            </div>
          )}

          {/* Tags */}
          <div className="space-y-2">
            <Label>Etiquetas</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Añadir etiqueta..."
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
              />
              <Button type="button" onClick={addTag} variant="outline">
                Añadir
              </Button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="gap-1">
                    {tag}
                    <X className="h-3 w-3 cursor-pointer" onClick={() => removeTag(tag)} />
                  </Badge>
                ))}
              </div>
            )}
          </div>

          {/* Settings */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Plantilla pública</Label>
              <p className="text-sm text-muted-foreground">Otros usuarios podrán ver y usar esta plantilla</p>
            </div>
            <Switch
              checked={formData.isPublic}
              onCheckedChange={(checked) => setFormData({ ...formData, isPublic: checked })}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit">Guardar Cambios</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
