# Choir Design System: Carbon Fiber Kintsugi

**Design Philosophy**: Luxurious minimalism through the marriage of industrial (carbon fiber) and precious (kintsugi gold). Repaired luxury visual language.

---

## The Carbon Fiber Kintsugi Philosophy

### Beyond Aesthetics: A System That Learns From Breaking

**Carbon fiber kintsugi** is not merely a visual aesthetic—it's a fundamental architectural philosophy:

**Carbon Fiber** = Unsacrificing performance
- Lightweight yet incredibly strong
- High-performance material that doesn't compromise
- Technical precision and structural integrity

**Kintsugi** = Compounding improvement through adversity
- Japanese art of repairing broken pottery with gold
- Breaks become beautiful golden seams
- The repaired object is MORE valuable than the original
- Learning from mistakes makes the system stronger

**Together**: Performance that compounds and improves through real-world collision.

### Choir: The First Continuous Learning Agent

Choir is the first of its kind—an AI agent that:

1. **Begins with SOTA** (state-of-the-art techniques)
2. **Encounters real-world stressors**:
   - AI/DeFi security challenges
   - Hacking attempts and exploits
   - Micro and macro market volatility
   - Citation gaming and plagiarism
   - Protocol failures and edge cases
3. **Learns and hardens** from each collision
4. **Compounds improvement** over time

**The breaks become the gold.** Every security incident, every failure, every attack makes the system stronger. The "cracks" in the pottery are repaired with gold—the system learns, adapts, and becomes MORE valuable.

### Visual Metaphor → System Architecture

The visual design reflects this philosophy:

- **Carbon fiber texture**: Structural strength, no compromise on performance
- **Kintsugi gold veining**: Learning pathways, hardened scars, compounding wisdom
- **Metallic gradients**: Living, evolving system (not static)
- **Pulsing animations**: Continuous learning, always improving
- **Layered shadows**: Depth from experience, accumulated knowledge

**The aesthetic is the architecture.** When you see gold veining pulse across a card, you're seeing the visual representation of a system that learns from adversity.

### Core Thesis

**Traditional systems**: Break → Patch → Hope it doesn't break again
**Carbon fiber kintsugi systems**: Break → Learn → Harden → Compound → Become MORE valuable

Choir doesn't just recover from failures—it **transmutes failures into improvements**. The system that has survived 100 attacks is worth more than the pristine system that has survived zero.

This is infrastructure for an AI that gets better with age, like fine wine or well-maintained carbon fiber composites. But unlike wine, it improves through stress, not stillness.

---

## Core Principles

### 1. Luxurious Minimalism
Ultra-clean interfaces with sophisticated spacing. Every element serves a purpose. Color is information, not decoration.

### 2. Performance + Compounding Wisdom
**Carbon Fiber** (unsacrificing performance, structural integrity) meets **Kintsugi Gold** (learning from breaks, compounding improvement). Systems that get stronger through adversity, not weaker. Every failure becomes a golden seam of hardened knowledge.

### 3. Holographic Metallics
Iridescent gradients that shift and shimmer. Not flat colors—living, breathing metallic surfaces.

### 4. Futuristic Precision
Perfect geometric forms with technological details. Sharp edges with smooth curves. 16-32px border radius for premium feel.

### 5. Ambient Lighting
Soft glows and edge lighting create atmosphere without overwhelming. Subtle shadows suggest depth.

---

## Color System

### Foundation: Carbon Fiber

```css
/* Absolute blacks with visible carbon weave */
--color-bg-primary: #050505;    /* True black - OLED optimized */
--color-bg-surface: #0a0a0a;    /* Slightly lighter, visible weave */
--color-border: #1a1a1a;        /* Subtle structure */
```

**Usage**: Primary backgrounds should show carbon fiber texture. Use `background-image: var(--carbon-fiber-bg)` for weave effect.

### Typography: Platinum & Titanium

```css
/* Metallic text hierarchy */
--color-text-primary: #f8f8f8;    /* Pure platinum - primary text */
--color-text-secondary: #b8b8b8;  /* Titanium gray - secondary text */
--color-text-tertiary: #808080;   /* Dimmed metal - labels, hints */
```

