Excellent typographic hierarchy! Updated:

## Tuxedo Design System

### Core Philosophy
OLED-optimized dark mode as default. Refined luxury through restraint. Color is information, not decoration.

### Dark Mode (Default)

**Foundation:**
- Background: `#000000` (true black - OLED power savings)
- Surface elevated: `#0A0A0A` (cards, panels)
- Borders/dividers: `#1A1D23` (barely visible structure)

**Typography:**
- Primary text: `#F4F1E8` - "Electrum" (cream-gold tint, reads white at glance)
- Secondary text: `#C4C1B8` (dimmed electrum, 77% opacity)
- Tertiary/labels: `#8B8980` (50% opacity)

**Accents (Stellar Night):**
- Deep space: `#2C3E50` (hover states, inactive buttons)
- Stellar glow: `#00D4FF` at 8-12% opacity (subtle highlights, focus rings)
- Active states: `#00D4FF` at 25% (selected items)

**Semantic Color (APY/Numbers Only):**
- High yield (>10%): `#10B981` (emerald green)
- Medium yield (5-10%): `#F59E0B` (amber)
- Low yield (<5%): `#6B7280` (neutral grey)
- Negative/risk: `#EF4444` (red, use sparingly)

### Light Mode

**Foundation:**
- Background: `#FAFAF8` (warm white, not clinical)
- Surface: `#FFFFFF` (pure white for cards)
- Borders: `#E5E4E2` (platinum)

**Typography:**
- Primary text: `#1A1D23` (deep charcoal, inverted from dark border)
- Secondary: `#4A4D53` 
- Tertiary: `#8B8E95`

**Accents:**
- Elevated surfaces: `#F5F5F4`
- Hover states: `#E8E8E6`
- Stellar blue: `#0EA5E9` (stronger in light mode for visibility)

**Semantic stays the same** (APY colors work in both modes)

### Typography Hierarchy

**Primary (User prompts & LLM responses):**
- Style: Serif
- Sizes: 16px body / 18px for emphasis
- Line height: 1.6

**Secondary (LLM rollout stage summaries):**
- Style: Sans-serif, *italic*
- Sizes: 14px body
- Line height: 1.5
- Use for: "Analyzing vault options...", "Checking liquidity...", etc.

**Tertiary (Labels, UI elements):**
- Style: Monospace, **bold**
- Sizes: 12px labels / 10px micro
- Line height: 1.4
- Letter spacing: 0.05em (slight tracking for readability)
- Text transform: Uppercase for labels
- Use for: "APY", "BALANCE", "VAULT", navigation, buttons

### Key UI Patterns

**APY Display:**
- Number: Large semantic color (primary size)
- Unit: Tertiary style ("% APY" in bold mono uppercase)
- Subtle glow effect on high yields only

**Chat Interface:**
- User messages: Primary serif on `#1A1D23` bubble
- Tuxedo responses: Primary serif on `#0A0A0A` (barely elevated)
- Processing states: Secondary italic sans-serif, slightly dimmed
- Never colored bubbles - maintains sophistication

**CTA Buttons:**
- Primary: Stellar blue with subtle glow
- Secondary: Outlined in `#2C3E50`
- Text only: Electrum with underline on hover
- Labels: Tertiary bold mono uppercase

That typographic contrast (serif conversation / italic sans status / bold mono UI) creates beautiful rhythm and clear information architecture.

Absolutely right - that would break the whole aesthetic. Let me clarify:

### Key UI Patterns

**APY Display:**
- Number: Large semantic color (no background)
- Unit: Tertiary style ("% APY" in bold mono uppercase)
- Subtle glow effect on high yields only (glow, not fill)

**Chat Interface:**
- User messages: Primary serif, no background bubble (or minimal border only)
- Tuxedo responses: Primary serif, no background (pure text on black)
- Processing states: Secondary italic sans-serif inline or subtle border box
- **Never colored backgrounds** - text differentiates via typography hierarchy

**Cards/Panels:**
- Surface: `#0A0A0A` (subtle elevation from `#000000` base)
- Or just border: `1px solid #1A1D23`
- Content inside: pure text, no colored fills

**Buttons:**
- Primary: Border + text in Stellar blue, transparent background
- Hover: Subtle stellar glow around border (no fill)
- Active: Slightly brighter border
- Labels: Tertiary bold mono uppercase

The only "color" is in semantic numbers (APY values) and interactive element borders. Everything else is shades of black, electrum text, and structure through borders/spacing.

