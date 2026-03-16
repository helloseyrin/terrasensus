# TerraSensus — Farmer Personas

*Written by the repo owner, who is Ukrainian.*

These are the three farmers whose plots are simulated in TerraSensus. They are not invented to be convenient. Each one was chosen because they represent a genuine agricultural context, a distinct set of soil challenges, and a failure mode that the system must handle correctly. Using real regions as a simulation backdrop carries a responsibility to be honest about what we know and what we do not.

---

## Why these three and not others

Each persona was selected to exercise a different dimension of the system that the other two cannot cover:

| Dimension | Mykola (Ukraine) | Fatima (Uzbekistan) | Elena (Oregon) |
|---|---|---|---|
| Climate | Continental | Arid | Maritime |
| Farming approach | Conventional, high-input | Conventional under ecological stress | Regenerative |
| Alert scenario | Slow drift into warning over a season | Already in warning from day one | Almost never alerts — suppresses false alarms |
| Key threshold story | N ceiling lower than global (fruiting crop) | EC tolerance higher than global (salt-adapted crop) | N floor lower than global (intentional deficiency) |
| Soil type | Chernozem (high fertility) | Serozem (thin, alkaline, degraded) | Jory silty clay loam (volcanic) |
| Primary risk | Drought + EC accumulation | Salt toxicity + over-irrigation | False nitrogen alarms misleading a regenerative farmer |

A fourth persona in a tropical climate (cassava, rice) would add further coverage. That is a future addition. These three cover the most important threshold-logic edge cases for the current implementation.

---

## Mykola Petrenko
**Plot**: `plot-ukr-001` — 50 ha, Kherson Oblast, Ukraine
**Crop**: Watermelon (*Citrullus lanatus*, Kherson variety)
**Farming style**: Conventional
**Coordinates**: 46.6354°N, 32.6169°E

### Who he is

Mykola grows watermelons on chernozem soil in Kherson Oblast. The Kherson watermelon holds Geographical Indication (GI) status — the same legal protection as Champagne or Parmigiano-Reggiano. This is not a marketing designation. It reflects something real: the combination of black earth richness, southern sunshine, sandy alluvial soil near the lower Dnipro, and the stress of a hot dry continental summer produces fruit with a sweetness and flavour that people who grew up eating it describe as irreplaceable. Ukrainian watermelons, tomatoes, and produce more broadly carry a quality that is specific to that soil and that sun. It is not reproducible elsewhere, and people who have left Ukraine and spent years in other countries know this.

Mykola farms conventionally — synthetic fertilisers, irrigation, standard inputs. He is not opposed to change but his margins are tight and he is not looking to experiment. He needs reliable information, not agronomic theory.

### Pain points

- **EC drift**: synthetic fertiliser applications raise EC slowly over the season. By August it can be approaching warning range without him noticing. He has no current way to see this trend — he checks things visually.
- **N management for fruit quality**: watermelon is a fruiting crop. Too much nitrogen drives vine growth at the expense of fruit sugar. Getting this balance right is something experienced growers develop over years. He does not have a systematic way to track it.
- **Drought timing**: the continental dry season peaks in July–August, which coincides with critical fruit-set. Missing the irrigation window during fruit-set directly affects yield and sugar content. He currently estimates this from weather and experience.
- **Fertiliser cost and uncertainty**: input costs have been volatile. He needs to know whether what he is spending is working — whether the N he applied is showing up in the soil or has already depleted.
- **Market access and logistics**: post-2022, supply chains and market access in this region have been disrupted in ways that are outside the scope of this app but are part of the context in which he is farming.

### What TerraSensus does for him

- EC trend alerts before salt accumulation reaches warning range — time to act before yield is affected
- Nitrogen ceiling alerts specific to watermelon (critical_high=120 mg/kg, below global default of 180) — catches over-fertilisation that global thresholds would miss
- Drought risk scoring from moisture trend + rainfall data — irrigation timing support during fruit-set
- Fertiliser ROI tracking — connects his applications (logged as activity_log entries) to soil readings at the time

### The Kherson context

*This section exists because using a real region as a simulation backdrop requires honesty about what that region is.*

Kherson city was occupied by Russian forces in February 2022 and de-occupied by Ukrainian forces in November 2022. Parts of Kherson Oblast — primarily the left bank of the Dnipro — remain under Russian occupation. Drone strikes, shelling, and active combat continue across the region. Farming on the Ukrainian-controlled right bank continues under these conditions.

