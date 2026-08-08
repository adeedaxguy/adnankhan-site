---
name: "Lofts Studio"
description: "A quiet editorial web system for direct, evidence-led studio work."
colors:
  paper: "#f4f0e9"
  paper-soft: "#ebe5db"
  surface: "#fbfaf7"
  ink: "#171411"
  ink-soft: "#4f4942"
  muted: "#766f67"
  muted-2: "#9a9289"
  line: "#d7cec2"
  line-soft: "#e6ded4"
  accent: "#a9432d"
  accent-deep: "#843322"
  accent-soft: "#ead2c9"
typography:
  display:
    fontFamily: '"Libertinus Math", Georgia, "Times New Roman", serif'
    fontSize: "4rem"
    fontWeight: 400
    lineHeight: 0.99
    letterSpacing: "-0.025em"
  headline:
    fontFamily: '"Libertinus Math", Georgia, "Times New Roman", serif'
    fontSize: "3.25rem"
    fontWeight: 400
    lineHeight: 1.02
  title:
    fontFamily: '"Libertinus Math", Georgia, "Times New Roman", serif'
    fontSize: "clamp(2rem, 3.25vw, 3.45rem)"
    fontWeight: 400
    lineHeight: 1
  body:
    fontFamily: '"Libertinus Math", Georgia, "Times New Roman", serif'
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.58
  label:
    fontFamily: '"Libertinus Math", Georgia, "Times New Roman", serif'
    fontSize: "0.72rem"
    fontWeight: 500
    lineHeight: 1.35
    letterSpacing: "0"
  wordmark:
    fontFamily: '"Iowan Old Style", Baskerville, "Palatino Linotype", Georgia, serif'
    fontSize: "1.32rem"
    fontWeight: 500
    lineHeight: 1
rounded:
  tight: "2px"
  control: "3px"
  standard: "4px"
  panel: "6px"
  soft: "8px"
spacing:
  page-gutter: "clamp(1.25rem, 3vw, 3rem)"
  section-space: "clamp(4.75rem, 8vw, 8.5rem)"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "0.9rem 1.5rem"
    height: "46px"
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "#fff"
    rounded: "{rounded.control}"
    height: "46px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0.9rem 1.5rem"
    height: "46px"
  editorial-field:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "0"
    padding: "0.5rem 0 0.85rem"
  diagnostic-panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
  faq-row:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    padding: "1.6rem 0"
  diagnostic-nav:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    height: "76px"
    padding: "0 clamp(1rem, 4vw, 3rem)"
  tool-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.soft}"
    padding: "clamp(1.35rem, 3vw, 2rem)"
---

# Design System: Lofts Studio

## Overview

**Creative North Star: "The Quiet Evidence Desk"**

Lofts Studio makes operational and service pages feel like a composed paper desk: warm, quiet, clear, and ready for an honest next action. The system earns authority through generous editorial type, restrained utility framing, and short visual paths rather than a dashboard-like density or fear-based visual drama.

The interface uses an editorial voice without becoming ornamental. Large serif statements hold the premise, compact explanatory text supplies the proof, and almost-square controls keep the action practical. The WordPress diagnostic route expresses this system as a direct two-column explanation-and-panel layout; it is an application of the incumbent language, not a separate security identity.

**Key Characteristics:**

- Warm paper fields, quiet tonal surfaces, and fine dividers establish a calm reading environment.
- A single Libertinus-led type voice carries display, body, form, and utility text; the Iowan Old Style wordmark is the exception.
- Small-radius, bordered panels contain actions without turning the page into a card grid.
- Near-black leads primary actions; terracotta is a deliberate signal, hover, and marker rather than a full-screen brand field.

## Colors

The palette is a low-contrast paper-and-ink field whose warm neutral range lets one earthy accent carry the small moments of emphasis.

### Primary

- **Restrained Terracotta** (`accent`): Use for short rules, dots, focus outlines, and the primary action's interactive shift. It is an accent signal, not the default CTA fill.

### Neutral

- **Warm Paper** (`paper`): The default page field and the light side of ink-led controls.
- **Soft Paper** (`paper-soft`): A slightly deeper tonal surface for quiet separation.
- **Clean Surface** (`surface`): The pale panel and form surface that sits above the page without feeling glossy.
- **Warm Ink** (`ink`): The primary reading color and default direct-action fill.
- **Soft Ink** (`ink-soft`): Long-form explanation and supporting copy.
- **Muted Utility** (`muted`, `muted-2`): Labels, secondary detail, and placeholder text.
- **Hairline Pair** (`line`, `line-soft`): Borders, section rules, and the low-contrast structure of forms and lists.

The dark theme preserves these roles by remapping the same variables rather than adding a separate visual vocabulary.

### Named Rules

**The Restrained Accent Rule.** Keep terracotta to the small evidence marks, focus treatment, and interactive states that need a precise signal. Primary commitment stays ink-led, and an otherwise quiet page may need no accent at all.

## Typography

**Display Font:** Libertinus Math (with Georgia and Times New Roman fallbacks)

**Body Font:** Libertinus Math (with Georgia and Times New Roman fallbacks)

**Wordmark Font:** Iowan Old Style (with Baskerville, Palatino Linotype, and Georgia fallbacks)

**Character:** The same bookish family is deliberately carried through display, body, controls, labels, and fields. This gives the system a composed editorial continuity; hierarchy comes from scale, line length, case, and placement instead of a separate neutral UI sans.

### Hierarchy

