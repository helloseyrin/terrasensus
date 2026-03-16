# A Note on the Kherson Persona

*Written by the repo owner, who is Ukrainian.*

---

TerraSensus includes a simulation persona set in Kherson Oblast, Ukraine — Mykola Petrenko, a farmer on chernozem soil. This note exists because using a real region as a simulation backdrop carries a responsibility to be honest about what we know and what we do not.

---

## What we know

Kherson Oblast is one of the most agriculturally significant regions in Europe. Its chernozem soil — formed over millennia of grassland decomposition — is among the most naturally fertile on earth. The region is known for grain and sunflowers in its northern parts, but what it is most celebrated for is its watermelons.

The Kherson watermelon has been granted Geographical Indication (GI) status — the same protection given to Champagne or Parmigiano-Reggiano. The combination of chernozem richness, southern sunshine, sandy soil texture in the lower Dnipro region, and the particular stress of a hot dry continental summer produces fruit with a sweetness and flavour that farmers and Ukrainians who grew up eating them describe as genuinely irreplaceable. This is not marketing. It is the accumulated agricultural identity of a region.

Kherson city was occupied by Russian forces in February 2022 and de-occupied by Ukrainian forces in November 2022. Parts of Kherson Oblast — primarily the left bank of the Dnipro — remain under Russian occupation as of the time of writing.

In June 2023, the Kakhovka hydroelectric dam was deliberately destroyed. The dam held back the Kakhovka Reservoir — one of the largest reservoirs in Europe. Its destruction released approximately 18 cubic kilometres of water into the lower Dnipro valley within hours. The flooding reached 80 settlements. Approximately 600,000 hectares of farmland across both banks were inundated. Drinking water infrastructure for hundreds of thousands of people was destroyed.

The water did not carry just water. It carried the contents of everything it submerged and swept away: homes, with everything inside them — furniture, clothing, food stores, household chemicals, heating fuel. Hospitals and clinics — medications, medical waste, disinfectants. Farms and agricultural storage — pesticides, herbicides, fertilisers, fuel tanks. Factories and workshops — industrial chemicals, lubricants, solvents. And it carried the dead. People who did not make it out in time. Dogs, cats, cattle, pigs — livestock and pets that could not be evacuated. All of it moved downstream through the Dnipro delta and into the Black Sea.

The ecological consequences are still unfolding. The lower Dnipro floodplain — an irreplaceable wetland and one of Europe's most significant migratory bird corridors — was destroyed. The soil in flooded agricultural areas absorbed contamination whose full composition is not yet characterised. The biological load alone — from decomposing bodies, human and animal — introduced disease risk on top of the chemical contamination. Researchers are still studying what was deposited and what it will mean for the land over the coming years and decades. The regional water table was disrupted. Irrigation infrastructure that farms had depended on for generations was gone overnight.

This was not a flood. It was the destruction of a region — its infrastructure, its ecology, its animals, and some of its people — in a matter of hours. International environmental law organisations and the UN have described it as ecocide. That word is accurate.

Drone strikes, shelling, and active combat continue across the region. Farming on the Ukrainian-controlled right bank continues under these conditions.

---

## What we do not know

This is the part that matters more.

TerraSensus monitors seven sensors: moisture, temperature, pH, nitrogen, phosphorus, potassium, and electrical conductivity. These sensors are designed for standard agricultural conditions. They are not designed to capture:

- **Explosive residue in soil.** Munitions leave RDX, TNT breakdown products, and heavy metals (lead, copper, tungsten) in the soil. These are toxic to soil microbiology and to crops. None of them appear in a standard N-P-K-pH reading.
- **Fuel and lubricant contamination.** Military vehicle movement leaves hydrocarbons in the soil that disrupt microbial communities and reduce permeability. Our EC sensor may pick up some of this indirectly, but it is not measuring what it would need to measure.
- **Flood contamination from the dam destruction.** What the Kakhovka flooding deposited in soil — across hundreds of thousands of hectares — is not fully characterised. Researchers are still studying it. We do not know.
- **Impact on soil biodiversity.** Soil is not just chemistry. It is billions of microorganisms, fungi, nematodes, and invertebrates that drive nutrient cycling, water retention, and structure. Explosions, fire, compaction from armoured vehicles, and flooding all damage this ecosystem in ways that N-P-K readings cannot detect. Recovery timelines for soil biology after conflict are measured in years to decades, not months.
- **What farming in this region actually looks like right now.** The simulation uses pre-2022 agronomic baselines. A farmer operating in Kherson Oblast today is navigating realities — physical danger, infrastructure damage, market disruption, psychological load — that no soil model can accurately represent from the outside. The repo owner does not have direct contact with farmers in this region and has not validated any of these assumptions with people who live there.

---

## What this means for the application

TerraSensus is explicitly a decision support tool, not a decision maker. This distinction matters everywhere. It matters especially here.

If this app were ever deployed in conflict-affected regions:

- The agronomist disclaimer on every AI recommendation is not boilerplate. It is the honest truth that the model was not trained on, and cannot reason about, the specific soil chemistry of a post-conflict flood plain.
- The seven sensor readings would tell a farmer about standard soil health parameters. They would not tell a farmer whether their soil has munitions contamination. The app must not imply otherwise.
- Offline resilience — the rule-based alert engine, the mobile cache, the local fallback — becomes a safety requirement, not a convenience. Infrastructure in active conflict zones is unreliable by definition.
- If TerraSensus is ever to be useful in this context rather than just representative of it, the people who would use it must be involved in defining what it should measure and say. That means Ukrainian agronomists, farmers currently operating in the region, and environmental scientists studying post-conflict soil recovery. The repo owner is none of these things.

---

## Why this is in the repo

Because Mykola is not a fictional character to us. He represents real farmers on real land in a region that has been deliberately targeted for environmental and agricultural destruction. Using that as a simulation persona without acknowledging what we don't know about it felt wrong.

TerraSensus is a demonstration framework. Before it becomes anything more in a context like Kherson Oblast, it needs people with direct knowledge of that context to shape it. This note is a placeholder for that future conversation — and an honest acknowledgment that it hasn't happened yet.
