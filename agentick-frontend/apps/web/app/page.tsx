import { CONTAINER } from "@/config/layout"
import { Header } from "@/components/sections/header"
import { HeroSection } from "@/components/sections/hero-section"
import { EcosystemSection } from "@/components/sections/ecosystem-section"
import { SeamsTopologySection } from "@/components/sections/seams-topology-section"
import { SecuritySection } from "@/components/sections/security-section"
import { PillarsSection } from "@/components/sections/pillars-section"
import { DeepDiveSection } from "@/components/sections/deep-dive-section"
import { AiWorkflowSection } from "@/components/sections/ai-workflow-section"
import { FaqSection } from "@/components/sections/faq-section"
import { Footer } from "@/components/sections/footer"

/**
 * Modern developer landing page with high craft inspired by interfaces.dev:
 * - Wide 1336px responsive container with comfortable whitespace
 * - Animate UI components: spring CopyButton, CountingNumber, spring gliding tabs
 * - Strict design system compliance: smallest text is text-xs, zero custom -[] values
 * - Decoupled modular sections with code splitting and lazy loading via next/dynamic
 * - Zero barrel overhead with explicit package imports
 */
export default function HomePage() {
  return (
    <>
      <Header />
      <main className={`${CONTAINER} flex flex-col gap-16 pt-16 pb-24 sm:gap-24 sm:pt-20`}>
        <HeroSection />
        <EcosystemSection />
        <SeamsTopologySection />
        <SecuritySection />
        <PillarsSection />
        <DeepDiveSection />
        <AiWorkflowSection />
        <FaqSection />
      </main>
      <Footer />
    </>
  )
}
