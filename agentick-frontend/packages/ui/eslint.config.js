import { config } from "@workspace/eslint-config/react-internal"

/** @type {import("eslint").Linter.Config} */
export default [
  ...config,
  {
    // Vendored from shadcn and kept unmodified for upgrades; it syncs state with matchMedia on mount.
    files: ["src/hooks/use-mobile.ts"],
    rules: { "react-hooks/set-state-in-effect": "off" },
  },
  {
    // Vendored from shadcn and kept unmodified for upgrades; it reads the Embla API into state on init.
    files: ["src/components/carousel.tsx"],
    rules: { "react-hooks/set-state-in-effect": "off" },
  },
]
