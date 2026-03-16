# TerraSensus — Business Case & Problem Statement

*Written 2026-03-16. This document captures the founding vision, known unknowns, and strategic opportunities. It is intentionally honest about what we do not yet know and what requires domain expert validation.*

---

## The Problem

### Farmers spend hundreds of dollars per hectare on fertiliser they do not need

Typical fertiliser costs for major crops:

| Crop | Typical input cost (fertiliser only) | Per hectare | Source |
|---|---|---|---|
| Wheat | NPK + micronutrients | $150–350/ha/year | FAO / AHDB estimates |
| Maize/corn | Heavy N requirement | $200–450/ha/year | USDA ERS |
| Rice | N + P intensive | $120–300/ha/year | IRRI |
| Vegetables | High P + K | $300–600/ha/year | varies by type |

**The core issue**: most farmers apply fertiliser by habit, by what worked last season, or by blanket agronomic guidelines — not by what is actually in their soil right now. Soil composition changes with weather, crop rotation, microbial activity, and drainage. A field that needed heavy nitrogen last autumn may have adequate levels this spring.

**Result**: chronic over-fertilisation. Industry estimates suggest 30–50% of applied nitrogen never reaches the crop — it leaches into groundwater, volatilises into the atmosphere as nitrous oxide (a greenhouse gas 265× more potent than CO₂), or accumulates as toxic salt buildup (high EC).

A 200ha farm spending $250/ha on fertiliser = **$50,000/year**. A 25% reduction through precision application = **$12,500 saved annually**. With TerraSensus, this becomes measurable and attributable.

---

## The Opportunity

### This problem is not unique to agriculture

The same sensor-pipeline-recommendation architecture applies to adjacent sectors that are chronically underserved by SaaS:

| Sector | Analogue problem | TerraSensus application |
|---|---|---|
| **Marine conservation** | Water quality degradation, dead zones from agricultural runoff | Coastal/estuary sensors: pH, dissolved oxygen, nitrogen, phosphorus, salinity |
| **Bioremediation** | Contaminated land restoration (heavy metals, hydrocarbons) | Track remediation progress: soil pH, organic matter, EC, toxin proxies |
| **Urban ecology** | Green infrastructure (parks, urban farms, rewilding projects) | Municipal soil health monitoring at scale |
| **Forestry** | Soil carbon sequestration measurement for carbon credit markets | Standardised soil carbon reporting pipeline |
| **Aquaculture** | Pond/tank water quality affecting fish health | Same event-driven alert architecture, different sensor suite |

The insight: **the pipeline is the product**. Sensor → ingestion → alert → recommendation → cost-benefit analysis. The sensors and thresholds change per sector; the architecture does not. TerraSensus v1 is agriculture. The framework is sector-agnostic.

---

## What We Do Not Know (and must find out)

This section is intentionally honest. The framework is built by a software engineer, not an agronomist. Before TerraSensus can make authoritative recommendations, the following require validation by domain experts — preferably people actively working in the sector:

### Agronomic unknowns
- [ ] Are the sensor threshold values in `services/alert-engine/rules.py` agronomically accurate for the target regions?
- [ ] Do nutrient recommendations vary significantly by soil type (clay vs sandy vs peat)?
- [ ] What is the correct sampling depth for continuous sensors vs lab samples?
- [ ] How do crop growth stages affect acceptable nutrient ranges?

### Economic unknowns
- [ ] What are realistic fertiliser costs per hectare in target markets (UK? EU? Global?)
- [ ] What is the typical application rate (kg/ha) per nutrient type per crop?
- [ ] What is the economic value of a single "unnecessary" fertiliser application avoided?
- [ ] What does a soil lab report actually cost a farmer to commission? (€50? €300?)

### Ecological unknowns
- [ ] Which fertiliser compounds are most harmful to soil invertebrates (earthworms, beetles, mycorrhizal fungi)?
- [ ] What is the quantified biodiversity cost of a specific fertiliser product per hectare?
- [ ] What are validated regenerative alternatives to synthetic fertilisers, and what is their cost-effectiveness data?

### Operational unknowns
- [ ] How long do buried IoT sensors last in field conditions?
- [ ] What wireless protocols work reliably in rural areas with poor connectivity? (LoRaWAN? NB-IoT?)
- [ ] What does sensor installation and calibration actually cost per plot?

