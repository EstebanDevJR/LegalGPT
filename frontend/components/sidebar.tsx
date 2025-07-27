"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  MessageSquare,
  FileText,
  User,
  BarChart3,
  Settings,
  ChevronLeft,
  Clock,
  BookmarkPlus,
  Crown,
  PenTool,
} from "lucide-react"

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const navigation = [
  {
    name: "Nueva Consulta",
    href: "/app/chat",
    icon: MessageSquare,
    primary: true,
  },
  {
    name: "Plantillas",
    href: "/app/templates",
    icon: BookmarkPlus,
  },
  {
    name: "Generar Documentos",
    href: "/app/document-generator",
    icon: Crown,
    premium: true,
  },
  {
    name: "Firmas Digitales",
    href: "/app/signatures",
    icon: PenTool,
    premium: true,
  },
  {
    name: "Historial",
    href: "/app/history",
    icon: Clock,
  },
  {
    name: "Documentos",
    href: "/app/documents",
    icon: FileText,
  },
  {
    name: "Estadísticas",
    href: "/app/stats",
    icon: BarChart3,
  },
  {
    name: "Perfil",
    href: "/app/profile",
    icon: User,
  },
  {
    name: "Configuración",
    href: "/app/settings",
    icon: Settings,
  },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && <div className="fixed inset-0 z-40 bg-black/50 md:hidden" onClick={onClose} />}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed left-0 top-16 z-50 h-[calc(100vh-4rem)] w-64 transform border-r bg-background transition-transform duration-200 ease-in-out md:relative md:top-0 md:h-screen md:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 md:hidden">
            <h2 className="text-lg font-semibold">Menú</h2>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
          </div>

          {/* Navigation */}
          <ScrollArea className="flex-1 px-3">
            <div className="space-y-2 py-4">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                return (
                  <Link key={item.name} href={item.href} onClick={onClose}>
                    <Button
                      variant={isActive ? "secondary" : "ghost"}
                      className={cn(
                        "w-full justify-start gap-3 h-11",
                        item.primary && "bg-primary text-primary-foreground hover:bg-primary/90",
                        item.premium &&
                          "bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border border-yellow-500/20",
                        isActive && !item.primary && "bg-secondary",
                      )}
                    >
                      <item.icon className={cn("h-4 w-4", item.premium && "text-yellow-600 dark:text-yellow-400")} />
                      <span className={cn(item.premium && "font-medium")}>{item.name}</span>
                      {item.premium && <Crown className="h-3 w-3 text-yellow-500 ml-auto" />}
                    </Button>
                  </Link>
                )
              })}
            </div>
          </ScrollArea>

          {/* Footer */}
          <div className="border-t p-4">
            <div className="text-xs text-muted-foreground">
              <p>Consultas hoy: 5/50</p>
              <p>Tokens usados: 1,250/10,000</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
