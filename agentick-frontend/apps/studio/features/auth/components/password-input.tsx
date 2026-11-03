"use client"

import { useState } from "react"
import { IconEye, IconEyeOff } from "@tabler/icons-react"

import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
} from "@workspace/ui/components/input-group"

type PasswordInputProps = {
  id: string
  name: string
  autoComplete: "current-password" | "new-password"
  placeholder?: string
  disabled?: boolean
}

export function PasswordInput({
  id,
  name,
  autoComplete,
  placeholder,
  disabled,
}: PasswordInputProps) {
  const [visible, setVisible] = useState(false)
  return (
    <InputGroup>
      <InputGroupInput
        id={id}
        name={name}
        type={visible ? "text" : "password"}
        autoComplete={autoComplete}
        placeholder={placeholder}
        required
        minLength={6}
        maxLength={128}
        disabled={disabled}
      />
      <InputGroupAddon align="inline-end">
        <InputGroupButton
          size="icon-xs"
          aria-label={visible ? "Hide password" : "Show password"}
          onClick={() => setVisible((value) => !value)}
        >
          {visible ? <IconEyeOff /> : <IconEye />}
        </InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  )
}