**These are the questions to bring to domain experts.** The software framework is designed to be modified once expert answers are available. Nothing in the codebase should be treated as agronomically authoritative at this stage.

---

## Cost-Benefit Analysis Feature

### What TerraSensus should calculate for each farm

At the end of a growing season (or on-demand), TerraSensus should produce a **Soil Health ROI Report**:

```
TerraSensus ROI Summary — North Field (12.5 ha) — 2026 Season

Fertiliser applications recorded:    6
Applications flagged as unnecessary: 2  (soil readings within range at time of application)
Estimated overspend:                 £1,840
Estimated savings if advice followed: £1,840 (37% of fertiliser budget)

Soil health trend:                   ↑ improving (pH stabilised, N trend positive)
EC trend:                            ↓ declining (salt buildup reducing — good)

Ecological impact score:             B+ (reduced synthetic N application vs last season)
```

### The calculation model

```
Savings = (Applications flagged as unnecessary) × (avg application cost per hectare × plot area)

Ecological score inputs:
  - Synthetic N applications: negative weight (nitrous oxide, waterway runoff)
  - Organic/slow-release applications: neutral/positive weight
  - EC trend: negative if rising (salt buildup → long-term yield degradation)
  - Soil organic matter trend: positive if rising (carbon sequestration, biodiversity)
  - Biodiversity proxy: earthworm density estimator (derived from organic matter + pH + pesticide history)
```

This is a v2 feature — but it should be designed into the data model now. Every fertiliser application event (type, quantity, plot, date) must be recorded from day one, so the ROI calculation has historical data to work with.

---

## Regenerative Alternatives — Knowledge Base

One of the most valuable things TerraSensus can do is surface **non-chemical alternatives** when the AI recommendation engine detects deficiencies. These should be offered alongside conventional fertiliser suggestions, with comparative cost and ecological impact data.

### Known alternatives to document and build into the recommendation engine

| Problem | Chemical default | Regenerative alternative | Evidence |
|---|---|---|---|
| Low nitrogen | Synthetic urea / ammonium nitrate | Cover crops (clover, vetch) fix atmospheric N; compost; biochar | Well-established |
| Low phosphorus | Triple superphosphate | Mycorrhizal fungi inoculants; bone meal; rock phosphate | Established |
| Pest pressure + nutrient cycling | Pesticides + NPK | **Integrated pest management**: rice paddies with fish + crabs (Japan/SE Asia) consume pests, fertilise with waste, no synthetic input | Documented, significant |
| Soil structure / water retention | Irrigation + synthetic | Cover cropping; reduced tillage; compost mulch | Well-established |
| Heavy metal contamination | Excavation / cap-and-cover | **Phytoremediation**: sunflowers (Pb, Cd), hemp (heavy metals), Indian mustard (As) | Documented |
| Low soil carbon | N/A (ignored in conventional) | Biochar application; compost; perennial ground cover | Active research area |

The rice-fish-crab system is a particularly compelling example for the app: zero synthetic fertiliser, simultaneous protein production, closed-loop nutrient cycling. It is a UNESCO-recognised agricultural heritage system in Japan. This is the kind of alternative that belongs in TerraSensus recommendations — not just "buy product X from supplier Y."

---

## Strategic Framing

TerraSensus is not a SaaS play on top of the existing broken system. It is a **measurement and accountability layer** for farming practices that are currently invisible.

The thesis:
1. You cannot improve what you cannot measure
2. Farmers are rational economic actors — if the data shows they are wasting money, most will change behaviour
3. The ecological cost of that wasted fertiliser is currently externalised (paid by rivers, insects, future generations) — TerraSensus makes it visible and attributable
4. Over time, the dataset becomes intrinsically valuable: regional soil health trends, fertiliser waste attribution, biodiversity correlation data

The climate crisis makes this software necessary, not optional. Agricultural runoff is a leading cause of freshwater dead zones. Nitrous oxide from over-fertilisation represents 6% of global greenhouse gas emissions. This is solvable with better data.

---

## What TerraSensus Is Not (Scope Guard)

- It is not an agronomic authority — it surfaces data and suggestions; a qualified agronomist makes the final call
- It is not a sensor hardware company — phase 1 uses simulation; phase 2 integrates existing sensor hardware (PySensorMQTT)
- It is not a fertiliser marketplace — supplier recommendations are informational, not commercial partnerships (initially)
- It is not a substitute for domain expertise — the codebase is a framework awaiting expert calibration