In June 2023, the Kakhovka hydroelectric dam was deliberately destroyed. The dam held back the Kakhovka Reservoir — one of the largest reservoirs in Europe. Its destruction released approximately 18 cubic kilometres of water into the lower Dnipro valley within hours. The flooding reached 80 settlements. Approximately 600,000 hectares of farmland across both banks were inundated. Drinking water infrastructure for hundreds of thousands of people was destroyed.

The water did not carry just water. It carried the contents of everything it submerged and swept away: homes, with everything inside them — furniture, clothing, food stores, household chemicals, heating fuel. Hospitals and clinics — medications, medical waste, disinfectants. Farms and agricultural storage — pesticides, herbicides, fertilisers, fuel tanks. Factories and workshops — industrial chemicals, lubricants, solvents. And it carried the dead. People who did not make it out in time. Dogs, cats, cattle, pigs — livestock and pets that could not be evacuated. All of it moved downstream through the Dnipro delta and into the Black Sea.

The ecological consequences are still unfolding. The lower Dnipro floodplain — an irreplaceable wetland and one of Europe's most significant migratory bird corridors — was destroyed. The soil in flooded agricultural areas absorbed contamination whose full composition is not yet characterised. The biological load from decomposing bodies, human and animal, introduced disease risk on top of the chemical contamination. Researchers are still studying what was deposited and what it will mean for the land over the coming decades. The regional water table was disrupted. Irrigation infrastructure that farms had depended on for generations was gone overnight.

This was not a flood. It was the destruction of a region — its infrastructure, its ecology, its animals, and some of its people — in a matter of hours. The UN and international environmental law organisations have described it as ecocide. That word is accurate.

**What this means for TerraSensus design:**

- Offline-first is not a convenience here. It is a requirement. Power and internet outages are routine in this region. The rule-based alert engine must fire with no network access. The mobile app must serve cached readings with no connectivity.
- Remote monitoring matters more than field access. Sensor data viewed from shelter, from a different city, or from abroad may be the primary interaction mode for a farmer in this region.
- TerraSensus's seven sensors measure N-P-K-pH-EC-moisture-temperature. They cannot detect explosive residue (RDX, heavy metals), hydrocarbon contamination from military vehicles, or the full chemical composition of what the Kakhovka flood deposited. The app must not imply completeness. The agronomist disclaimer is especially load-bearing here.
- The simulation uses pre-2022 agronomic baselines. The repo owner is Ukrainian but does not have direct contact with farmers currently operating in Kherson Oblast and has not validated these assumptions with people living there. If this app ever moves beyond demonstration in this context, that conversation must happen first.

---

## Fatima Yusupova
**Plot**: `plot-uzb-001` — 30 ha, Ferghana Valley, Uzbekistan
**Crop**: Cotton (*Gossypium hirsutum*, upland cotton)
**Farming style**: Conventional
**Coordinates**: 40.3864°N, 71.7864°E

### Who she is

Fatima grows cotton in the Ferghana Valley, one of Central Asia's most agriculturally productive but ecologically stressed regions. Cotton has been the dominant crop here for generations — and the consequences of cotton monoculture combined with saline flood irrigation are written into the landscape: the Aral Sea, once one of the world's largest lakes, is largely gone. The sea was drained by Soviet-era irrigation projects diverting the Amu Darya and Syr Darya rivers primarily to grow cotton. What remains is a salt flat.

Fatima did not cause this. She farms the land she has, with the water she has access to, growing the crop the regional economy is built around. Her soil is serozem — thin, alkaline, low in organic matter, naturally prone to salt accumulation. The irrigation water available to her is saline. Her EC baseline is already 2.4 dS/m on day one — already in warning range before the first growing season begins.

### Pain points

- **Salt accumulation is her primary crisis, not a future risk.** Her EC is already elevated. Without active management — careful irrigation scheduling, leaching, salt-tolerant amendments — it will continue to rise toward crop-damaging levels.
- **She has little visibility into how fast it is rising.** She checks fields visually and from experience. She does not have trend data.
- **Extreme heat** (40°C+ in summer) combined with the region's very low rainfall means moisture drops fast between irrigation cycles. Missing an irrigation window during boll development has direct yield consequences.
- **Cotton's alkaline tolerance is an asset, but also makes it easy to assume the soil is fine** when it is actually accumulating problems that will compound over years.
- **Knowledge gap on soil chemistry.** Cotton tolerates salinity better than most crops, which is partly why the Aral Sea disaster happened — the crop survived conditions that destroyed the surrounding ecosystem. This tolerance can mask problems until they become severe.