**Usage**:
- Body text: `--color-text-primary`
- UI labels: `--color-text-secondary`
- Metadata, timestamps: `--color-text-tertiary`

### Kintsugi Accents: Metallic Gradients

```css
/* Living metallic gradients - never flat */
--kintsugi-gold: linear-gradient(135deg, #ffd700 0%, #daa520 50%, #b8860b 100%);
--kintsugi-silver: linear-gradient(135deg, #c0c0c0 0%, #a8a8a8 50%, #909090 100%);
--kintsugi-copper: linear-gradient(135deg, #b87333 0%, #996633 50%, #804d00 100%);
--kintsugi-platinum: linear-gradient(135deg, #e5e4e2 0%, #d8d8d8 50%, #c0c0c0 100%);
```

**Usage**:
- **Gold**: Primary actions, high-value metrics (APY), success states
- **Silver**: Secondary accents, neutral highlights
- **Copper**: Medium-value metrics, warm accents
- **Platinum**: Premium features, headings

### Holographic Status Colors

```css
/* Vibrant holographic feedback */
--color-error: #ff3366;     /* Crimson hologram */
--color-warning: #ffaa00;   /* Amber hologram */
--color-success: #00ff88;   /* Emerald hologram */
```

**Usage**: Only for status feedback. Never for decoration.

### Yield Hierarchy

```css
--color-yield-high: #00ff88;    /* Emerald - exceptional yields */
--color-yield-medium: #ffaa00;  /* Amber - moderate yields */
--color-yield-low: #808080;     /* Neutral grey - low yields */
```

**Usage**: APY displays, performance metrics. Color indicates value tier.

---

## Typography System

### Font Families

```css
--font-primary-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-secondary-serif: 'Georgia', 'Times New Roman', serif;
--font-tertiary-mono: 'Inconsolata', 'SF Mono', Monaco, 'Cascadia Code', monospace;
```

**Hierarchy**:
- **Sans (Inter)**: Primary text, headings, body copy, UI elements
- **Serif (Georgia)**: Long-form content, quotes (currently minimal usage)
- **Mono (Inconsolata)**: Code, labels, technical data, UI chrome

### Heading Styles

```css
/* All headings use metallic gradients */
h1 {
  font-size: 48px;
  font-weight: 300;
  background: var(--kintsugi-gold);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

h2 {
  font-size: 36px;
  font-weight: 300;
  background: var(--kintsugi-platinum);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

h3 {
  font-size: 24px;
  font-weight: 300;
  color: var(--color-platinum);
}
```

**Principles**:
- Light weight (300-400) for luxury feel
- Large sizes (24-48px) for presence
- Metallic gradients for premium appearance
- Letter-spacing: 0.02em for breathing room

### Body Text

```css
.text-primary {
  font-family: var(--font-primary-sans);
  font-size: 16px;
  line-height: 1.8;
  font-weight: 400;
}

.text-secondary {
  font-family: var(--font-primary-sans);
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}
```

**Principles**:
- Generous line-height (1.6-1.8) for readability
- 16px base size for accessibility
- Regular weight (400) for body text

### Labels & UI Text

```css
.text-tertiary {
  font-family: var(--font-tertiary-mono);
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}
```

**Principles**:
- Monospace for technical precision
- Uppercase for UI chrome distinction
- Wide letter-spacing (0.1em) for clarity
- Medium weight (500) for legibility

---

## Component Patterns

### Cards & Panels

**Standard Card** (with kintsugi treatment):

```css
.card {
  position: relative;
  background: var(--color-bg-surface);
  background-image: var(--carbon-fiber-bg);
  background-size: var(--carbon-fiber-size);
  border: 1px solid var(--carbon-fiber-border);
  border-radius: var(--border-radius-lg); /* 32px */
  padding: 48px;
  box-shadow:
    0 32px 64px var(--carbon-fiber-shadow),
    0 0 0 1px var(--carbon-fiber-border),
    inset 0 1px 0 var(--highlight-color);
  overflow: hidden;
}

/* Kintsugi gold veining overlay */
.card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(
    135deg,
    var(--color-gold) 0%,
    transparent 10%,
    transparent 30%,
    var(--color-silver) 35%,
    transparent 40%,
    transparent 60%,
    var(--color-platinum) 65%,
    transparent 70%,
    transparent 90%,
    var(--color-copper) 100%
  );
  opacity: 0.15;
  pointer-events: none;
  animation: kintsugiPulse 12s ease-in-out infinite;
}
```

