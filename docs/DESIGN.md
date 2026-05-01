# Design Intent

## Design Intent and Product Personality

Platvision ID should feel like a focused inspection console for reading Indonesian license plates. The interface should help a student or evaluator understand the pipeline without making the screen feel like a generic dashboard.

## Audience and Use-Context Signals

The main users are students, lecturers, and demo evaluators. They need fast upload, visible result confidence, and clear notes when the demo uses fallback behavior.

## Visual Direction and Distinctive Moves

The conceptual anchor is a vehicle inspection lightbox: a matte workbench, a bright scan lane, and measured result readouts. The distinctive move is a horizontal scan reveal over the upload preview and result panel after recognition.

## Color, Typography, Spacing, and Density Decisions

Use a neutral workbench base, amber inspection accents, green success, red error, and blue information only where meaning requires it. Use strong monospace typography for plate text and compact sans-serif text for labels and body copy.

## Token Architecture and Alias Strategy

Tokens should be layered as primitive, semantic, and component roles. Components must use semantic aliases instead of raw color values.

## Responsive Recomposition Plan

Desktop shows upload and result side by side. Tablet stacks the result under the upload with diagnostics in a compact row. Mobile prioritizes upload first, then plate result, then diagnostics.

## Motion, Interaction, and Feedback Rules

Motion is light and functional. Upload hover should show an inspection-lane highlight. Recognition should use a short scan-line transition. Reduced-motion users should get direct state changes with no sweeping animation.

## Component Language, States, and Morphology

Controls should be rectangular with small radii, clear borders, and strong focus states. Required states are default, hover, focus-visible, active, disabled, loading, empty, error, success, and transition.

## Source Boundaries and Context Hygiene

This design is derived from the ALPR workflow and current repo requirements. It does not copy external UI references or reuse old visual memory.

## Accessibility Non-Negotiables

All controls must be keyboard reachable. Focus must be visible. Text contrast must meet WCAG 2.2 AA. Status messages must be readable without relying on color alone.

## Anti-Patterns to Avoid

Avoid decorative gradients, oversized marketing heroes, generic card grids, and hiding demo limitations. Do not make the UI imply accurate plate detection when only the fallback model was used.

## Implementation Notes for Future UI Tasks

Keep the UI dependency-free until a stronger frontend requirement appears. Native HTML, CSS, and a small amount of JavaScript are enough for version 1.
