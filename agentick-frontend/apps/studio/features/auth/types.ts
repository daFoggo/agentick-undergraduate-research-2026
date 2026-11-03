/** What a form posts to: a Server Action of the app, the shape `useActionState` expects. */
export type FormAction<State> = (
  previous: State,
  formData: FormData
) => Promise<State>

/** `values` echoes non-secret fields back: React resets the form after an action finishes. */
export type SignInState = { error?: string; values?: { email: string } }
export type SignUpState = {
  error?: string
  confirmEmail?: boolean
  values?: { name: string; email: string }
}
export type DemoSignInState = { error?: string }