- **Display** (`typography.display`): The opening proposition. Keep it balanced, tightly set, and short enough to read as one statement.
- **Headline** (`typography.headline`): Major section propositions and explanatory breaks.
- **Title** (`typography.title`): Panel, form, and sectional headings that need presence without competing with the hero.
- **Body** (`typography.body`): Calm, readable evidence and supporting explanation; leads are constrained to a deliberate reading measure.
- **Label** (`typography.label`): Small uppercase utility context for eyebrow text, field labels, and metadata.
- **Wordmark** (`typography.wordmark`): The serif-italic Lofts signature; retain it as a compact identity mark rather than a display heading.

### Named Rules

**The Measured Line Rule.** Let display statements take the narrow, balanced measure established by the route; supporting copy carries the details beside or beneath it instead of widening the headline into a banner.

## Layout

The system works from a wide centered container and a fluid page gutter, with generous sectional breathing room and a persistent rhythm of one-pixel horizontal rules. Tool and diagnostic surfaces use explanation first, then the control or evidence panel; on larger viewports the diagnostic shell is a text column beside a minimum-width panel, while the layout becomes a single stack at the established tablet breakpoint. At the small-mobile breakpoint the gutter contracts and the large diagnostic display size steps down rather than allowing the opening to overflow.

Navigation is compact and horizontal at desktop scale. Tool-specific navigation stays sticky, uses a quiet translucent paper treatment, and keeps its actions in the same narrow editorial band as the content.

## Elevation & Depth

Depth is tonal and structural first: warm background shifts, hairline borders, and white-leaning surfaces do most of the separation. The soft and card shadow tokens are reserved for isolated, action-bearing panels such as the diagnostic signup and studio tool cards; the rest of the page stays flat enough for typography and rules to carry the hierarchy.

### Named Rules

**The Flat-Until-Needed Rule.** Use elevation to identify an actionable contained surface, not to decorate every section or create floating-dashboard density.

## Shapes

The geometry is deliberately near-square. Use the tight through soft radius scale for controls, panels, and cards, with the diagnostic panel using the panel radius and primary buttons using the dedicated control radius. One-pixel borders are the default edge treatment. Fully rounded forms are reserved for compact tags, related links, and circular status or list markers; they are not the primary surface language.

Subtle internal white fades and tonal layers are acceptable inside utility panels because they already appear in the implemented diagnostic and tool-card surfaces. They should remain close to the paper palette rather than become illustrative gradients.

### Named Rules

**The Quiet Corners Rule.** Keep large containers gently softened and everyday controls almost square so the system reads as precise and utilitarian, not soft or app-like.

## Components

### Buttons

**Character:** Direct, ink-led controls with small corners and enough height for practical touch use.

- **Primary:** Uses `button-primary`; it is the decisive action and shifts to terracotta on hover.
- **Ghost:** Uses `button-ghost`; it preserves the paper field and gains a surface fill on hover.
- **Editorial Link:** Uses an ink underline or an underlined text treatment for lower-emphasis navigation and resource paths.
- **Focus:** Retain the visible terracotta focus outline and offset.

### Cards / Containers

**Character:** Soft utilitarian panels rather than decorative cards.

- **Diagnostic Panel:** Uses `diagnostic-panel`: a bordered clean surface with the card shadow token, containing a short explanatory heading and an editorial form.
- **Tool Card:** Uses `tool-card`: an eight-radius surface with a faint internal tonal treatment, bounded line work, and a slight upward hover response.
- **Border Strategy:** Borders and section rules remain visible at rest; shadow is supplemental, not the primary separator.

### Inputs / Fields

**Character:** Editorial fields that leave the value and its one-pixel baseline as the visual focus.

- **Editorial Field:** Uses `editorial-field`: transparent background, no surrounding box, and a single bottom border.
- **Label:** Uses the compact uppercase label role above the field.
- **Focus:** The field's baseline darkens on focus while the global visible-focus treatment remains available for keyboard navigation.
- **Consent:** A native checkbox remains visibly boxed and adopts the accent as its control color.

### Navigation

**Character:** A compact editorial masthead that leaves the page field visually open.

- **Diagnostic Navigation:** Uses `diagnostic-nav`: sticky paper with a fine bottom rule and blur, a serif-italic wordmark, and low-density text links.
- **Responsive Treatment:** The main site navigation compacts below its established desktop threshold; the diagnostic opening itself remains content-first and stacks its panel at the tablet threshold.

### FAQ

**Character:** An unobtrusive evidence list rather than a boxed accordion.

- **FAQ Row:** Uses `faq-row`: a bottom hairline, a display-style question, and a small plus that rotates when the native details element is open.
- **Answer:** Supporting text stays in the body role and keeps a limited reading measure.

## Do's and Don'ts

### Do:

- **Do** use warm paper, clean surfaces, and hairline rules to make dense information feel calm.
- **Do** lead with a concise editorial proposition, then place the explanation and action in a clear visual sequence.
- **Do** make a contained action panel visibly practical with a border, small radius, and only the elevation it needs.
- **Do** reserve terracotta for a small rule, marker, focus state, or meaningful interaction shift.
- **Do** preserve visible keyboard focus and native form affordances.

### Don't:

- **Don't** turn every primary action terracotta; direct commitments are ink-led in the incumbent system.
- **Don't** replace the fine-divider structure with borderless, heavily elevated dashboard cards.
- **Don't** use oversized radii or pervasive pills for core controls and containers.
- **Don't** make utility panels loud with high-saturation fills, dramatic gradients, or fear-based visual urgency.
