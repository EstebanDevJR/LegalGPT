"use client"

import { useAuth } from "@/components/auth-provider"
import { AuthPage } from "@/components/auth-page"
import { ChatPage } from "@/components/chat-page"
import { LoadingSpinner } from "@/components/loading-spinner"

export default function AppPage() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (!user) {
    return <AuthPage />
  }

  return <ChatPage />
}