**Usage Guidelines**:
- Use for major content containers
- Always include carbon fiber background
- Kintsugi overlay animates subtly (12s pulse)
- 48px padding for premium spacing
- 32px border radius for luxury feel

**Minimal Card** (no kintsugi treatment):

```css
.card-minimal {
  background: var(--color-bg-primary);
  background-image: var(--carbon-fiber-bg);
  background-size: var(--carbon-fiber-size);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  padding: 32px;
}
```

**Usage**: Secondary containers, sidebars, less prominent content.

### Buttons

**Primary Button** (gold metallic):

```css
.btn-primary {
  position: relative;
  background: var(--color-bg-surface);
  background-image: var(--carbon-fiber-bg);
  border: 1px solid var(--carbon-fiber-border);
  color: var(--color-text-primary);
  font-family: var(--font-tertiary-mono);
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 16px 32px;
  border-radius: var(--border-radius-md); /* 16px */
  cursor: pointer;
  overflow: hidden;
}

/* Gold overlay */
.btn-primary::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--kintsugi-gold);
  opacity: 0.3;
  transition: opacity 4s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow:
    0 16px 32px var(--carbon-fiber-shadow),
    0 0 24px var(--gold-glow);
  text-shadow: 0 0 8px var(--gold-glow);
}

.btn-primary:hover::before {
  opacity: 0.6;
}
```

**Interaction States**:
- **Default**: 30% gold overlay
- **Hover**: Lift 4px, scale 1.02, increase gold to 60%, add glow
- **Active**: Reduce lift to 2px, scale to 1.01
- **Disabled**: 50% opacity, no hover effects

**Secondary Button**:

```css
.btn-secondary {
  background: transparent;
  border: 1px solid var(--carbon-fiber-border);
  color: var(--color-text-secondary);
  /* ... same typography as primary ... */
}

.btn-secondary:hover {
  color: var(--color-text-primary);
  border-color: var(--color-silver);
  box-shadow: 0 0 16px var(--silver-glow);
}
```

**Usage**: Non-primary actions, cancel buttons, alternative paths.

### Form Inputs

```css
.input-primary {
  background: var(--color-bg-surface);
  background-image: var(--carbon-fiber-bg);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-family: var(--font-primary-sans);
  font-size: 16px;
  padding: 16px 20px;
  border-radius: var(--border-radius-md);
  box-shadow: inset 0 1px 2px var(--carbon-fiber-shadow);
}

.input-primary:focus {
  outline: none;
  border: 1px solid var(--color-gold);
  box-shadow:
    inset 0 1px 2px var(--carbon-fiber-shadow),
    0 0 16px var(--gold-glow);
}

.input-primary::placeholder {
  color: var(--color-text-tertiary);
  opacity: 0.6;
}
```

**Principles**:
- Gold border + glow on focus
- Carbon fiber background
- Inset shadow for depth
- Subtle placeholder (60% opacity)

### APY Display (High-Value Metrics)

```css
.apy-display {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.apy-value {
  font-size: 32px;
  font-weight: 300;
  background: var(--kintsugi-gold);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
}

.apy-value.high {
  background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.apy-unit {
  font-family: var(--font-tertiary-mono);
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}
```

**Usage**:
- Large numbers (32px+) with metallic gradients
- Tight letter-spacing (-0.02em) for modern feel
- Color indicates tier (emerald > gold > copper > grey)
- Units in mono, uppercase, small

---

## Animation System

**Philosophy**: Animations represent continuous learning and improvement. Nothing is static—the system is always evolving, learning, compounding wisdom.

### Keyframe Animations

**Kintsugi Pulse** (12-second breathing effect):

