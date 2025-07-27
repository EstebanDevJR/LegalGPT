"use client"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Crown, Check, Zap, Shield, Users, FileText, Headphones } from "lucide-react"

interface PlanUpgradeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentPlan: string
}

const plans = [
  {
    id: "profesional",
    name: "Profesional",
    price: "49.900",
    description: "Perfecto para pequeñas empresas",
    icon: Zap,
    color: "text-blue-600",
    bgColor: "bg-blue-100 dark:bg-blue-900",
    features: [
      "200 consultas/mes",
      "20K tokens",
      "50 documentos",
      "Generador de documentos básicos",
      "Plantillas avanzadas",
      "Soporte por email",
      "Exportación PDF",
    ],
    popular: true,
  },
  {
    id: "empresarial",
    name: "Empresarial",
    price: "99.900",
    description: "Para medianas empresas y equipos",
    icon: Crown,
    color: "text-purple-600",
    bgColor: "bg-purple-100 dark:bg-purple-900",
    features: [
      "500 consultas/mes",
      "50K tokens",
      "Documentos ilimitados",
      "Generador completo de documentos",
      "Todas las plantillas",
      "Soporte prioritario",
      "Múltiples usuarios",
      "Analytics avanzados",
      "API access",
    ],
    popular: false,
  },
]

export function PlanUpgradeDialog({ open, onOpenChange, currentPlan }: PlanUpgradeDialogProps) {
  const handleUpgrade = (planId: string) => {
    // Aquí iría la lógica de upgrade real
    console.log(`Upgrading to ${planId}`)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Crown className="h-6 w-6 text-yellow-500" />
            Mejora tu Plan
          </DialogTitle>
          <DialogDescription>
            Desbloquea funcionalidades premium y crea documentos legales profesionales
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Current Plan */}
          <Card className="border-orange-200 dark:border-orange-800">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-orange-100 dark:bg-orange-900">
                  <Shield className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <h3 className="font-semibold">Plan Actual: {currentPlan}</h3>
                  <p className="text-sm text-muted-foreground">Acceso limitado al generador de documentos</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Available Plans */}
          <div className="grid gap-6 md:grid-cols-2">
            {plans.map((plan) => (
              <Card key={plan.id} className={`relative ${plan.popular ? "ring-2 ring-primary" : ""}`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground">Más Popular</Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-4">
                  <div className={`mx-auto flex h-12 w-12 items-center justify-center rounded-lg ${plan.bgColor}`}>
                    <plan.icon className={`h-6 w-6 ${plan.color}`} />
                  </div>
                  <CardTitle className="text-xl">{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                  <div className="text-3xl font-bold">
                    ${plan.price}
                    <span className="text-sm font-normal text-muted-foreground">/mes</span>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <Separator />

                  <div className="space-y-3">
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Check className="h-4 w-4 text-green-600" />
                        <span className="text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Button
                    onClick={() => handleUpgrade(plan.id)}
                    className="w-full"
                    variant={plan.popular ? "default" : "outline"}
                  >
                    Mejorar a {plan.name}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Benefits Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>¿Qué obtienes con el upgrade?</CardTitle>
              <CardDescription>Comparación de funcionalidades por plan</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="text-center space-y-2">
                  <FileText className="h-8 w-8 mx-auto text-blue-600" />
                  <h4 className="font-semibold">Documentos Avanzados</h4>
                  <p className="text-sm text-muted-foreground">Contratos, actas, políticas y más</p>
                </div>

                <div className="text-center space-y-2">
                  <Zap className="h-8 w-8 mx-auto text-green-600" />
                  <h4 className="font-semibold">IA Avanzada</h4>
                  <p className="text-sm text-muted-foreground">Generación inteligente y personalizada</p>
                </div>

                <div className="text-center space-y-2">
                  <Users className="h-8 w-8 mx-auto text-purple-600" />
                  <h4 className="font-semibold">Colaboración</h4>
                  <p className="text-sm text-muted-foreground">Múltiples usuarios y equipos</p>
                </div>

                <div className="text-center space-y-2">
                  <Headphones className="h-8 w-8 mx-auto text-orange-600" />
                  <h4 className="font-semibold">Soporte Premium</h4>
                  <p className="text-sm text-muted-foreground">Atención prioritaria y especializada</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Tal vez después
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
