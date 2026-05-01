# AGENTS.md

## Project Overview

AtHand is now a Tauri desktop app: a lightweight global hotkey AI assistant with a floating Spotlight-style UI, system tray, local JSON config, Markdown + KaTeX rendering, and OpenAI-compatible HTTP calls.

## Where To Look

- `src/main.js` - frontend behavior, settings overlay, keyboard shortcuts, Tauri command calls.
- `index.html` - single-page UI markup and styles.
- `src-tauri/src/main.rs` - Tauri app setup, tray menu, window behavior, command registration.
- `src-tauri/src/config.rs` - `~/.athand/config.json` load/save.
- `src-tauri/src/hotkey.rs` - global double-Shift listener via `rdev`.
- `src-tauri/src/llm.rs` - OpenAI-compatible chat completions requests.
- `src-tauri/tauri.conf.json` - Tauri window, allowlist, bundle, tray, and icon configuration.

## Commands

- `npm install` - install frontend and Tauri CLI dependencies.
- `npm run build` - build the Vite frontend.
- `npm run tauri build` - build the desktop app bundle.
- `npm run tauri dev` - run the app in development mode.
- `cargo check --manifest-path src-tauri/Cargo.toml` - check Rust backend only.

## Conventions

- Keep Tauri v1 APIs unless intentionally migrating the whole project.
- Keep the UI dependency-light; this project intentionally uses vanilla JS rather than a frontend framework.
- Do not commit generated `node_modules/`, `dist/`, or `src-tauri/target/` output.
- Preserve the OpenAI-compatible API shape so custom endpoints continue working.
- Double-Shift is implemented below Tauri's normal shortcut layer; treat macOS Accessibility/Input Monitoring permission issues as runtime/platform concerns, not normal shortcut registration failures.
