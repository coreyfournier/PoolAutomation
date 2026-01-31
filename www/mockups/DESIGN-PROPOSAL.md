# Pool Automation UI Redesign - "Hydrological Control" Dark Theme

## Selected Design

**Theme:** "Hydrological Control" (Dark)
**File:** `proposed-ui.html`

**Aesthetic Inspiration:** Scientific instruments, SCADA control systems, depth charts

---

## Typography

| Role | Font | Fallback |
|------|------|----------|
| Display/Headers | Young Serif | Georgia, serif |
| Data/UI | Martian Mono | Courier New, monospace |

**Google Fonts import:**
```html
<link href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Martian+Mono:wght@300;400;500;600&display=swap" rel="stylesheet">
```

---

## Color Palette

```css
:root {
    /* Backgrounds */
    --bg-deep: #0A1628;           /* Main background */
    --bg-card: #0F2133;           /* Card surfaces */
    --bg-card-hover: #142a42;     /* Card hover state */
    --bg-elevated: #1a3550;       /* Elevated elements */

    /* Accents */
    --accent-cyan: #00CED1;       /* Primary - water/tech */
    --accent-cyan-glow: rgba(0, 206, 209, 0.3);
    --accent-amber: #F4A460;      /* Secondary - warmth */
    --accent-amber-glow: rgba(244, 164, 96, 0.3);

    /* Status */
    --status-active: #20B2AA;     /* Running/Online */
    --status-inactive: #FF6B6B;   /* Stopped/Offline */
    --status-warning: #FFD93D;    /* Attention needed */

    /* Text */
    --text-primary: #E8F4F8;      /* Main text */
    --text-secondary: #8BA9B3;    /* Secondary text */
    --text-muted: #4A6572;        /* Muted/labels */

    /* Borders */
    --border-subtle: rgba(0, 206, 209, 0.15);
    --border-accent: rgba(0, 206, 209, 0.4);
}
```

---

## ApexCharts Dark Theme Configuration

The existing ApexCharts are preserved and styled to match the dark theme:

```typescript
// stats.component.ts - Updated chart configuration
getChart(categoryData: any, seriesData: any): any {
    return {
        chart: {
            type: 'line',
            height: 200,
            width: '100%',
            id: 'temperature-chart',
            background: 'transparent',
            fontFamily: "'Martian Mono', 'Courier New', monospace",
            toolbar: { show: false },
            zoom: { enabled: false },
            animations: {
                enabled: true,
                easing: 'easeinout',
                speed: 800,
                animateGradually: {
                    enabled: true,
                    delay: 150
                }
            }
        },
        series: seriesData,
        colors: ['#00CED1', '#F4A460', '#20B2AA', '#FFD93D'],
        stroke: {
            curve: 'smooth',
            width: 2
        },
        markers: {
            size: 0,
            hover: { size: 5 }
        },
        xaxis: {
            categories: categoryData,
            tickAmount: 1,
            type: 'category',
            labels: {
                show: true,
                style: {
                    colors: '#8BA9B3',
                    fontSize: '10px',
                    fontFamily: "'Martian Mono', monospace"
                }
            },
            axisBorder: { color: 'rgba(0, 206, 209, 0.15)' },
            axisTicks: { color: 'rgba(0, 206, 209, 0.15)' }
        },
        yaxis: {
            labels: {
                style: {
                    colors: '#8BA9B3',
                    fontSize: '10px',
                    fontFamily: "'Martian Mono', monospace"
                },
                formatter: (val) => val + '°F'
            }
        },
        grid: {
            borderColor: 'rgba(0, 206, 209, 0.1)',
            strokeDashArray: 3
        },
        legend: {
            position: 'top',
            horizontalAlign: 'right',
            floating: true,
            offsetY: -8,
            labels: { colors: '#8BA9B3' },
            markers: { width: 8, height: 8, radius: 2 },
            itemMargin: { horizontal: 12 }
        },
        tooltip: {
            theme: 'dark',
            y: { formatter: (val) => val + '°F' }
        },
        title: {
            text: 'Avg Temperature by Hour',
            align: 'left',
            style: {
                fontSize: '12px',
                fontWeight: 400,
                fontFamily: "'Young Serif', Georgia, serif",
                color: '#E8F4F8'
            }
        }
    };
}
```

**CSS overrides for ApexCharts tooltips:**
```css
.apexcharts-tooltip {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
}

.apexcharts-tooltip-title {
    background: var(--bg-card) !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    font-family: var(--font-mono) !important;
    color: var(--text-primary) !important;
}
```

