# Card Standards

This document defines the standardized sizing and usage for card components across doctor and nurse interfaces.

## Specifications

- Base height: `clamp(160px, 22vh, 220px)`
- Mobile height (≤768px): `clamp(140px, 26vh, 200px)`
- Large screens (≥1200px): `clamp(180px, 20vh, 240px)`
- Width: Full width of parent container; grid/column layout controls card width.
- Layout: Content sections within standardized cards should use `.card-content` with `display: flex; align-items: center; justify-content: space-between;`.

## Implementation

- Shared stylesheet: `frontend/src/css/cards.css` imported globally via `App.vue`.
- Apply standardized sizing by adding the class `app-card` to Quasar cards: `\<q-card class="app-card"\>...\</q-card\>`.
- Convenience: existing `.dashboard-card` automatically uses the standardized sizing (no markup change needed), but using `app-card` is preferred for clarity.

## Pages Updated

- Doctor Dashboard: four summary tiles.
- Nurse Dashboard: four summary tiles.
- Doctor Appointment: schedule, performance, notifications tiles.
- Doctor Patient Management: patient list, statistics, nurses tiles.
- Nurse Medicine Inventory: four stat tiles.
- Doctor/Nurse Analytics: main analytics cards.

## Notes

- Cards used for dialogs or complex, scrollable content should avoid `app-card` unless a fixed height is desired.
- To opt-out on a specific card, simply omit the `app-card` class.
- The height clamps ensure proportional sizing across viewport sizes while maintaining visual consistency.