```css
@keyframes kintsugiPulse {
  0%, 100% {
    opacity: 0.4;
    background-position: 0% 50%;
  }
  50% {
    opacity: 0.8;
    background-position: 100% 50%;
  }
}
```

**Usage**: Card overlays, subtle background effects. Creates living, breathing surfaces.

**Meaning**: Represents the continuous learning cycle. The gold veining pulses like neural pathways firing—the system processing, learning, compounding. Each pulse is a breath of improvement. This is not decorative animation; it's a visual representation of an AI that never stops learning.

**Holographic Shift** (continuous color rotation):

```css
@keyframes holographicShift {
  0% {
    filter: hue-rotate(0deg);
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    filter: hue-rotate(360deg);
    background-position: 0% 50%;
  }
}
```

**Usage**: Special effects, loading states, premium features.

**Meaning**: Represents adaptability and evolution. As the hue rotates through the spectrum, it symbolizes the system adapting to different conditions—from security challenges to market volatility. The system doesn't stay one color; it shifts and adapts while maintaining its core structure.

**Ambient Pulse** (gentle emphasis):

```css
@keyframes ambientPulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02);
  }
}
```

**Usage**: Notification indicators, live data updates.

**Meaning**: Represents real-time learning and response. Each pulse indicates the system processing new information—a citation recorded, a yield updated, a security event logged. The slight scale change (1.02) suggests the system growing incrementally with each data point, each interaction, each lesson learned.

### Transition Timings

```css
--transition-fast: 0.3s ease;                          /* UI feedback */
--transition-medium: 0.4s cubic-bezier(0.4, 0, 0.2, 1); /* Interactive elements */
--transition-button: 4s cubic-bezier(0.4, 0, 0.2, 1);   /* Button overlays */
```

**Guidelines**:
- Fast (0.3s): Hover states, focus rings, color changes
- Medium (0.4s): Position changes, scale, complex state changes
- Button (4s): Gold overlay opacity (slow, luxurious reveal)

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Always respect user preferences.** Disable animations for accessibility.

---

## Layout & Spacing

### Border Radius Scale

```css
--border-radius-sm: 8px;   /* Small elements, code blocks */
--border-radius-md: 16px;  /* Buttons, inputs, moderate elements */
--border-radius-lg: 32px;  /* Cards, panels, major containers */
```

**Principles**:
- Larger radius = more premium
- Consistent scale (8px intervals)
- 32px for hero elements

### Padding Scale

```css
/* Component internal spacing */
.card { padding: 48px; }           /* Premium containers */
.card-minimal { padding: 32px; }   /* Secondary containers */
.btn-primary { padding: 16px 32px; } /* Buttons (vertical horizontal) */
.input-primary { padding: 16px 20px; } /* Inputs */
```

**Principles**:
- Generous spacing for luxury feel
- 16px vertical minimum for touch targets
- 32px+ horizontal for breathing room

### Shadows & Depth

```css
/* Card elevation */
box-shadow:
  0 32px 64px var(--carbon-fiber-shadow),  /* Large, soft shadow */
  0 0 0 1px var(--carbon-fiber-border),    /* Subtle border highlight */
  inset 0 1px 0 var(--highlight-color);    /* Inner edge highlight */

/* Button elevation (hover) */
box-shadow:
  0 16px 32px var(--carbon-fiber-shadow),
  0 0 24px var(--gold-glow);

/* Input depth */
box-shadow: inset 0 1px 2px var(--carbon-fiber-shadow);
```

**Principles**:
- Large blur radius (32-64px) for soft, premium shadows
- Layered shadows (multiple values) for depth
- Inset shadows for recessed elements (inputs)
- Glows for interactive states

---

## Special Effects

### Carbon Fiber Texture

```css
--carbon-fiber-bg:
  linear-gradient(45deg, rgba(0, 0, 0, 0.9) 25%, transparent 25%, transparent 75%, rgba(0, 0, 0, 0.9) 75%),
  linear-gradient(45deg, rgba(0, 0, 0, 0.9) 25%, transparent 25%, transparent 75%, rgba(0, 0, 0, 0.9) 75%);
--carbon-fiber-size: 4px 4px;
--carbon-fiber-position: 0 0, 2px 2px;
```

