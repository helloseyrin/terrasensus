# A Note on the Kherson Persona

*Developer note — written by the repo owner, who is Ukrainian.*

TerraSensus includes a simulation persona set in Kherson Oblast, Ukraine — Mykola Petrenko, a watermelon farmer on chernozem soil. This file exists because using a real region as a simulation backdrop carries a responsibility to be honest about what we know and what we do not. It belongs here, in the engineering notes, not abstracted into a personas doc. It is part of how this software was made and why it was made the way it was.

See also: `docs/personas.md` for Mykola's full persona including pain points and what TerraSensus does for him.

---

## What we know — the land and the crop

Kherson Oblast is one of the most agriculturally significant regions in Europe. Its chernozem soil — formed over millennia of grassland decomposition — is among the most naturally fertile on earth. The region is known for grain and sunflowers in its northern parts, but what it is most celebrated for is its watermelons.

The Kherson watermelon holds Geographical Indication (GI) status — the same legal protection as Champagne or Parmigiano-Reggiano. The combination of chernozem richness, southern sunshine, sandy soil texture in the lower Dnipro region, and the stress of a hot dry continental summer produces fruit with a sweetness and flavour that farmers and Ukrainians who grew up eating it describe as irreplaceable. This is not marketing. It is the accumulated agricultural identity of a region and a people.

During the Russian occupation, farmers in the region who had always grown watermelons were unable to do so. In that absence, the watermelon became a symbol — of Kherson, of occupation, of what had been taken. At the Ukrainian stand at COP27, a watermelon was displayed alongside a Ukrainian flag. When President Zelenskyy arrived in newly liberated Kherson in November 2022, he joked that he had come because he "wanted a watermelon." Ukrposhta, the Ukrainian national postal service, released watermelon-themed stamps commemorating the liberation. A fruit became a flag.

This is why Mykola grows watermelons and not something else. The choice is not incidental.

---

## What we know — the conflict and the ecocide

<details>
<summary>⚠ Developer note — Kakhovka dam destruction, occupation, and what the flood carried (click to expand)</summary>

*Written by the repo owner, who is Ukrainian, because this context belongs in the repository and should not be sanitised out of it.*

Kherson city was occupied by Russian forces in February 2022 and de-occupied by Ukrainian forces in November 2022. Parts of Kherson Oblast — primarily the left bank of the Dnipro — remain under Russian occupation as of the time of writing. Drone strikes, shelling, and active combat continue across the region. Farming on the Ukrainian-controlled right bank continues under these conditions.

In June 2023, the Kakhovka hydroelectric dam was deliberately destroyed. The dam held back the Kakhovka Reservoir — one of the largest reservoirs in Europe. Its destruction released approximately 18 cubic kilometres of water into the lower Dnipro valley within hours. The flooding reached 80 settlements. Approximately 600,000 hectares of farmland across both banks were inundated. Drinking water infrastructure for hundreds of thousands of people was destroyed.

The water did not carry just water. It carried the contents of everything it submerged and swept away: homes, with everything inside them — furniture, clothing, food stores, household chemicals, heating fuel. Hospitals and clinics — medications, medical waste, disinfectants. Farms and agricultural storage — pesticides, herbicides, fertilisers, fuel tanks. Factories and workshops — industrial chemicals, lubricants, solvents. And it carried the dead. People who did not make it out in time. Dogs, cats, cattle, pigs — livestock and pets that could not be evacuated. All of it moved downstream through the Dnipro delta and into the Black Sea.

The ecological consequences are still unfolding. The lower Dnipro floodplain — an irreplaceable wetland and one of Europe's most significant migratory bird corridors — was destroyed. The soil in flooded agricultural areas absorbed contamination whose full composition is not yet characterised. The biological load from decomposing bodies, human and animal, introduced disease risk on top of the chemical contamination. Researchers are still studying what was deposited and what it will mean for the land over the coming decades. The regional water table was disrupted. Irrigation infrastructure that farms had depended on for generations was gone overnight.

This was not a flood. It was the destruction of a region — its infrastructure, its ecology, its animals, and some of its people — in a matter of hours. The UN and international environmental law organisations have described it as ecocide. That word is accurate.

</details>

---

## What we do not know

This is the part that matters most for how this software is built.

TerraSensus monitors seven sensors: moisture, temperature, pH, nitrogen, phosphorus, potassium, and electrical conductivity. These sensors are designed for standard agricultural conditions. They are not designed to capture:

- **Explosive residue in soil.** Munitions leave RDX, TNT breakdown products, and heavy metals (lead, copper, tungsten) in the soil. These are toxic to soil microbiology and to crops. None of them appear in a standard N-P-K-pH reading.
- **Fuel and lubricant contamination.** Military vehicle movement leaves hydrocarbons in the soil that disrupt microbial communities and reduce permeability. Our EC sensor may pick up some of this indirectly, but it is not measuring what it would need to measure.
- **Flood contamination from the dam destruction.** What the Kakhovka flooding deposited in soil — across hundreds of thousands of hectares — is not fully characterised. We do not know.
- **Impact on soil biodiversity.** Soil is not just chemistry. It is billions of microorganisms, fungi, nematodes, and invertebrates that drive nutrient cycling, water retention, and structure. Explosions, fire, compaction from armoured vehicles, and flooding all damage this ecosystem in ways that N-P-K readings cannot detect. Recovery timelines for soil biology after conflict are measured in years to decades, not months.
- **What farming in this region actually looks like right now.** The simulation uses pre-2022 agronomic baselines. A farmer operating in Kherson Oblast today is navigating realities — physical danger, infrastructure damage, market disruption, psychological load — that no soil model can accurately represent from the outside. The repo owner does not have direct contact with farmers in this region and has not validated any of these assumptions with people who live there.

---

## What this means for the application

- The agronomist disclaimer on every AI recommendation is not boilerplate here. It is the honest truth: the model cannot reason about the soil chemistry of a post-conflict flood plain.
- The seven sensor readings will not tell a farmer whether their soil contains munitions residue. The app must not imply otherwise.
- Offline resilience — the rule-based alert engine, the mobile cache, the local fallback — is a safety requirement in this context, not a convenience. Infrastructure in active conflict zones is unreliable by definition.
- If TerraSensus is ever to be useful in this context rather than just representative of it, Ukrainian agronomists, farmers currently operating in the region, and environmental scientists studying post-conflict soil recovery must be involved in shaping it. The repo owner is none of these things.

---

## Why this file exists

Because Mykola is not a fictional character to us. He represents real farmers on real land in a region that has been deliberately targeted for environmental and agricultural destruction. Using that as a simulation persona without acknowledging what we don't know about it felt wrong.

TerraSensus is a demonstration framework. Before it becomes anything more in a context like Kherson Oblast, it needs people with direct knowledge of that context to shape it. This file is a placeholder for that future conversation — and an honest acknowledgment that it has not happened yet.
