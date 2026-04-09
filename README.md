# Marp Presentations — Agent Zero Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-featured [Marp](https://marp.app/) presentation plugin for [Agent Zero](https://github.com/frdel/agent-zero). Create, view, edit, and export slide presentations directly inside Agent Zero — no external tools required.

![Marp Presentations Plugin](https://marp.app/og-image.png)

---

## Features

| Feature | Description |
|---|---|
| **AI Generation** | Ask the agent to create a presentation — it writes Marp markdown and saves it automatically |
| **Floating Panel Viewer** | Non-modal, draggable, resizable panel — stays on screen while you work |
| **Page-by-page navigation** | Single slide display with ◀ ▶ buttons and arrow keys |
| **Live Split-pane Editor** | Real-time preview as you type |
| **Syntax Highlighting** | CodeMirror 6 with One Dark theme for Markdown editing |
| **Color Picker Toolbar** | Insert background and text color directives at cursor |
| **Click-to-Sync Cursor** | Click any slide in the preview → editor jumps to that slide's code |
| **Export** | Export to HTML, PDF, or PPTX via `marp-cli` |
| **Server-side Rendering** | Slides rendered via Node.js + `@marp-team/marp-core` locally — no CDN dependency |

---

## Requirements

- **Agent Zero** (latest)
- **Node.js** v16+ (pre-installed in the Agent Zero Docker image)
- **npm** (for the local `@marp-team/marp-core` install)
- PDF/PPTX export additionally requires **Chromium** (auto-downloaded by `marp-cli` on first export)

---

## Installation

1. **Clone or copy** this plugin into your Agent Zero plugins directory:

   ```bash
   cd /a0/usr/plugins
   git clone https://github.com/PaoloC68/marp-presentations.git marp-presentations
   ```

2. **Install Node.js dependencies:**

   ```bash
   cd /a0/usr/plugins/marp-presentations
   npm install
   ```

3. **Restart Agent Zero** — the plugin is auto-discovered on startup.

The sidebar dropdown will show a **Presentations** button after restart.

---

## Usage

### Via the Agent

Just ask naturally:

> *"Create a presentation about machine learning with 5 slides and open it"*

The agent uses `marp_tool` to write the Marp markdown, save it, and render it in the viewer panel.

### Via the Sidebar Button

1. Click the **☰ quick-actions dropdown** in the Agent Zero sidebar
2. Click **Presentations**
3. Select a `.md` file from the list
4. Slides render immediately in the floating panel

### Panel Controls

| Control | Action |
|---|---|
| Drag title bar | Move the panel |
| Drag bottom-right corner | Resize the panel |
| ◀ / ▶ buttons | Navigate slides |
| Arrow keys (← →) | Navigate slides (keyboard) |
| ✏️ Edit button | Open live split-pane editor |
| ⬇ Export ▾ | Export to HTML / PDF / PPTX |
| ✕ Close | Hide the panel |

### Editor Features

- **Syntax highlighting** via CodeMirror 6 (One Dark theme)
- **BG color picker** → inserts `<!-- _backgroundColor: #hex -->` at cursor
- **Text color picker** → inserts `<!-- _color: #hex -->` at cursor
- **Click any slide** in the preview pane → editor cursor jumps to that slide's markdown
- **Save** — saves the file, updates the viewer panel
- **Save & Close** — saves, re-renders in the panel, closes editor

---

## Presentation Storage

All presentations are saved as Marp-flavored Markdown files:

```
/a0/usr/workdir/presentations/*.md
```

Exported files (HTML/PDF/PPTX) are saved to the same directory.

---

## Marp Markdown Quick Reference

```markdown
---
marp: true
theme: default
---

# First Slide

This is the first slide content.

---

# Second Slide

<!-- _backgroundColor: #1e1e2e -->
<!-- _color: #cdd6f4 -->

This slide has a custom background and text color.

---

## With a Table

| Column A | Column B |
|---|---|
| Value 1 | Value 2 |
```

See the [Marp documentation](https://marpit.marp.app/) for full syntax reference.

---

## Architecture

```
marp-presentations/
├── plugin.yaml                          # Plugin manifest
├── hooks.py                             # Install hook (marp-cli)
├── package.json                         # Node.js dependencies
├── helpers/
│   └── render.js                        # Server-side Marp renderer
├── tools/
│   └── marp_tool.py                     # Agent tool (save/load/list/open/export)
├── api/
│   ├── marp_render.py                   # POST: render markdown → HTML/CSS
│   ├── marp_save.py                     # POST: save .md file
│   ├── marp_load.py                     # POST: load .md file
│   ├── marp_list.py                     # POST: list presentations
│   └── marp_export.py                   # POST: export to HTML/PDF/PPTX
├── extensions/
│   └── webui/
│       ├── page-head/
│       │   └── marp-panel.html          # Floating viewer panel
│       └── sidebar-quick-actions-main-start/
│           └── marp-button.html         # Sidebar trigger button
└── webui/
    ├── marp-store.js                    # Alpine.js store (global state)
    └── marp-editor.html                 # Split-pane editor modal
```

### Rendering Pipeline

```
Agent writes .md → marp_tool.py saves file
                ↓
Frontend calls /api/plugins/marp-presentations/marp_render
                ↓
marp_render.py → subprocess → node helpers/render.js
                ↓
@marp-team/marp-core → { html, css, slideCount }
                ↓
Iframe (document.write) renders slides in browser
CSS class toggle for page-by-page navigation
```

---

## Export Notes

| Format | Speed | Requirements |
|---|---|---|
| **HTML** | Fast | None |
| **PDF** | Slow on first run | Chromium (auto-downloaded ~200MB) |
| **PPTX** | Slow on first run | Chromium (auto-downloaded ~200MB) |

PDF and PPTX use `npx @marp-team/marp-cli` which bundles its own Chromium. The first export triggers a one-time download; subsequent exports are fast.

---

## License

[MIT](LICENSE) © 2026 Paolo Cesare Calvi