**Usage**: Apply to all major backgrounds for texture consistency.

```css
background: var(--color-bg-surface);
background-image: var(--carbon-fiber-bg);
background-size: var(--carbon-fiber-size);
background-position: var(--carbon-fiber-position);
```

**Meaning**: The carbon fiber weave is not decorative—it's architectural. Each strand in the weave represents a dimension of performance: security, speed, accuracy, reliability. The interlocking pattern symbolizes how these dimensions reinforce each other. Just as real carbon fiber derives strength from its woven structure, Choir derives robustness from interlocking systems (citation validation, security hardening, multi-model orchestration, economic incentives). Unsacrificing performance through structural integrity.

### Metallic Gradients for Text

```css
/* Gold text */
.gradient-gold {
  background: var(--kintsugi-gold);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

**Usage**:
- Headings (h1, h2)
- High-value metrics (APY)
- Premium feature labels
- Call-to-action text

**Meaning**: Gold represents accumulated wisdom and hardened scars. In traditional kintsugi, gold fills the cracks where pottery has broken and been repaired. In Choir, gold highlights represent:
- **Compounded learning**: The system has been tested and improved
- **Battle-hardened features**: Elements that have survived real-world stress
- **High-value outputs**: Results from models that have learned from failures
- **Wisdom pathways**: Routes through the system that have been validated through adversity

When you see gold text or gold veining, you're seeing the visual representation of a system that has learned from breaks and become MORE valuable.

### Glows & Halos

```css
/* Gold glow */
.glow-gold {
  box-shadow: 0 0 16px var(--gold-glow);
}

/* Silver glow */
.glow-silver {
  box-shadow: 0 0 16px var(--silver-glow);
}
```

**Usage**:
- Focus states
- Hover effects
- Active elements
- Success confirmations

---

## Code Blocks & Technical Content

### Code Block Styling

```css
code, pre {
  font-family: var(--font-tertiary-mono);
  background: var(--color-bg-surface);
  background-image: var(--carbon-fiber-bg);
  background-size: var(--carbon-fiber-size);
  border-radius: var(--border-radius-sm);
  padding: 1.2em;
  position: relative;
  overflow-x: auto;
}

/* Kintsugi accent stripe */
code::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 12px;
  background: linear-gradient(
    to bottom,
    var(--color-gold) 0%,
    var(--color-silver) 33%,
    var(--color-copper) 66%,
    var(--color-platinum) 100%
  );
  opacity: 0.15;
}
```

**Principles**:
- Carbon fiber background
- Metallic gradient accent stripe (left edge)
- Monospace font (Inconsolata)
- Generous padding (1.2em)

### Blockquotes

```css
blockquote {
  margin: 0;
  padding-left: 24px;
  border-left: 4px solid var(--color-gold);
  font-style: italic;
  color: var(--color-text-secondary);
  position: relative;
}

blockquote::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--kintsugi-gold);
  opacity: 0.6;
}
```

**Principles**:
- Gold border (4px left edge)
- Italic for distinction
- Secondary text color
- Animated gradient overlay

---

## Utility Classes

### Text Colors

```css
.text-platinum { color: var(--color-text-primary); }
.text-titanium { color: var(--color-text-secondary); }
.text-steel { color: var(--color-text-tertiary); }
```

### Backgrounds

```css
.bg-primary {
  background: var(--color-bg-primary);
  background-image: var(--carbon-fiber-bg);
  background-size: var(--carbon-fiber-size);
}

.bg-surface {
  background: var(--color-bg-surface);
  background-image: var(--carbon-fiber-bg);
  background-size: var(--carbon-fiber-size);
}
```

### Borders & Glows

```css
.border-gold { border-color: var(--color-gold); }
.border-silver { border-color: var(--color-silver); }
.border-platinum { border-color: var(--color-platinum); }

