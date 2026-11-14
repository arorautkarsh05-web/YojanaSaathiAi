# YojanaSaathi AI — Product Vision, Innovation & Feasibility Overview
**Document Version:** 3.0.0  
**Authors:** Team Aalekh (Adima Agarwal - Team Leader, Utkarsh Arora)  
**Product Category:** Evidence-Grounded Farmer Benefit Intelligence and Multi-Scheme Convergence Platform  
**Target Region:** Uttar Pradesh, India (All 75 Administrative Districts)

---

## 1. The Core Agricultural Problem in India

While Central and State Governments allocate over ₹3,00,000 Crores annually towards agricultural welfare schemes (PM-KISAN, PMFBY, PMKSY, KCC, Agricultural Mechanization, Accident Insurance), small and marginal farmers face acute friction:

1. **Information Asymmetry & Disjointed Portals:** A farmer growing wheat in Jhansi must navigate up to 5 disparate portals (pmkisan.gov.in, pmfby.gov.in, uphorticulture.gov.in, agriculture.up.gov.in, and commercial bank branches) with conflicting eligibility rules and uncoordinated deadlines.
2. **Double-Dipping Fears vs. Lost Convergence:** Farmers either inadvertently apply for overlapping, disqualified subsidies or fail to leverage synergistic combinations (e.g. using PM-KISAN cash grants to fund the farmer's share of micro-irrigation systems under PMKSY-PDMC).
3. **Flawed AI Advice:** Generalist LLM chatbots hallucinate eligibility conditions, invent fake government circulars, or quote defunct rules.
4. **Unit Ambiguities:** In Uttar Pradesh, land is colloquially measured in "Bigha", which varies drastically: a Pucca Bigha in Western UP is ~0.625 acres (27,225 sq. ft.), whereas a Kachha Bigha in Eastern UP is ~0.208 to 0.33 acres. Converting Bigha with a single universal factor leads to statutory disqualification.

---

## 2. Key Product Innovations in YojanaSaathi AI

### 2.1 Deterministic Decoupled Rules Engine
YojanaSaathi uses a strictly deterministic 3-valued (`PASS`, `FAIL`, `UNKNOWN`) policy engine. The AI layer (NLP/intake) only extracts information and explains results; it **never** determines entitlement. Missing information strictly evaluates to `UNKNOWN`, preventing false guarantees of benefits.

### 2.2 Evidence-Backed Pairwise Convergence Engine
YojanaSaathi computes pairwise scheme compatibility across all $\binom{N}{2}$ combinations. It explicitly rejects false transitivity ($A \sim B \land B \sim C \not\implies A \sim C$). Every compatibility status is tied directly to published joint government orders, circulars, or operational guidelines.

### 2.3 Regional Bigha Ambiguity Resolution
When a farmer states land in Bigha (e.g. "मेरे पास दो बीघा जमीन है"), YojanaSaathi automatically flags a regional unit notice, explains the statutory difference between Pucca and Kachha Bigha across UP regions, and prompts the farmer to confirm their exact land area before evaluating eligibility.

### 2.4 Unified Document Deduplication
Instead of gathering separate document sets for every scheme, the engine identifies shared statutory proofs (Aadhaar, Khatauni ROR, Bank Passbook, Domicile Certificate). One certified document satisfies multiple concurrent applications.

### 2.5 Strict Non-Claimant Distinction
YojanaSaathi acts as a trustworthy benefit intelligence and preparation navigator. It explicitly distinguishes between citizen preparation (what YojanaSaathi does) and official claim approval (what only designated government authorities like Tehsildars, Agriculture Officers, and Bank Branch Managers execute).

---

## 3. Technical & Operational Feasibility

- **Zero-Dependency Core:** Works offline or on low-bandwidth rural 2G/3G connections using local storage caching.
- **Multilingual Native Interaction:** 4 operational modes: Hindi (हिन्दी), English, Hinglish, and Punjabi (ਪੰਜਾਬੀ).
- **Public Domain Data Grounding:** Relies solely on published public Gazette notifications, circulars, and departmental orders.
- **Extensible Architecture:** Designed to scale from 6 core UP schemes to nationwide Central and State schemes via modular seeder registries.

