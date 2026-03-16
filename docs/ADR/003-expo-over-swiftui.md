# ADR 003 — React Native (Expo) over SwiftUI

**Date:** 2026-03-16
**Status:** Accepted

## Context
TerraSensus needs a mobile app for farmers in the field. Primary test device is iPhone (iOS).

## Decision
Use React Native with Expo rather than native SwiftUI.

## Rationale
- Significant code sharing with the Next.js web dashboard (hooks, API clients, TypeScript types)
- Expo Go enables instant iPhone testing without Xcode build cycles during early development
- Expo's new architecture (JSI/Fabric renderer) delivers native-speed performance for data-display UIs
- JS/React familiarity reduces context switching across the full stack
- Android support for free if needed in future

## Consequences
- Cannot match 100% native SwiftUI performance — acceptable for a data-display app
- Camera module for lab report scanning may need a native Swift module if Expo's camera library proves insufficient
- EAS Build handles TestFlight distribution when ready for broader testing