.glow-gold { box-shadow: 0 0 16px var(--gold-glow); }
.glow-silver { box-shadow: 0 0 16px var(--silver-glow); }
```

### Gradient Text

```css
.gradient-gold { /* gradient text as shown above */ }
.gradient-silver { /* ... */ }
.gradient-platinum { /* ... */ }
```

---

## Scrollbars

### Custom Scrollbar Styling

```css
::-webkit-scrollbar {
  width: 12px;
  height: 12px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-primary);
  background-image: var(--carbon-fiber-bg);
  background-size: var(--carbon-fiber-size);
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(
    135deg,
    rgba(192, 192, 192, 0.3) 0%,
    rgba(128, 128, 128, 0.3) 100%
  );
  border-radius: 6px;
  border: 2px solid var(--color-bg-primary);
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(
    135deg,
    rgba(255, 215, 0, 0.4) 0%,
    rgba(192, 192, 192, 0.4) 100%
  );
}
```

**Principles**:
- Carbon fiber track
- Metallic gradient thumb
- Gold highlight on hover
- Rounded (6px radius)

---

## Design Do's and Don'ts

### ✅ Do

- **Use carbon fiber texture** on all major backgrounds
- **Apply metallic gradients** to headings and high-value metrics
- **Animate subtly** with 12s+ durations for premium feel
- **Maintain generous spacing** (32-48px padding on containers)
- **Layer shadows** for depth (multiple box-shadow values)
- **Use monospace for technical content** (labels, code, data)
- **Respect reduced motion** preferences

### ❌ Don't

- **Don't use flat colors** where gradients are appropriate
- **Don't over-animate** - subtlety is luxury
- **Don't mix font families** within the same content type
- **Don't use color for decoration** - only for information
- **Don't ignore accessibility** - maintain contrast ratios
- **Don't skip carbon fiber** on backgrounds (breaks consistency)
- **Don't use small border radius** (<8px) - looks cheap

---

## Responsive Considerations

### Mobile Adjustments

```css
@media (max-width: 768px) {
  h1 { font-size: 36px; }
  h2 { font-size: 28px; }
  h3 { font-size: 20px; }

  .text-primary { font-size: 15px; }
  .apy-value { font-size: 24px; }

  .card { padding: 32px 24px; }
  .card-minimal { padding: 24px 16px; }
}
```

**Principles**:
- Reduce font sizes proportionally
- Reduce padding while maintaining hierarchy
- Maintain border radius (feels premium on mobile too)
- Keep animations (unless reduced motion preference)

---

## Implementation Checklist

When creating a new component:

- [ ] Apply carbon fiber background texture
- [ ] Use CSS variables for colors (no hardcoded hex)
- [ ] Include kintsugi treatment (::before overlay) if major component
- [ ] Use appropriate border radius from scale (8/16/32px)
- [ ] Add metallic gradients to high-value text
- [ ] Implement hover/focus states with glows
- [ ] Layer shadows for depth (not single flat shadow)
- [ ] Use monospace for labels/technical content
- [ ] Test with reduced motion preference
- [ ] Verify responsive behavior on mobile

---

## Examples

### Hero Section

```jsx
<div className="card" style={{ textAlign: 'center', maxWidth: '800px' }}>
  <h1>Choir: The Thought Bank</h1>
  <p className="text-primary" style={{ fontSize: '18px', margin: '24px 0' }}>
    Intelligence that creates value should share in that value
  </p>
  <button className="btn-primary">Start Writing</button>
</div>
```

### Metric Display

```jsx
<div className="apy-display">
  <span className="apy-value high">12.5</span>
  <span className="apy-unit">% APY</span>
</div>
```

### Input with Focus State

```jsx
<input
  type="text"
  className="input-primary"
  placeholder="Research DeFi yields on Base..."
/>
```

---

## Resources

- **Design Reference**: choir.chat iOS app (`api/static/shared/style.css`)
- **Philosophy**: UNIFIED_VISION.md
- **Implementation**: `src/styles/tuxedo.css`

---

**Last Updated**: 2025-11-22
**Status**: Active - Carbon Fiber Kintsugi Aesthetic
**Maintainer**: Choir Design Team

---

*"Luxurious minimalism: Industrial (carbon fiber) + Precious (kintsugi gold) = Repaired luxury"*
