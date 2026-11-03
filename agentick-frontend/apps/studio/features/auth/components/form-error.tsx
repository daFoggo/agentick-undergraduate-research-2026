import { IconAlertCircle } from "@tabler/icons-react"

import { Alert, AlertDescription } from "@workspace/ui/components/alert"

export function FormError({ message }: { message?: string }) {
  if (!message) return null
  return (
    <Alert variant="destructive">
      <IconAlertCircle />
      <AlertDescription>{message}</AlertDescription>
    </Alert>
  )
}
