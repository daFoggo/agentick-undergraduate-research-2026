# Design system

How `apps/studio` looks and behaves: color, type, spacing, responsive layout, components and motion. The theme is
shadcn `base-nova` with the stock shadcn tokens, nothing custom. Every value is Tailwind's default scale. Tokens live in
`packages/ui/src/styles/globals.css`, components in `packages/ui/src/components` (shadcn, style `base-nova`).
An illustrated, interactive version of this guide lives in [design-system/base-design-system.html](design-system/base-design-system.html)
(it still shows the previous theme). When the two disagree, this file wins.

---

## 1. Rules that never bend

1. **Nothing is custom.** Colors are the stock shadcn tokens. Font size, weight, leading, tracking, spacing, border width, radius, duration, easing and
   breakpoints come from Tailwind's default scale. No arbitrary values (`mt-[54px]`, `text-[13px]`, `grid-cols-[auto_1fr]`).
   If no step fits, use the nearest one. **One exception: the logo.** Its frame-by-frame keyframes live as
   `--animate-logo-*` tokens in `globals.css` and are used only by `AppLogo` (see [Logo](#logo)).
   **Flat by default:** every `shadow-*` utility is neutralised in `globals.css` (`--shadow-*` tokens) and overlays do not blur
   (`backdrop-filter: none` on `[data-slot$="overlay"]`). Do not add shadows or blur.
   **Second exception: `app/global-error.tsx`.** It uses inline system-color styles (`Canvas`, `CanvasText`) because
   `global-error` replaces the root layout, so global CSS and the theme tokens are not loaded there.
2. **Smallest text is `text-xs`.** Weights are `font-normal` and `font-medium` only.
3. **Components keep their own sizes.** Pick a `size` / `variant` prop (`<Button size="sm">`). Never override height,
   padding or font size through `className`. Layout classes such as `w-full` or `mt-*` are fine. If no size fits, add a
   variant to the component instead of patching the call site.
4. **Dark first, light complete.** `defaultTheme="dark"`, but `:root` (light) and `.dark` both define every token. Never
   style for one theme only.
5. **Root stays 16px.** The rem scale must match Tailwind's.

---

## 2. Color

Defined in `globals.css` (oklch, neutral zinc) and exposed as utilities (`bg-background`, `text-muted-foreground`, ...).
Only the stock shadcn tokens exist: `background`, `foreground`, `card`, `popover`, `primary`, `secondary`, `muted`,
`accent`, `destructive`, `border`, `input`, `ring`, `chart-1..5`, `sidebar-*` (each with its `-foreground`), plus `--radius`
(`0.625rem`). Both `:root` and `.dark` define every token.

| Need | Use |
| :--- | :--- |
| Page and body text | `bg-background` / `text-foreground` |
| Descriptions, meta, labels, dates | `text-muted-foreground` |
| Decoration only (`└`, dots) | `text-muted-foreground/50`. Never readable text |
| Raised surfaces, menus | `bg-card`, `bg-popover` |
| CTA fill, selected row | `bg-primary text-primary-foreground` |
| Hover surface | `bg-accent` |
| Errors, blocked | `text-destructive`, `<Alert variant="destructive">` |
| Hairlines, field outlines | `border-border`, `border-input` |

To add a semantic color (success, warning), add a token to both `:root` and `.dark` and map it in `@theme inline`.

---

## 3. Typography

| Family | Class | Use |
| :--- | :--- | :--- |
| Geist | `font-sans` | UI, headings, body, prose |
| Geist Mono | `font-mono` | Nav, tabs, labels, dates, durations, code, in-article section headings |
| STIX Two Text | `font-serif` | Registered only. No component uses it by default |

| Role | Classes |
| :--- | :--- |
| Article / featured title | `text-3xl md:text-4xl font-medium leading-tight` |
| Page name in the rail | `font-mono text-3xl leading-none` |
| Section title in the rail | `font-mono text-2xl leading-tight` |
| Standfirst, prose | `text-lg leading-relaxed text-muted-foreground` (`max-sm:text-base`) |
| Row title, UI body | `text-base` |
| In-article H2/H3 | `font-mono text-sm font-medium uppercase tracking-wide` |
| Nav, tabs, dates, durations | `font-mono text-sm text-muted-foreground` |
| Labels, table headers, chips | `font-mono text-xs uppercase tracking-wider` |

---

## 4. Spacing

Related things sit close, unrelated things sit far apart, and each tier is roughly 1.5 to 2.5 times the one below it.
That ratio is what makes the pages feel open yet clearly sectioned. Use the tier's class; do not invent new tokens.

| Tier | Tailwind | Measured | Use |
| :--- | :--- | :--- | :--- |
| T1 Glyph | `gap-1.5`, `gap-2` | 6-7px | List items, `dt` to `dd`, icon to text |
| T2 Group | `gap-3`, `gap-3.5` | 12-14px | Consecutive paragraphs; chip, title and author in one block; footer links |
| T3 Heading | `gap-5` | 18-20px | A heading to its first content |
| T4 Block | `gap-8` / `my-8`; `mt-9` before an H3 | 30-36px | Figures, tables, article meta, blocks inside one section |
| T5 Section | `gap-14` | 54px | Between sections of an article or doc page |
| T6 Page region | `pt-20` / `mt-20` | 72-80px | Nav to content, header to body, content to footer |
| T7 Major break | `mt-28` | 110px | End of main content to a different block (related posts, CTA) |

Rules:

- **A heading belongs to what follows.** Space above a heading is always larger than below (H3: `mt-9` above, `gap-5`
  below). Wrap heading and content in `flex flex-col gap-5` rather than giving each a margin.
- **Space first, hairline second, box last.** Sections are separated by space only. Lists use `border-b`. A full border
  box is reserved for media objects: figure, card.
- **Containers own spacing.** Use `gap` / `space-y` on the parent; avoid one-off margins on children.
- **One left axis.** Header, prose, lists and related posts all start at the content column; the rail never crosses it.
- **List rows carry their own padding.** `py-4 border-b` with `gap-0` between rows, so the hover fill covers the row.

Horizontal: page gutter `px-9` (`max-sm:px-6`), 12-column grid with no column gap, rail `col-span-4 pr-10`, content
`col-span-8 pl-8`, prose `max-w-2xl`.

Component padding: list row `py-4`; featured row `py-4` with `gap-3` inside; media item (mod) `py-9`; figure `my-8 p-4`,
caption `py-2.5 px-4`; footer `pt-11 pb-14`, links `gap-3`.

- `ItemGroup` whose children are not real list items must pass `role="none"` (upstream `ItemGroup` ships `role="list"`).

---

## 5. Responsive

Pages use Tailwind's four default breakpoints and are written mobile-first; only one of them changes the layout.

| Breakpoint | Kind | What changes |
| :--- | :--- | :--- |
| `xl` 1280 | Tuning | Widest: rail at full 4 columns, rows on one line (date, title, duration) |
| `lg` 1024 | **Layout** | Below lg: nav becomes a burger, rail stacks above content and stops being sticky, TOC hides, rows split into two lines, featured post stacks, media items put media on top |
| `md` 768 | Hide extras | Below md: keyboard hint and category column hide, tabs wrap, newsletter goes one column |
| `sm` 640 | Margins and rhythm | Below sm: gutter `px-6`, nav `h-18`, prose `text-base`, footer two columns, outer spacing tiers shrink |

| Component | < sm | sm to lg | >= lg |
| :--- | :--- | :--- | :--- |
| Nav | `h-18`, burger | `h-24`, burger | `h-24`, full links with `[X]` keys |
| Rail / content | Stacked: rail becomes a static header block | Stacked | 4 / 8 columns, rail sticky |
| Article TOC | Hidden (share links only) | Hidden | Sticky in the rail |
| Post row | Two lines, date hidden | Two lines: title / date + duration | One line |
| Article meta | `grid-cols-2` | `grid-cols-3` | `grid-cols-3`, aligned to grid columns |
| Footer | `grid-cols-2`, brand and newsletter full width | `grid-cols-3` | Brand, two link columns, newsletter |
| Spacing T5 / T6 / T7 | `gap-10` / `pt-12` / `mt-16` | `gap-14` / `pt-20` / `mt-28` | same |

Principles:

- **One layout breakpoint.** Only `lg` may restructure a page; `sm`, `md` and `xl` adjust margins, hide extras or tune
  column ratios.
- **Reflow, don't shrink.** Type sizes barely change; rows split into two lines instead of truncating. The title always
  gets the first line.
- **Hide from least to most important:** keyboard hint, category, tile and TOC, then date. Titles, durations and CTAs
  never hide.
- **Hover effects need a mouse.** Tailwind v4's `hover:` already applies only under `(hover: hover)`; on touch, the
  tapped row takes the hover's role.
- **Shrink the outer tiers, keep the inner ones.** Only the gutter and T5-T7 change below `sm`.

```tsx
{/* Shell: rail stacked on mobile, 4/8 from lg */}
<div className="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:gap-0">
  <aside className="lg:sticky lg:top-24 lg:col-span-4 lg:self-start lg:pr-10" />
  <main className="min-w-0 lg:col-span-8" />
</div>

{/* Post row: title on line 1, date + duration on line 2; one line from lg */}
<a className="flex items-start gap-4 border-b py-4 lg:items-center">
  <PixelIcon className="size-8 shrink-0" />
  <div className="flex min-w-0 flex-1 flex-col gap-2 lg:grid lg:grid-cols-8 lg:items-center lg:gap-0">
    <span className="text-base lg:order-2 lg:col-span-5">{title}</span>
    <span className="flex gap-4 font-mono text-sm text-muted-foreground lg:contents">
      <time className="max-sm:hidden lg:order-1 lg:col-span-2" />
      <span className="lg:order-3 lg:col-span-1 lg:text-right">{minutes}</span>
    </span>
  </div>
</a>
```

---

## 6. Components

shadcn `base-nova`: rounded corners (`--radius: 0.625rem`: `rounded-lg` fields and buttons, `rounded-md` menu rows, `rounded-xl` cards), compact sizes, no shadows. Every component is installed (`shadcn add --all`), including the chat set (`message`, `bubble`, `code-block`, `trace`, `questionnaire`, `message-scroller`, `attachment`, `marker`) and `carousel`; add what the app needs, delete nothing.

| Need | Use |
| :--- | :--- |
| Primary CTA | `<Button size="lg">` (h-9) |
| Button in a form or toolbar | `<Button>` (h-8) or `size="sm"` (h-7) |
| Secondary action | `variant="outline"` |
| "Featured" chip | `<Badge variant="default">` |
| Category chip | `<Badge variant="outline">` |
| Filter tabs | `<Tabs>`, `<TabsList variant="line">` |
| Form error / success notice | `<Alert variant="destructive">` / `<Alert>` |
| Animated press button / copy / ripple / theme switch | `@workspace/ui/components/animate-ui/buttons/{button,copy,ripple,theme-toggler}` |
| Animated numbers (stats, odometers, wheels) | `@workspace/ui/components/animate-ui/numbers/{counting-number,sliding-number,scrolling-number}` |
| Animated layout & pointer effects | `@workspace/ui/components/animate-ui/effects/{auto-height,scroll-fade,tilt,highlight,effect}` |
| Overlapping avatars with hover rise | `@workspace/ui/components/animate-ui/avatar-group` |

**Animate UI first (always prioritized over static shadcn):**

All interactive components in `packages/ui/src/components/*` (`accordion`, `alert-dialog`, `checkbox`, `collapsible`, `combobox`, `context-menu`, `dialog`, `drawer`, `dropdown-menu`, `hover-card`, `input-otp`, `menubar`, `navigation-menu`, `pagination`, `popover`, `preview-link-card`, `progress`, `questionnaire`, `radio-group`, `select`, `sheet`, `sidebar`, `slider`, `switch`, `tabs`, `toast`, `toggle`, `toggle-group`, `tooltip`) are powered by **Animate UI v2** (`@animate-ui/react`, Base UI primitives). Additional Animate UI primitives and registry components live under `packages/ui/src/components/animate-ui/*`.

Rules:
- **Always prefer Animate UI components and primitives over static shadcn components or hand-rolled CSS/JS animations whenever possible.**
- After installing or updating any shadcn component in `packages/ui` (`pnpm dlx shadcn@latest add <name>`), always run `pnpm --filter @workspace/ui animate` to swap its Base UI primitives for `@animate-ui/react`'s animated primitives.
- Keep `@tabler/icons-react` as the sole icon library across the monorepo (do not install Lucide or Hugeicons from `@animate-ui`).

Patterns specific to this language:

- **Inverted hover** on list rows: `hover:bg-primary hover:text-primary-foreground`, other rows dim to `opacity-35`.
- **`└` marks hierarchy** in the TOC, article meta and spec lists, in `text-muted-foreground/50`.
- **Bracketed keys** `[H]` before primary nav items, with matching keyboard shortcuts.
- **Mono uppercase labels** for metadata, never for body text.

---

## Logo

`AppLogo` (`packages/ui-patterns/src/app-logo.tsx`, shared by `apps/web` and `apps/studio`): an 8x8 pixel mark, a `>` prompt (`currentColor`, follows
the theme), a little spark in `primary` and one muted ember, drawn as `<rect>`s with `shape-rendering="crispEdges"`.

| Prop | Values | Use |
| :--- | :--- | :--- |
| `variant` | `full` (default) · `mark` · `wordmark` | `mark` where space is tight or for icons; `wordmark` when the mark already shows nearby |
| `size` | `sm` 16px · `md` 24px (default) · `lg` 32px | Mark and wordmark scale together; the wordmark is mono `font-medium tracking-tight` (`text-sm/none` / `text-lg/none` / `text-2xl/none`) |
| `motion` | `idle` (default) · `static` | The logo is always alive: `idle` everywhere in the app (sidebar, headers, auth). `static` only where the mark must stay still (print, dense lists) |

Rules:

- Sizes are whole multiples of the 8x8 grid (16, 24, 32px) so every pixel stays crisp. Never scale the mark freely.
- Do not redraw or recolor the mark at the call site; wrap it in a `Link` when it navigates. The logo is a block-level
  `flex w-fit` box (an inline box would sit on the text baseline and add a gap below it).
- `idle` animates only under `motion-safe`; with reduced motion it renders exactly like `static`.
- The favicon is `apps/studio/app/icon.svg`, the same mark with fixed light/dark colors (`prefers-color-scheme`).

---

## 7. Navigation

- Site nav: sticky, `h-24` (`max-sm:h-18`), brand left, links with `[X]` keys in the middle, commands and CTA right.
- Below `xl` (or whenever the links stop fitting) the links move into a **burger panel**: a `size-9` button with three
  2px bars that turn into an X (`aria-expanded`, `aria-controls`). The panel drops under the nav, full width, `bg-background
  border-b`, groups labelled with mono `text-xs` headings, links `font-mono text-sm py-2.5`. It closes on link click, Esc,
  outside click, and when the viewport grows past the breakpoint.
- Between `xl` and `2xl` hide the `[X]` brackets first (keys still work), then fall back to the burger.
- In-page links scroll with an offset equal to the nav height (`scroll-mt-24`); the logo always scrolls to `0` and clears
  the hash, so clicking it twice still works.

---

## 8. Dashboard shell

The app layout extends the same language: the article TOC "tree" becomes the sidebar, the Mods spec list becomes a
detail sheet. Reference demo: the "Next Mono Base Design System" artifact, section 06.

### Anatomy

Two full-height columns. Each column is a **header cell** plus a scrolling body. All header cells use one shared
component so they always line up and the hairline runs straight across. Anything more (a record, a trace, a file) opens
as a [detail sheet](#detail-sheets) from the page, never as a third column.

```tsx
function ColumnHeader({ children }: { children: React.ReactNode }) {
  return <div className="flex h-14 shrink-0 items-center gap-4 border-b px-4">{children}</div>
}
```

| Column | Header cell | Body |
| :--- | :--- | :--- |
| Sidebar (shadcn `<Sidebar collapsible="icon">`, `w-64`) | Logo + workspace switcher | `px-4 py-6 gap-8`: one labelled **section** per nav group (`WORKSPACE`, `SETTINGS`, ...), then account pinned to the bottom |
| Main (`flex-1 min-w-0`) | `SidebarTrigger`, logo (below `md` only), path breadcrumb (`dashboard / settings / account`, no project name), `ThemeToggle` at the far right | `px-4 sm:px-8 pt-10 pb-14 gap-8`: page head, metrics, tabs + list |

The header holds no state of its own: shadcn owns the sidebar's open state (`SidebarProvider`), `next-themes` the theme.

Scroll areas hide their scrollbar but stay scrollable (mouse, keys, touch):

```css
@utility no-scrollbar { scrollbar-width: none; &::-webkit-scrollbar { display: none; } }
```

### Sections

The sidebar holds any number of **sections**, each a mono `text-xs` uppercase label over a tree
(`config/navigation.ts`, `NavSection`). Name a section after what its pages are about (`Workspace`, `Settings`,
`Projects`), never after the widget ("Tree", "Menu"). A section whose links the role cannot open is hidden. Inside a
section an entry is a link or a collapsible group of links (two levels max).

### Scoped menus (organization, project)

The menu depends on the URL, like Supabase's Studio: `/org/<slug>/...` shows the organization menu, `/project/<ref>/...`
the project menu, everything else the global one. A menu is a `NavScope` in `NAV_SCOPES` (`config/navigation.ts`): plain
data (`id`, `prefix`, `param`, `sections`) whose hrefs hold `:param` placeholders. To add a scope, add one entry and its
layout under `app/(dashboard)/<prefix>/[param]/`. `SessionNav` (server) filters every scope by role; the client
`ScopedNav` picks the scope from `usePathname()` and renders `NavTree`, which knows nothing about scopes.

The header has two icon buttons (`ghost`, `icon-sm`): `SidebarTrigger` (with `SidebarPrimitive.TriggerIcon` swapping between collapse/expand icons; Cmd/Ctrl+B also works) and `ThemeToggle`
(built on Animate UI's `ThemeTogglerButton` icon spin/blur swap, while the page theme flips instantly via `disableTransitionOnChange`). The account row shows `└`, a user icon, name and role. Icons are functional only: one per navigable page (and the
account row), never on group headers or menu items; the `└` glyph stays next to them as the hierarchy mark.

Main header below `md`: sidebar trigger, wordmark, `/`, current page in ink, truncated with `…` rather than wrapping.

### Icon rail

The sidebar uses `collapsible="icon"`: the trigger (or a click on the rail edge) shrinks it from `w-64` to a 48px rail instead of
hiding it, so every page stays one click away.

- Every nav link carries `└`, its icon and its label. In the rail only the icon shows (the glyph and label hide; the
  current page's icon is `text-foreground` there) and a right-side tooltip names it (`SidebarMenuButton`'s rule: only
  while collapsed on desktop).
- The rail lists individual pages only, never groups: a section label becomes a hairline between sections, a collapsible
  group loses its header and its links show flat (open or closed). The logo shrinks to its mark and the account row to
  a user icon whose menu opens to the right.
- Icons are named in `config/navigation.ts` (`NavLink.icon: NavIconName`) and resolved to components in
  `components/layout/sidebar/nav-icons.tsx` (a `Record`, so a new name without an icon fails typecheck). Names, not components,
  because `entries` cross from a Server Component to the client `NavTree`.
- Rows use `group-data-[collapsible=icon]:*` variants of the sidebar's own `group` wrapper; no JS state except the tooltip.

### Tree items (the large TOC)

| State | Look | Classes |
| :--- | :--- | :--- |
| Default | `└` muted at 50%, Tabler icon `size-4` and label `text-muted-foreground` | `font-mono text-sm py-1.5 text-muted-foreground` |
| Hover | Label `text-foreground` and nudged 4px right, hover surface | `hover:bg-accent hover:text-foreground` |
| Current | `└`, icon and label `text-foreground`, medium | `aria-current="page"`, glyph `text-foreground` |
| Group | `└`, label and a caret that rotates when collapsed (no icon); children indent | `aria-expanded`, children `pl-4` |
| Count | Mono, right aligned | `ml-auto text-xs text-muted-foreground tabular-nums` |

Keep the tree at most two levels deep; deeper structure belongs on its own page. Keyboard: arrows move, left/right
collapse and expand groups, Enter opens.

### Content conventions

- **One focal accent per screen**: the current tree item. Status uses small square dots: `bg-foreground` for "needs
  review", `bg-destructive` for blocked, `bg-muted-foreground/50` for done.
- **No big-number tiles.** Metrics are one `dl` row: mono `text-xs` label, `text-2xl font-medium` value, separated by space.
- **Selected list row is inverted** (`bg-primary text-primary-foreground`); hover is only `bg-accent`.
- **A detail sheet is context, not a route.** It opens from the page that owns the data and keeps its own open state.
- **Usage meters are flat**: a `bg-primary` fill over a `bg-muted` track (shadcn `Progress`).
- One tier denser than marketing pages on the outside only: page top `pt-10` instead of `pt-20`, sections `gap-10`
  instead of `gap-14`; T1 to T4 unchanged.

### Responsive

| Region | < lg | lg to xl | >= xl |
| :--- | :--- | :--- | :--- |
| Sidebar | Hidden below `md` (shadcn's `useIsMobile`, 768px); the trigger opens it as a left Sheet | `w-64` from `md`; the trigger collapses it to a 48px icon rail | same |
| Detail sheet | Full width, panes stacked | `42rem`, draggable wider or narrower, panes side by side from `@xl` | same |
| Logo | Main header, next to the trigger | Sidebar header | Sidebar header |
| List row | Two lines: title / id, status, time | One line | One line |
| Metrics | `grid-cols-2` | `grid-cols-4` | `grid-cols-4` |
| Header buttons | Trigger and theme toggle | same | same |

Needed components: `pnpm dlx shadcn@latest add sidebar sheet badge tabs` (from `packages/ui`). shadcn's sidebar width
comes from the `--sidebar-width` variable; change it in the theme rather than with a class.

### Implementation (apps/studio)

shadcn files in `packages/ui` are **never edited**, so `shadcn add --overwrite` and future migrations stay clean. The
Next Mono Base look is composed on top in `apps/studio/components/layout/`, grouped by area (`sidebar/`, `header/`; `ColumnHeader` and `PageHead` sit at the root). No barrel `index.ts`: import the file you need (`@/components/layout/sidebar/nav-tree`):


| Part | File | Built from |
| :--- | :--- | :--- |
| `ColumnHeader` | `column-header.tsx` | Plain `div` (`h-14 border-b px-4`) |
| `AppSidebar`, `AppSidebarBody`, `AppSidebarSection` | `sidebar/app-sidebar.tsx` | Animated `Sidebar collapsible="icon"` (`@animate-ui/react/primitives/sidebar`), `SidebarContent`, `data-sidebar="group"` / `data-sidebar="group-label"` for FLIP collapse folding |
| `NavTree` | `sidebar/nav-tree.tsx`, `sidebar/nav-icons.tsx` | `SidebarMenu` / `SidebarMenuItem` + animated `Collapsible` for groups + `data-sidebar="menu-button"` so `SidebarPrimitive.Highlight` shares one gliding spring hover surface and smoothly blurs/folds labels on icon-rail collapse; `Tooltip` names the icon in the rail |
| `ThemeToggle` | `packages/ui-patterns/src/theme-toggle.tsx` | Animate UI `ThemeTogglerButton` (`ghost`, `icon-sm`); also in the landing header and the auth rail footer |
| `DetailSheet*` | `components/shared/detail-sheet.tsx` | Compound parts over animated `Sheet` (see Detail sheets) |
| `CopyButton` | `components/shared/copy-button.tsx` | Animate UI `CopyButton` + `CopyButtonIcon` (`ghost`, `icon-sm`) |
| `UserMenu` | `sidebar/user-menu.tsx` | Animated `DropdownMenu` with `data-sidebar="menu-button"` on the trigger; items are passed as children (sign out comes from `features/auth`) |
| `DashboardBreadcrumb`, `CrumbMenu` | `header/dashboard-breadcrumb.tsx`, `header/crumb-menu.tsx` | `Breadcrumb`; global pages read like the path, scoped pages start with organization / project menus (`Crumb.options`, a `DropdownMenu`) then the page title from the nav |
| `ScopedNav` | `sidebar/scoped-nav.tsx` | Client; the sidebar sections of the current scope, over `NavTree` |
| `PageHead`, `Metrics`, `SpecList` | `page-head.tsx`, `components/shared/` | Plain markup |
| `InfoHint` | `components/shared/info-hint.tsx` | `Popover` + ghost `icon-xs` `Button`; copy comes from `config/help.ts` (also read by the Guide page). `PageHead`, `Metric` and section titles take a `hint` key |
| `ResponsiveDialog` | `components/shared/responsive-dialog.tsx` | `Dialog` from `md` up, bottom `Drawer` below (shadcn "Responsive Dialog"); `size` `md` or `lg`; `DialogActions` for the button row. Use it for every form that opens over a page; `AlertDialog` stays for confirmations |

Two consequences of not editing shadcn: the sidebar switches to a Sheet below `md` (768px, hard-coded in shadcn's hook)
instead of `lg`, and keeps one width (`16rem`); `xl:w-72` would need an arbitrary value. A fixed third column
is not part of the shell: use a detail sheet.

### Detail sheets

A record that needs more room than a row (a trace, an order, a file) opens in a right `Sheet` from the page that owns
the data. It never takes layout space and the shell keeps no state for it. Built with composition
(vercel-composition-patterns): compound parts over one `Sheet` instead of boolean props, and the open state and the
width live inside the sheet, so a page needs no provider and the header no button.

**Size.** The sheet opens fitting its content (`42rem`) and is resized by dragging its left edge (a `role="separator"` handle:
arrow keys step 32px, double click resets, minimum 384px, maximum the viewport minus 64px). The width is remembered in
`localStorage` (`storageKey` prop). Below `sm` it is always full width and the handle is hidden. The panes split on the
sheet's own width (container query `@xl`), not the viewport's.

**Three header tiers**, each a part, so every level reads on its own:

| Tier | Part | Holds |
| :--- | :--- | :--- |
| 1 The record | `DetailSheetHeader` (`h-14`) | `DetailSheetClose` (`»`), kind tile, title, copy buttons, then at the right Previous / Next as one `ButtonGroup` of `icon-sm` outline buttons (tooltip with `J` / `K`) |
| 2 A pane | `DetailSheetPaneHeader` (`h-12`, `bg-card`) | List pane: label with count, expand-all. Detail pane: kind tile, name, copy id, kind badge |
| 3 Content | `DetailSheetPaneBody` | Meta row (icon + value), tags, `Tabs`, then the tab content |

```tsx
<Sheet>
  <SheetTrigger render={<Button size="lg" />}>Open trace</SheetTrigger>
  <DetailSheetContent>
    <TraceProvider>
      <DetailSheetHeader>
        <DetailSheetClose />
        …
      </DetailSheetHeader>
      <DetailSheetSplit>
        <DetailSheetList>
          <DetailSheetPaneHeader>Spans (8)</DetailSheetPaneHeader>
          <DetailSheetPaneBody><SpanTree /></DetailSheetPaneBody>
        </DetailSheetList>
        <DetailSheetMain><SpanDetail /></DetailSheetMain>
      </DetailSheetSplit>
    </TraceProvider>
  </DetailSheetContent>
</Sheet>
```

**Interactive tree in the list pane.** Build it the way shadcn's File Tree does (ui.shadcn.com/docs/ai-elements/base/file-tree):
a node with children is a `Collapsible` whose chevron (`Button variant="ghost" size="icon-xs"`) toggles it, every node is a
`Button variant="ghost" size="sm"` that selects it, children sit in `CollapsibleContent` indented with `ml-3 border-l pl-1`.
States: hover `bg-muted` (the ghost default), selected `data-current:bg-primary/10`, selected and hovered
`data-current:hover:bg-primary/15`. A ghost `Button` paints `aria-expanded` as a hover surface, so the chevron overrides it
(`aria-expanded:bg-transparent aria-expanded:hover:bg-muted`); otherwise every open node looks hovered. In light mode
`muted`, `accent` and `secondary` are the same grey, so never tell hover from selected with those.

The selection, the open nodes and the `J` / `K` keys are shared by the tree, the detail pane and the stepper, so they live in a
provider inside the sheet (`TraceProvider` + `useTrace`), not in the shell. It mounts with the sheet and goes with it.
Other shadcn parts for similar jobs: `Accordion` (flat expandable list), `SidebarMenuSub` (navigation only), `Tabs`
(peer views of one record).

**Performance** (what made the first version laggy, and what Opik does instead): Opik's `ResizableSidePanel` writes
`style.left` straight to the element while dragging, with no React state and with the CSS transition switched off, and saves
the width on release. In the same spirit here:

- Do not animate a size. Animating `width` / `max-width` re-lays out the whole sheet on every frame (worse with a container
  query inside). Slide with `transform` and `opacity` only; resize instantly.
- No `backdrop-filter`. A blurred full-screen overlay repaints under every frame of the sheet's slide.
- Memoize the provider value and give its actions stable identities (`useMemo`, `useCallback`); attach window listeners
  once (`useEffectEvent` reads the latest state), never one per render.
- The resize handle does what Opik's does: during the drag it writes the `--detail-sheet-width` CSS variable on the sheet through
  a ref (no React state, no transition) and commits to `localStorage` on pointer up.
- Long lists or trees (hundreds of nodes) need virtualization; the 8-node demo does not.

Rules: always render a `SheetTitle` (and a `SheetDescription`, `sr-only` if needed); never put `w-*` on `SheetContent`
(use the sheet's own width); a client part that needs `window` (copy link) is its own component, because a server page
cannot pass functions or icon components to a client one. The Overview page carries a working example in
`app/(dashboard)/dashboard/_components/` (`trace-sheet.tsx` assembles `span-tree.tsx`, `span-detail.tsx`, `trace-nav.tsx`,
`trace-context.tsx` and the mock `trace-data.ts`); delete it when you add real data.

---

## 9. Motion

Interactive components use **Animate UI v2** (`@animate-ui/react` + `AnimateUIProvider` mounted inside `ThemeProvider`), which provides spring physics, shared gliding highlights (`Tabs`, `Sidebar`, `DropdownMenu`, `Select`, `Combobox`, `Tooltip`), and disclosure height/blur folding (`Accordion`, `Collapsible`). For plain CSS transitions, use Tailwind durations and easings (`ease-out` to enter, `ease-in-out` to leave):

| Interaction | Implementation / Classes |
| :--- | :--- |
| Interactive primitives (menus, dialogs, tabs, tooltips, collapsible, sidebar) | Animate UI v2 (`@workspace/ui/components/*` & `@workspace/ui/components/animate-ui/*`) |
| Sidebar hover & collapse | `SidebarPrimitive.Highlight` (shared spring highlight across `[data-sidebar="menu-button"]`, 280ms FLIP collapse & label blur) |
| Theme switch | Instant page flip (`disableTransitionOnChange`) + Animate UI `ThemeTogglerButton` (90° spin + blur icon swap) |
| Copy feedback | Animate UI `CopyButton` + `CopyButtonIcon` (blur/scale icon swap + spring press) |
| Changing numbers | `CountingNumber`, `SlidingNumber`, `ScrollingNumber` (`@workspace/ui/components/animate-ui/numbers/*`) |
| Color change (links, rows) | `transition-colors duration-150` |
| Small movement (arrow, TOC item) | `transition-transform duration-200 ease-out`, `translate-x-1` |
| Dropdown caret | `rotate-180 duration-300` |
| Reveal on enter | `tw-animate-css` fade/slide, `duration-500`/`700`, stagger `delay-75` steps |

Everything respects `prefers-reduced-motion` (`AnimateUIProvider` + `useShouldReduceMotion()` for Animate UI, and `motion-safe:` / `motion-reduce:` for CSS).

Applied in `apps/studio`:

| Pattern | Where | Implementation |
| :--- | :--- | :--- |
| Stagger on enter (slide up 8px, `duration-500`, `delay-75` steps) | Dashboard body, auth form column | `components/shared/stagger.tsx` (direct children, `*:nth-N:delay-*`). Plays once per element: Cache Components hides visited routes with `display: none` and a CSS animation restarts when its element is shown again, so each child switches its animation off when it ends (`onAnimationEnd`) and going back is instant |
| Stack logos reveal in order | Auth rail | `app/(auth)/_components/stack-showcase.tsx` (`Stagger`) |
| Glyph background (WebGL characters, cursor glow, click waves; pauses off screen, static under reduced motion) | Auth rail | `GlyphBackground` from [Animate UI](https://animate-ui.com/docs/backgrounds/glyph), installed in `packages/ui` via the `@animate-ui` registry in `components.json` |
| Sun and moon swap with a spin and zoom (`duration-300 ease-out`) | Theme toggle | `packages/ui-patterns/src/theme-toggle.tsx` |
| TOC nudge (`translate-x-1`, `duration-200`) | Sidebar nav rows | `NavTree` `RowLabel` |
| Arrow slides on hover (`translate-x-1`) | Auth switch link, 403 CTA | `group-hover` on the icon |
| Caret rotates (`duration-300`) | Collapsible nav group | `NavTree` `TreeGroup` |

| Next Mono Base twinkles (`+` → `×`), embers rise, `steps()` frames | Every logo (sidebar, headers, auth) | `AppLogo` (`motion="idle"` by default), `--animate-logo-*` |

Not used: the typing intro and ambient float (custom keyframes are allowed for the logo only), and the theme switch
stays instant.

---

## 10. Accessibility

- Focus: visible `outline` with `outline-offset-2`; never remove it without a replacement.
- `text-muted-foreground/50` is decorative; readable text uses `text-muted-foreground` or stronger.
- Anchor targets sit below the sticky nav: give them `scroll-mt-24` (`max-sm:scroll-mt-18`).
- `::selection` uses `bg-primary text-primary-foreground`.
