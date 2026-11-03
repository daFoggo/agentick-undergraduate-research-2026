import { z } from "zod"

export const SignInSchema = z.object({
  email: z.email("Invalid email"),
  password: z
    .string()
    .min(6, "Password must be at least 6 characters")
    .max(128, "Password must be at most 128 characters"),
})

export type SignInInput = z.infer<typeof SignInSchema>

export const SignUpSchema = SignInSchema.extend({
  name: z.string().trim().min(1, "Please enter your name").max(255),
})

export type SignUpFormInput = z.infer<typeof SignUpSchema>
