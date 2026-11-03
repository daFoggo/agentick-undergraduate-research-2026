---
name: design-system
description: >
  Visual rules for apps/studio and packages/ui (shadcn base-nova theme): colors, typography, the 7-tier spacing
  scale, responsive breakpoints, shadcn base-nova component sizes and motion. Use whenever writing or changing JSX
  classNames, layouts, pages, sections, lists, cards, navigation, footers, theme tokens in globals.css, or adding a
  shadcn component, and whenever the user mentions spacing, padding, margin, responsive, mobile, breakpoint, dark or
  light theme, font, color, or "looks off", even if they do not name the design system.
---

# Base design system

Source of truth: [docs/design-system.md](../../../docs/design-system.md). This file is the quick router; read the doc
section when a case is not covered here.

## Hard rules (check every className you write)

1. Nothing is custom. Everything numeric uses Tailwind's default scale. **No arbitrary values**
   (`mt-[54px]`, `text-[13px]`, `grid-cols-[auto_1fr]`, `rounded-[10px]`). Only exception: the logo's
   `--animate-logo-*` keyframes, used by `AppLogo` alone.
2. Smallest text is `text-xs`. Weights: `font-normal`, `font-medium`.
3. shadcn components: choose a `size` / `variant` prop. Never set `h-*`, `px-*`, `py-*`, `text-*` on them via
   `className`; layout classes (`w-full`, `mt-*`, `self-*`) are fine.
4. Style through the stock shadcn tokens (`bg-background`, `text-muted-foreground`, `border-border`, `bg-primary`), never
   hex or `dark:` color pairs. Both themes must work; dark is the default. Errors: `text-destructive`. No custom color
   tokens and no shadows (`shadow-*` is neutralised in `globals.css`).
5. `font-serif` exists but is opt-in; do not apply it unless asked.
6. CSS that comes from `vercel-react-view-transitions` (`::view-transition-*`) or `web-design-guidelines`
   (`content-visibility`, `transition`, etc.) must snap to the Tailwind scale and color tokens too; see

## Spacing tier lookup

| Relationship between the two things | Class |
| :--- | :--- |
| Glyph-level (icon/text, list items, dt/dd) | `gap-1.5` / `gap-2` |
| Same group (paragraphs, chip/title/author) | `gap-3` / `gap-3.5` |
| Heading to its content | `gap-5` |
| Blocks inside a section (figure, table, meta) | `gap-8` / `my-8`; `mt-9` above an H3 |
| Section to section | `gap-14` (`max-sm:gap-10`) |
| Page region (nav to content, body to footer) | `pt-20` / `mt-20` (`max-sm:pt-12`) |
| Major break (to related posts, CTA) | `mt-28` (`max-sm:mt-16`) |

Space above a heading is always larger than below it. Put spacing on the parent (`flex flex-col gap-*`), not margins on
children. Separate with space first, `border-b` second, a bordered box only for media objects.

## Layout and responsive

- Shell: `px-9 max-sm:px-6`; `grid grid-cols-1 lg:grid-cols-12`; rail `lg:col-span-4 lg:pr-10 lg:sticky lg:top-24`;
  content `min-w-0 lg:col-span-8`; prose `max-w-2xl`.
- Mobile-first. Only `lg` changes structure (rail stacks above, TOC hides, nav becomes a burger, rows split into two
  lines). `sm` / `md` / `xl` only adjust gutters, hide extras or tune columns.
- Reflow, never shrink type or truncate titles. Hide in this order: keyboard hint, category, tile/TOC, date.
- List rows: `flex items-start gap-4 border-b py-4`, no gap between rows; hover `hover:bg-primary
  hover:text-primary-foreground`.
- Anchor targets: `scroll-mt-24 max-sm:scroll-mt-18`.
- `ItemGroup` whose children are not real list items must pass `role="none"` (upstream `ItemGroup` ships `role="list"`).

## Components (Animate UI First)

**Always prioritize Animate UI components and primitives over static shadcn components or hand-rolled animations whenever possible.**

- All interactive shadcn components in `@workspace/ui/components/*` (`accordion`, `alert-dialog`, `checkbox`, `collapsible`, `combobox`, `context-menu`, `dialog`, `drawer`, `dropdown-menu`, `hover-card`, `input-otp`, `menubar`, `navigation-menu`, `pagination`, `popover`, `preview-link-card`, `progress`, `questionnaire`, `radio-group`, `select`, `sheet`, `sidebar`, `slider`, `switch`, `tabs`, `toast`, `toggle`, `toggle-group`, `tooltip`) are already animated with **Animate UI v2** (`@animate-ui/react`, Base UI primitives).
- Dedicated Animate UI primitives and registry components live in `@workspace/ui/components/animate-ui/*` (see `.agents/skills/animate-ui/SKILL.md`).