---

## Layout System

Replace Bootstrap 3 with CSS Grid:

```css
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: var(--space-lg);
}

/* Tile spans */
.tile--full { grid-column: span 12; }
.tile--half { grid-column: span 6; }
.tile--third { grid-column: span 4; }
.tile--quarter { grid-column: span 3; }

/* Responsive */
@media (max-width: 1024px) {
    .tile--half { grid-column: span 12; }
    .tile--third { grid-column: span 6; }
}

@media (max-width: 640px) {
    .tile--third { grid-column: span 12; }
}
```

---

## Animation System

### Page Load Orchestration
```css
/* Header entrance */
.app-header {
    animation: fadeSlideDown 0.6s ease-out;
}

@keyframes fadeSlideDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Staggered tile entrance */
.tile {
    opacity: 0;
    animation: tileEnter 0.5s ease-out forwards;
}

@keyframes tileEnter {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.tile:nth-child(1) { animation-delay: 0.1s; }
.tile:nth-child(2) { animation-delay: 0.15s; }
.tile:nth-child(3) { animation-delay: 0.2s; }
/* ... etc */
```

### Status Indicator Pulse
```css
.status-dot {
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--status-active); }
    50% { opacity: 0.6; box-shadow: 0 0 16px var(--status-active); }
}
```

### Hover Transitions
```css
.tile {
    transition:
        transform 250ms ease-out,
        box-shadow 250ms ease-out,
        border-color 250ms ease-out;
}

.tile:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border-color: var(--border-accent);
}
```

---

## Atmospheric Background

Topographic contour pattern suggesting water depth charts:

```css
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        /* Radial glow top-left */
        radial-gradient(ellipse 80% 50% at 20% 20%,
            rgba(0, 206, 209, 0.08) 0%, transparent 50%),
        /* Radial glow bottom-right */
        radial-gradient(ellipse 60% 40% at 80% 80%,
            rgba(244, 164, 96, 0.05) 0%, transparent 50%),
        /* Topographic lines - horizontal */
        repeating-linear-gradient(0deg,
            transparent, transparent 60px,
            rgba(0, 206, 209, 0.03) 60px,
            rgba(0, 206, 209, 0.03) 61px),
        /* Topographic lines - diagonal */
        repeating-linear-gradient(35deg,
            transparent, transparent 80px,
            rgba(0, 206, 209, 0.02) 80px,
            rgba(0, 206, 209, 0.02) 81px);
    pointer-events: none;
    z-index: 0;
}
```

---

## Component Structure

### Tile Pattern
```html
<div class="tile tile--half">
    <div class="tile__header">
        <h2 class="tile__title">Title</h2>
        <div class="tile__actions">
            <button class="btn">Action</button>
        </div>
    </div>
    <div class="tile__body">
        <!-- Content -->
    </div>
</div>
```

### Large Metric Display (Chemistry)
```html
<div class="metric">
    <div class="metric__label">pH Level</div>
    <div class="metric__value">
        7.4<span class="metric__unit">pH</span>
    </div>
    <div class="metric__range">Optimal: 7.2 - 7.6</div>
</div>
```

### Sensor Cards (Temperature)
```html
<div class="sensor-grid">
    <div class="sensor-card">
        <div class="sensor-card__name">Pool</div>
        <div class="sensor-card__value">78.5°F</div>
    </div>
</div>
```

### Control Items
```html
<div class="control-item">
    <span class="control-label">Spa Mode</span>
    <div class="toggle toggle--active"></div>
</div>
```

---

## Implementation Phases

### Phase 1: Foundation
1. Add CSS custom properties to `styles.css`
2. Add Google Fonts to `index.html`
3. Replace Bootstrap grid with CSS Grid in index component
4. Remove Bootstrap panel classes

### Phase 2: Component Updates
1. Update each tile component template with new class structure
2. Add tile animations
3. Style form controls (toggles, selects, inputs)

### Phase 3: ApexCharts Theme
1. Update chart configuration in `stats.component.ts`
2. Add CSS overrides for tooltip styling
3. Configure chart colors to match palette

### Phase 4: Polish
1. Add background effects to body
2. Fine-tune responsive breakpoints
3. Test animations on various devices
4. Add focus states for accessibility

---

## Files

```
mockups/
├── proposed-ui.html       ← Interactive mockup with ApexCharts
├── proposed-ui-light.html ← Alternative light theme (not selected)
└── DESIGN-PROPOSAL.md     ← This document
```

Open `proposed-ui.html` in a browser to see the full design with working ApexCharts.
