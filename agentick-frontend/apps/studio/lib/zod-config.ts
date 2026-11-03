import { z } from "zod"

/**
 * Zod probes `new Function("")` to enable its JIT parser; the probe is caught, but under our CSP
 * (no `unsafe-eval`) the browser still reports a violation in the console. Skipping the JIT costs
 * nothing at this scale. Zod decides on the JIT when a schema is constructed, so this must run
 * before client modules construct theirs: `instrumentation-client.ts` imports it and runs before
 * hydration.
 */
z.config({ jitless: true })