### What TerraSensus does for her

- EC warning from day one — the alert fires on her baseline reading because 2.4 dS/m is already above the cotton warning threshold (high=3.5 dS/m), even though it would be approaching critical under global defaults (critical_high=3.0). Crop-aware thresholds give her the right signal.
- Fast moisture drift alerts — arid climate zone has `moisture_drift_per_hour: -0.9`, meaning the simulator models the rapid evaporation that characterises her region. Moisture critical-low alerts during boll development give her an irrigation timing signal.
- Supplier recommendations that account for elevated EC — the prompt passes EC level explicitly and instructs the model to downrank high-salt synthetic fertilisers.
- Regenerative alternatives engine — cover crops and drip irrigation are among the most effective tools for managing salt accumulation in this context. TerraSensus surfaces these alongside conventional recommendations.

### The ecological context

The Ferghana Valley cotton system is not a neutral agricultural backdrop. It is the downstream consequence of one of the twentieth century's largest environmental disasters. This does not mean Fatima should not farm cotton — it means the app should understand the context it is operating in and not give advice that makes the underlying problem worse. High-EC, high-N synthetic fertiliser recommendations on an already-saline plot in Central Asia are not neutral suggestions. The AI layer is instructed to treat elevated EC as a signal to change approach, not just a number to monitor.

---

## Elena Marchetti
**Plot**: `plot-ore-001` — 8 ha, Willamette Valley, Oregon, USA
**Crop**: Pinot Noir (*Vitis vinifera*)
**Farming style**: Regenerative
**Coordinates**: 45.2168°N, 123.1953°W

### Who she is

Elena runs a small Pinot Noir vineyard on Jory silty clay loam — volcanic soil, iron-rich, excellent drainage, well-suited to the grape. She farms regeneratively: cover crops between vine rows, mycorrhizal inoculants, no synthetic fertilisers. She has made a deliberate decision to manage her soil through biological processes rather than chemical inputs.

Her nitrogen is intentionally low at 38 mg/kg. This is not a deficiency. Grapes kept nitrogen-low produce less vegetative growth and more fruit sugar — the balance that determines wine quality. High nitrogen makes for impressive-looking vines and mediocre wine. Every experienced viticulturalist knows this. A soil health app that does not know it will alarm her every day on a metric she is deliberately managing.

### Pain points

- **False alarms from tools built for grain crops.** If TerraSensus used global nitrogen thresholds, it would tell Elena her nitrogen is approaching warning range every single day. This is exactly the kind of noise that makes farmers stop trusting and stop using a tool.
- **Regenerative approaches are rarely what recommendation engines suggest.** Standard fertiliser recommendations assume synthetic inputs. Elena needs the regenerative alternatives engine to be a first-class output, not an afterthought.
- **Fine wine is unforgiving.** A wrong recommendation acted on during bud break or flowering can affect the entire vintage. The agronomist disclaimer is not bureaucratic cover for Elena — it is a genuine description of the app's limitations that she needs to see and understand.
- **EC sensitivity is higher for grapes than most crops.** Salt damage shows up in grapes before it would in field crops. Her EC ceiling is lower (critical_high=2.0 dS/m vs global 3.0) and she needs the alert to fire earlier.
- **She is farming at scale where every input decision has compounding effects.** 8 ha of Pinot Noir in the Willamette Valley represents significant capital. Mistakes are expensive and, in terms of soil biology, potentially multi-year to reverse.

### What TerraSensus does for her

- Suppresses false nitrogen alarms — the pinot_noir threshold (low=15 mg/kg) correctly identifies her N=38 baseline as healthy. She never sees a nitrogen alert on a well-managed vineyard.
- Regenerative alternatives as primary output — Elena's plot almost never triggers a fertiliser alert, so the regenerative alternatives engine runs frequently on this persona. Cover crop recommendations, mycorrhizal inoculant suggestions, and biochar notes are the primary AI output for her.
- Stricter EC alerts — critical_high=2.0 dS/m for pinot_noir vs global 3.0 means the app catches salt stress earlier for a salt-sensitive crop.
- Potassium management — grapes need K in a specific range; the pinot_noir K thresholds are overridden to reflect this.
- Ecological scoring on every recommendation — Elena chose regenerative farming for a reason. The eco-score and GHG estimates on supplier recommendations are meaningful to her in a way they may not be for Mykola or Fatima.
