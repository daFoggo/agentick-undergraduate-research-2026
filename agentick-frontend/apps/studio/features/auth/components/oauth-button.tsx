import { Button } from "@workspace/ui/components/button"

/**
 * One button for any OAuth provider: `<OAuthButton action={signInWithGoogleAction}>Continue with
 * Google</OAuthButton>`. The Server Action starts the flow and redirects, so no client state is needed.
 */
export function OAuthButton({
  action,
  children,
}: {
  action: () => Promise<void>
  children: React.ReactNode
}) {
  return (
    <form action={action}>
      <Button type="submit" variant="outline" size="lg" className="w-full">
        {children}
      </Button>
    </form>
  )
}
