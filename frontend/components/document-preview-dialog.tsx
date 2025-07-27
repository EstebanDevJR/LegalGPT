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
import { ScrollArea } from "@/components/ui/scroll-area"
import { Download, Copy, Share, PrinterIcon as Print } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface DocumentPreviewDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  document: string
  title: string
  onDownload: () => void
}

export function DocumentPreviewDialog({ open, onOpenChange, document, title, onDownload }: DocumentPreviewDialogProps) {
  const { toast } = useToast()

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(document)
      toast({
        title: "Copiado",
        description: "El documento ha sido copiado al portapapeles",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo copiar el documento",
        variant: "destructive",
      })
    }
  }

  const handlePrint = () => {
    const printWindow = window.open("", "_blank")
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>${title}</title>
            <style>
              body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
              h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
              h2 { color: #666; margin-top: 30px; }
              pre { white-space: pre-wrap; }
            </style>
          </head>
          <body>
            <pre>${document}</pre>
          </body>
        </html>
      `)
      printWindow.document.close()
      printWindow.print()
    }
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: document,
        })
      } catch (error) {
        // Fallback to copy
        handleCopyToClipboard()
      }
    } else {
      handleCopyToClipboard()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>Vista previa completa del documento generado</DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[60vh] w-full border rounded-lg p-4">
          <pre className="text-sm whitespace-pre-wrap leading-relaxed">{document}</pre>
        </ScrollArea>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={handleCopyToClipboard} className="gap-2 bg-transparent">
            <Copy className="h-4 w-4" />
            Copiar
          </Button>
          <Button variant="outline" onClick={handleShare} className="gap-2 bg-transparent">
            <Share className="h-4 w-4" />
            Compartir
          </Button>
          <Button variant="outline" onClick={handlePrint} className="gap-2 bg-transparent">
            <Print className="h-4 w-4" />
            Imprimir
          </Button>
          <Button onClick={onDownload} className="gap-2">
            <Download className="h-4 w-4" />
            Descargar
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