| Need | Use |
| :--- | :--- |
| Primary CTA | `<Button size="lg">` (or `@workspace/ui/components/animate-ui/buttons/button` for spring press) |
| Form / toolbar button | `<Button>` or `size="sm"` |
| Secondary | `variant="outline"` |
| Copy / Ripple / Theme switch | `@workspace/ui/components/animate-ui/buttons/{copy,ripple,theme-toggler}` |
| Animated numbers (stats, odometers, wheels) | `@workspace/ui/components/animate-ui/numbers/{counting-number,sliding-number,scrolling-number}` |
| Layout & pointer effects | `@workspace/ui/components/animate-ui/effects/{auto-height,scroll-fade,tilt,highlight,effect}` |
| Overlapping avatars | `@workspace/ui/components/animate-ui/avatar-group` |
| Chips | `<Badge variant="default">` / `variant="outline"` |
| Filter tabs | `<TabsList variant="line">` (gliding highlight & sliding panels built in) |
| Form error / success | `<Alert variant="destructive">` / `<Alert>` |

Add components from `packages/ui`: `pnpm dlx shadcn@latest add <name>`, then **always** run `pnpm --filter @workspace/ui animate` so its primitives are swapped for `@animate-ui/react`. Its `components.json` is the only one (`style: "base-nova"`). Keep `@tabler/icons-react` as the sole icon library.

## Navigation

Below `xl` the nav links move into a burger panel under the sticky nav (closes on link, Esc, outside click). In-page
anchors use `scroll-mt-24`; the logo scrolls to `0`.

## Dashboard shell (doc §8)

- Two full-height columns: shadcn `<Sidebar collapsible="icon">` · main `flex-1 min-w-0`. Each = `<ColumnHeader>` (`flex h-14
  shrink-0 items-center gap-4 border-b px-4`) + a body with `no-scrollbar overflow-y-auto`. No third column: a record opens in a
  detail sheet from the page.
- Logo lives in the sidebar header; below `md` (or with the sidebar collapsed) it shows in the main header next to the `SidebarTrigger`.
- Sidebar body = labelled sections (`config/navigation.ts`), named by content (`Workspace`, `Settings`), never "Tree".
  Header = `SidebarTrigger` + path breadcrumb (no project name) + `ThemeToggle`; no header state, no bare-key shortcuts.
  The menu follows the URL: `NAV_SCOPES` holds one `NavScope` per prefix (global, `/org/<slug>`, `/project/<ref>`); scoped breadcrumbs start with organization / project menus (`Crumb.options`). New scope = one entry, no component edits.
  The sidebar collapses to a 48px icon rail (doc § Icon rail): every `NavLink` needs an `icon` name; icons are functional, never decorative.
- Never edit shadcn files in `packages/ui`; compose in `apps/studio/components/layout/`.
- Each section is the big TOC: mono `text-sm`, `└` + an icon per link (current glyph `text-foreground`), max two levels, counts
  `ml-auto text-xs tabular-nums`.
- Detail sheet (doc § Detail sheets): `<Sheet>` + `DetailSheetContent` (fits content, drag the left edge to resize) with three header
  tiers (opens at 42rem, resized by dragging its left edge, width remembered): `DetailSheetHeader` (close, title, copy, Previous/Next as a `ButtonGroup`), `DetailSheetPaneHeader` per pane, then
  `DetailSheetPaneBody`. Open state, width and selection stay inside the sheet (`TraceProvider`); compound parts, no boolean
  props (vercel-composition-patterns). Trees follow shadcn File Tree: `Collapsible` per node + ghost `Button` rows; hover
  `bg-muted`, selected `bg-primary/10`, chevron `aria-expanded:bg-transparent`. Never animate a size (width, max-width): slide with transform/opacity only; no `backdrop-filter`; memoize provider values.
  List rows elsewhere: selected `bg-primary text-primary-foreground`.
- Metrics are a `dl` row, no stat cards. One focal accent per screen.
- Logo: always `<AppLogo variant size motion />` (doc § Logo), sizes 16/24/32 only, animated (`idle`) by default everywhere.

## Type and motion

- Titles `text-3xl md:text-4xl font-medium leading-tight`; prose `text-lg leading-relaxed text-muted-foreground`; labels
  `font-mono text-xs uppercase tracking-wider`; nav/dates `font-mono text-sm text-muted-foreground`.
- Transitions: colors `duration-150`, movement `duration-200 ease-out`; guard with `motion-safe:`.

## Before you finish

Grep your diff for `-[` inside classNames, `text-[`, hex colors and `h-`/`px-` on shadcn components. Check the page at
375px, 768px, 1024px and 1440px in both themes, with no horizontal scroll.
