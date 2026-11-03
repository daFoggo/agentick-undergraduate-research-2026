"use client"

import { useActionState, useState } from "react"
import { IconAlertCircle, IconPlus } from "@tabler/icons-react"

import { Alert, AlertDescription } from "@workspace/ui/components/alert"
import { Button } from "@workspace/ui/components/button"
import { Input } from "@workspace/ui/components/input"
import { Label } from "@workspace/ui/components/label"
import {
  NativeSelect,
  NativeSelectOption,
} from "@workspace/ui/components/native-select"
import { Spinner } from "@workspace/ui/components/spinner"

import {
  DialogActions,
  ResponsiveDialog,
} from "@/components/shared/responsive-dialog"

import {
  createOrgAction,
  createProjectAction,
  type CreateState,
} from "../actions"
import { REGIONS } from "../schemas"

/** Trigger button + dialog; the form goes in as children, so each dialog only supplies its fields. */
function CreateDialog({
  label,
  title,
  description,
  children,
}: {
  label: string
  title: string
  description: string
  children: (close: () => void) => React.ReactNode
}) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <Button onClick={() => setOpen(true)}>
        <IconPlus data-icon="inline-start" />
        {label}
      </Button>
      <ResponsiveDialog
        open={open}
        onOpenChange={setOpen}
        title={title}
        description={description}
      >
        {children(() => setOpen(false))}
      </ResponsiveDialog>
    </>
  )
}

function FormShell({
  action,
  state,
  pending,
  onCancel,
  submitLabel,
  children,
}: {
  action: (formData: FormData) => void
  state: CreateState
  pending: boolean
  onCancel: () => void
  submitLabel: string
  children: React.ReactNode
}) {
  return (
    <form action={action} className="flex flex-col gap-4">
      {state.error ? (
        <Alert variant="destructive">
          <IconAlertCircle />
          <AlertDescription>{state.error}</AlertDescription>
        </Alert>
      ) : null}
      {children}
      <DialogActions>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={pending}>
          {pending ? <Spinner data-icon="inline-start" /> : null}
          {submitLabel}
        </Button>
      </DialogActions>
    </form>
  )
}

function NameField({
  defaultValue,
  disabled,
  placeholder,
}: {
  defaultValue?: string
  disabled: boolean
  placeholder: string
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor="name">Name</Label>
      <Input
        id="name"
        name="name"
        defaultValue={defaultValue}
        placeholder={placeholder}
        required
        minLength={3}
        maxLength={48}
        autoComplete="off"
        disabled={disabled}
      />
    </div>
  )
}

export function CreateOrgDialog() {
  return (
    <CreateDialog
      label="New organization"
      title="New organization"
      description="Organizations group projects and members. You can rename it later."
    >
      {(close) => <OrgForm onCancel={close} />}
    </CreateDialog>
  )
}

function OrgForm({ onCancel }: { onCancel: () => void }) {
  const [state, action, pending] = useActionState(createOrgAction, {})
  return (
    <FormShell
      action={action}
      state={state}
      pending={pending}
      onCancel={onCancel}
      submitLabel="Create organization"
    >
      <NameField
        defaultValue={state.values?.name}
        disabled={pending}
        placeholder="Acme Inc"
      />
    </FormShell>
  )
}

export function CreateProjectDialog({ orgSlug }: { orgSlug: string }) {
  return (
    <CreateDialog
      label="New project"
      title="New project"
      description="A project has its own database, settings and region."
    >
      {(close) => <ProjectForm orgSlug={orgSlug} onCancel={close} />}
    </CreateDialog>
  )
}

function ProjectForm({
  orgSlug,
  onCancel,
}: {
  orgSlug: string
  onCancel: () => void
}) {
  const [state, action, pending] = useActionState(
    createProjectAction.bind(null, orgSlug),
    {}
  )
  return (
    <FormShell
      action={action}
      state={state}
      pending={pending}
      onCancel={onCancel}
      submitLabel="Create project"
    >
      <NameField
        defaultValue={state.values?.name}
        disabled={pending}
        placeholder="Web app"
      />
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="region">Region</Label>
        <NativeSelect
          id="region"
          name="region"
          defaultValue={state.values?.region ?? REGIONS[0]}
          disabled={pending}
          className="w-full"
        >
          {REGIONS.map((region) => (
            <NativeSelectOption key={region} value={region}>
              {region}
            </NativeSelectOption>
          ))}
        </NativeSelect>
      </div>
    </FormShell>
  )
}
