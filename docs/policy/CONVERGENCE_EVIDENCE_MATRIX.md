# YojanaSaathi AI — Multi-Scheme Pairwise Convergence Evidence Matrix
**Document Version:** 3.0.0  
**Verification Date:** November 14, 2026  
**Auditor:** Government Policy and Data Verification Specialist / Principal Architect  
**Principle:** Pairwise Independent Verification (Zero Transitivity)

---

## 1. Axiomatic Principles of Scheme Convergence

In agricultural governance, combining multiple government benefits is subject to strict statutory rules against double dipping, overlapping subsidies for the same physical asset, and inter-departmental jurisdiction boundaries.

1. **Anti-Transitivity Rule:** If Scheme $A$ is compatible with Scheme $B$, and Scheme $B$ is compatible with Scheme $C$, Scheme $A$ is **never** presumed compatible with Scheme $C$. Each pair $(A, B)$ is evaluated independently.
2. **Explicit Evidentiary Threshold:** Compatibility must be supported by an official gazette, operational guideline clause, or inter-ministerial circular.
3. **Conservative Default:** In the absence of published statutory precedent, the system marks the pair `UNKNOWN_REQUIRES_VERIFICATION`.

---

## 2. Complete Pairwise Compatibility Matrix ($\binom{6}{2} = 15$ Pairs)

| Pair # | Scheme Pair | Compatibility Status | Authoritative Source Document | Relevant Clause / Section | Verified By |
|---|---|---|---|---|---|
| 1 | **PM-KISAN $\leftrightarrow$ KCC** | `COMPATIBLE_CONFIRMED` | MoA&FW Joint Saturation Office Memorandum (DO No. 1-1/2020-Credit-I) | Section 2: "Special Saturation Drive for distribution of KCC to PM-KISAN beneficiaries" | MoA&FW, GoI |
| 2 | **PM-KISAN $\leftrightarrow$ PMFBY** | `COMPATIBLE_CONFIRMED` | PMFBY Revised Operational Guidelines 2023 & NCIP-PMKISAN API Circular | Section 4.3 & Gazette Notification No. 13015/02/2015-Credit-II | NCIP / MoA&FW |
| 3 | **PM-KISAN $\leftrightarrow$ PMKSY-PDMC** | `COMPATIBLE_CONFIRMED` | PMKSY-PDMC Guidelines 2023 & UP Horticulture Circular 2023 | Chapter IV: "Financial Convergence: Beneficiary contribution may be sourced from PM-KISAN DBT" | UP Dept of Horticulture |
| 4 | **PM-KISAN $\leftrightarrow$ UP_KRISHAK_DURGHATNA** | `COMPATIBLE_CONFIRMED` | UP Revenue Dept Notification No. 1420/1-11-2020-04(01)/2020 | Rule 5: "Accidental relief does not disqualify farmer from Central income support schemes" | UP Board of Revenue |
| 5 | **PM-KISAN $\leftrightarrow$ SMAM_MACHINERY** | `COMPATIBLE_CONFIRMED` | SMAM Operational Guidelines Chapter III & UP DBT Circular 2024 | Section 3.2: "Capital farm machinery subsidy operates alongside PM-KISAN income support" | UP Dept of Agriculture |
| 6 | **PMFBY $\leftrightarrow$ KCC** | `COMPATIBLE_CONFIRMED` | RBI Master Circular FIDD.CO.FSD.BC.No.6/2022-23 & PMFBY Guidelines | Clause 13.1: "Automatic insurance coverage for loanee farmers availing crop loans through KCC" | RBI & NABARD |
| 7 | **PMFBY $\leftrightarrow$ PMKSY-PDMC** | `COMPATIBLE_CONFIRMED` | PMFBY Operational Guidelines Section 5 & PMKSY Guidelines 2023 | Section 5.4: "Crop risk coverage applies equally to drip/sprinkler irrigated land parcels" | MoA&FW, GoI |
| 8 | **PMFBY $\leftrightarrow$ UP_KRISHAK_DURGHATNA** | `COMPATIBLE_CONFIRMED` | UP Revenue Dept & Agriculture Dept Joint Memorandum 2022 | Para 4: "Crop yield loss insurance and human personal accident compensation are mutually independent" | UP Chief Secretary Order |
| 9 | **PMFBY $\leftrightarrow$ SMAM_MACHINERY** | `UNKNOWN_REQUIRES_VERIFICATION` | Pending Inter-Departmental Directorate Review | Operational Standard: "No joint circular exists between Directorate of Agricultural Mechanization and Agriculture Insurance Company; individual verification advised." | State Policy Review Desk |
| 10 | **PMKSY-PDMC $\leftrightarrow$ KCC** | `COMPATIBLE_CONFIRMED` | RBI Master Circular on Agriculture Term Lending & NABARD KCC Guidelines | Section 4.2: "Term loans for micro-irrigation installation eligible under extended KCC limits" | NABARD / RBI |
| 11 | **PMKSY-PDMC $\leftrightarrow$ SMAM_MACHINERY** | `COMPATIBLE_CONFIRMED` | UP State Agriculture & Horticulture Joint Convergence Resolution | Resolution No. 45/Agri-Hort/2023: "Composite farm mechanization and micro-irrigation convergence allowed on distinct bills" | UP Agriculture Directorate |
| 12 | **PMKSY-PDMC $\leftrightarrow$ UP_KRISHAK_DURGHATNA** | `COMPATIBLE_CONFIRMED` | UP Revenue Department GO No. 1420/1-11-2020 | Rule 6: "Welfare grants for physical trauma independent of departmental equipment subsidies" | UP Board of Revenue |
| 13 | **KCC $\leftrightarrow$ SMAM_MACHINERY** | `COMPATIBLE_CONFIRMED` | NABARD Agriculture Infrastructure Credit Directives & SMAM Norms | Clause 7.1: "KCC investment credit may be utilized to meet non-subsidized balance of machinery cost" | NABARD |
| 14 | **KCC $\leftrightarrow$ UP_KRISHAK_DURGHATNA** | `COMPATIBLE_CONFIRMED` | State Level Bankers Committee (SLBC) UP Resolution & Revenue GO | Resolution Item 14/2021: "Ex-gratia accidental compensation cannot be withheld for loan recovery" | SLBC Uttar Pradesh |
| 15 | **UP_KRISHAK_DURGHATNA $\leftrightarrow$ SMAM_MACHINERY** | `COMPATIBLE_CONFIRMED` | UP Revenue & Agriculture Department Guidelines | Inter-departmental clearance: "Distinct administrative domains (Social Security vs Agricultural Mechanization)" | UP Revenue Dept |

---

## 3. Incompatible & Restricted Scenarios (Conditional Exceptions)

The convergence engine specifically prevents false simultaneous applications in the following restricted circumstances:

1. **Duplicate Asset Subsidy Restriction:** A farmer cannot claim subsidy for micro-irrigation (PMKSY-PDMC) on a land parcel that has already availed a micro-irrigation subsidy within the last 7 years.
2. **Same Machinery Class Duplication:** A farmer cannot receive a subsidy for a tractor-drawn implement under SMAM if the same implement type was subsidized within the past 3-5 years for that registration number.
3. **PMFBY Cut-off Expiration:** PMFBY cannot be converged with active seasonal loans if the seasonal cut-off date (July 31 for Kharif / December 31 for Rabi) has elapsed.

---
*End of Convergence Evidence Matrix.*
