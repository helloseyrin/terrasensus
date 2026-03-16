# Engineering Notes — Cost-Benefit Analysis

---

## The core insight: make the invisible visible

Farmers currently have no feedback loop between fertiliser spend and soil response. They apply, crops grow (or don't), and they repeat the same practice next season. TerraSensus closes this loop by:

1. Recording what was applied, when, at what cost
2. Cross-referencing with soil sensor readings at the time of application
3. Flagging applications where soil readings were already within acceptable range
4. Calculating the attributable cost of that over-application

This is not a judgement — it is a measurement. A farmer who sees "you spent £1,840 on applications that your own soil data suggests were unnecessary" has information they simply did not have before.

---

## Data model requirement: log applications from day one

The ROI calculation only works if application events are recorded historically. You cannot retrospectively determine whether a specific application was necessary without knowing what the soil readings were at that moment.

**This is a design constraint that must be enforced from v1**: the `fertiliser_applications` table must be populated even before the ROI feature is built. Every application a farmer logs becomes a data point that makes future ROI reports more accurate.

Schema: see `shared/types/cost_benefit.ts` — `FertiliserApplication` type.

---

## What "unnecessary application" means

An application is flagged as unnecessary if, at the time of application:
- The relevant nutrient reading was within the "healthy range" (above `low` threshold) for that sensor
- OR the EC was already above 2.0 dS/m (adding more synthetic fertiliser worsens salt buildup)

This is a conservative definition — the farmer's agronomist may disagree based on crop growth stage, upcoming weather forecast, or local knowledge. The flag is informational, not prescriptive. This is by design (see "domain expert review mode" in backlog).

---

## Ecological cost-benefit

Conventional cost-benefit only counts money. TerraSensus should also surface the ecological cost of each application — currently externalised and invisible to the farmer.

Key ecological costs to model:

| Impact | Proxy metric | How to estimate |
|---|---|---|
| Nitrous oxide (GHG) | Synthetic N application rate | IPCC emission factor: 1% of applied N volatilises as N₂O |
| Waterway runoff risk | Application rate × rainfall_7d | High rainfall after heavy application = high runoff risk |
| Soil invertebrate harm | Pesticide + synthetic N history | Earthworm population proxy: declining with EC, recovering with organic matter |
| Salt buildup | EC trend | Rising EC = long-term yield degradation, costly to reverse |

This is not a scientific model — it is an indication. It should be labelled clearly as an estimate and validated by domain experts before being presented as authoritative.

---

## Regenerative alternatives — why they belong in the app

The rice-fish-crab system used in Japan and SE Asia is a documented example of a zero-external-input farming system that outperforms conventional practice on multiple metrics simultaneously:
- Fish and crabs consume pests (replacing pesticides)
- Their waste fertilises the rice (replacing synthetic N)
- Farmers produce two additional protein crops from the same land
- Biodiversity in the paddy ecosystem is orders of magnitude higher than conventional monoculture

This is not an ideological position — it is an economic and ecological data point. TerraSensus should be able to say: "your current approach costs £X/ha and has this ecological profile. Here is an alternative approach that costs £Y/ha and has this ecological profile." The farmer decides.

The regenerative alternatives prompt (`prompts/regenerative_alternatives.txt`) is designed to surface these options alongside conventional recommendations — never instead of them.

---

## Sector expansion note

The cost-benefit framework is sector-agnostic. In marine conservation:
- "Application" becomes "intervention" (dredging, reef restoration, pollution remediation)
- "Soil readings" become "water quality readings"
- "Fertiliser savings" become "intervention cost vs ecosystem service value restored"

The same data model, same pipeline, different domain vocabulary. This is worth preserving as an architectural principle.
