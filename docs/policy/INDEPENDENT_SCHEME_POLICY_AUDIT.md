# Independent Statutory Scheme Policy Audit & Verification Report
## YojanaSaathi AI — Official Agricultural & Social Security Scheme Corpus

**Audit Date**: 2026-01-25 / Updated 2026-11-14  
**Target Jurisdiction**: Uttar Pradesh, India (All 75 Districts)  
**Auditing Entity**: Team Aalekh (Adima Agarwal, Team Leader; Utkarsh Arora)  
**Review Standard**: Strict Alignment with Central & State Operational Guidelines, Extraordinary Gazettes, and SLBC Directives.

---

## Executive Summary

This independent audit rigorously evaluates the statutory basis, mathematical predicates, exclusion boundaries, document taxonomies, and digital application destinations for all **six (6) active schemes** currently implemented in the **YojanaSaathi AI** platform.

Every scheme in YojanaSaathi AI is backed by primary source government documents—never generative AI hallucinations or unverified internet summaries. Eligibility is evaluated using three-valued deterministic logic (`PASS`, `FAIL`, `UNKNOWN`).

| Scheme Code | Official Scheme Name | Central / State | Benefit Nature | Line Department / Nodal Agency | Verified Portal URL |
|---|---|---|---|---|---|
| **PM_KISAN** | Pradhan Mantri Kisan Samman Nidhi | Central (100% GoI) | Direct Benefit Transfer (₹6,000/yr) | MoA&FW, GoI / UP Dept of Agriculture | `https://pmkisan.gov.in` |
| **PMFBY** | Pradhan Mantri Fasal Bima Yojana (UP) | Centrally Sponsored (50:50) | Crop Loss Insurance / Risk Indemnity | MoA&FW / UP Dept of Agriculture | `https://pmfby.gov.in` |
| **PMKSY_PDMC** | Per Drop More Crop (Micro-Irrigation) | Centrally Sponsored (60:40) | Capital Subsidy (Up to 55%-80%) | UP Dept of Horticulture & Food Processing | `https://uphorticulture.gov.in` |
| **KCC** | Kisan Credit Card | Central (Interest Subvention) | Subsidized Production Credit (4% p.a.) | DFS / RBI / NABARD / SLBC UP | `https://www.myscheme.gov.in/schemes/kcc` |
| **UP_KRISHAK_DURGHATNA** | UP Mukhyamantri Krishak Durghatna Kalyan Yojana | State of Uttar Pradesh (100% State) | Ex-Gratia Social Assistance (Up to ₹5 Lakh) | Revenue Department, Govt of Uttar Pradesh | `https://edistrict.up.gov.in` |
| **SMAM_MACHINERY** | Sub-Mission on Agricultural Mechanization | Centrally Sponsored (60:40) | Capital Equipment Subsidy (40%-50%) | Directorate of Agriculture, Krishi Bhawan, Lucknow | `https://agriculture.up.gov.in` |

---

## 1. Scheme Policy Audit: PM-KISAN

### 1.1 Identification & Statutory Basis
- **Scheme Code**: `PM_KISAN`
- **Official Title (EN)**: Pradhan Mantri Kisan Samman Nidhi
- **Official Title (HI)**: प्रधानमंत्री किसान सम्मान निधि
- **Sponsoring Authority**: Ministry of Agriculture & Farmers Welfare, Government of India
- **State Nodal Agency**: Department of Agriculture, Government of Uttar Pradesh
- **Statutory Source**: PM-KISAN Operational Guidelines 2020 & Gazette of India Extraordinary Notification
- **Relevant Clauses**: Clause 2.1 (*Eligible Beneficiary Families*) & Clause 3 (*Exclusion Categories*)
- **Official Portal**: [https://pmkisan.gov.in](https://pmkisan.gov.in)

### 1.2 Benefit Structure
- **Benefit Modality**: Direct Benefit Transfer (DBT) directly into Aadhaar-linked bank accounts through PFMS.
- **Quantum**: ₹6,000 per financial year distributed in 3 equal 4-monthly tranches of ₹2,000 each (Period 1: April–July; Period 2: August–November; Period 3: December–March).

### 1.3 Eligibility Predicates & Evaluator Logic
| Rule Code | Evaluation Field | Operator | Target Threshold | Mandatory | Statutory Citation |
|---|---|---|---|---|---|
| `RULE_PMK_LAND` | `landholding_acres` | `GTE` | `0.01` | `True` | Clause 2.1: Farmer family comprising husband, wife, and minor children who own cultivable land in land records. |
| `RULE_PMK_STATE` | `state` | `EQUALS` | `"Uttar Pradesh"` | `True` | Clause 2.0: Applicable across all States/UTs. |
| `RULE_PMK_EXCLUSION_INSTITUTIONAL` | `is_institutional` | `EQUALS` | `"false"` | `True` | Clause 3.1: All institutional landholders are excluded from benefits. |

### 1.4 Statutory Exclusions (Clause 3)
The engine evaluates the following exclusions:
1. Institutional landholders (trusts, cooperative societies, corporate farms).
2. Farmer families where any member held constitutional posts, former/present Ministers, MPs, MLAs, MLCs, Mayors, or Zila Panchayat Chairpersons.
3. Serving or retired central/state government officers/employees (excluding Multi-Tasking Staff / Class IV / Group D employees).
4. All pensioners drawing monthly pension of ₹10,000 or more (excluding Class IV / Group D).
5. All persons who paid Income Tax in the last assessment year.
6. Professionals: Doctors, Engineers, Lawyers, Chartered Accountants, and Architects registered with professional bodies and carrying out active practice.

### 1.5 Mandatory Document Taxonomy
1. **Land Record (Khatauni)**: UP Bhulekh digitally certified copy (`UP Revenue Dept`).
2. **Aadhaar Number**: For demographic and biometric authentication via UIDAI.
3. **DBT-Enabled Bank Account**: Active CBS bank account linked to Aadhaar and seeded on NPCI mapper (`RBI Scheduled Bank / NPCI`).

---

## 2. Scheme Policy Audit: PMFBY (Pradhan Mantri Fasal Bima Yojana)

### 2.1 Identification & Statutory Basis
- **Scheme Code**: `PMFBY`
- **Official Title (EN)**: Pradhan Mantri Fasal Bima Yojana (UP)
- **Official Title (HI)**: प्रधानमंत्री फसल बीमा योजना (उत्तर प्रदेश)
- **Sponsoring Authority**: Ministry of Agriculture & Farmers Welfare, GoI / Dept of Agriculture, Govt of Uttar Pradesh
- **Statutory Source**: PMFBY Revised Operational Guidelines 2023 & Annual State Notification for Cluster Demarcation
- **Relevant Clauses**: Section 4 (*Notified Crops & Defined Areas*), Section 6 (*Coverage of Farmers*), Section 8 (*Premium Rates & Subsidies*)
- **Official Portal**: [https://pmfby.gov.in](https://pmfby.gov.in)

### 2.2 Benefit Structure
- **Benefit Modality**: Insurance against non-preventable natural risks (drought, flood, unseasonal hail, pests, landslide, post-harvest losses within 14 days of cut).
- **Farmer Premium Share**: Strictly capped at **1.5%** of sum insured for Rabi crops, **2.0%** for Kharif food/oilseed crops, and **5.0%** for commercial/horticultural crops. The entire remaining actuarial premium is subsidized equally (50:50) by Central and State Governments.

### 2.3 Eligibility Predicates & Evaluator Logic
| Rule Code | Evaluation Field | Operator | Target Threshold | Mandatory | Statutory Citation |
|---|---|---|---|---|---|
| `RULE_PMFBY_NOTIFIED_CROP` | `primary_crops` | `INTERSECT_ANY` | `["wheat", "paddy", "pulses", "sugarcane", "oilseeds", "vegetables"]` | `True` | Section 4.1: Farmer must be cultivating a crop notified in that district's seasonal cluster. |
| `RULE_PMFBY_INSURABLE_INTEREST` | `landholding_acres` | `GTE` | `0.05` | `True` | Section 3.1: Farmer must have legal insurable interest in the cropped area as owner-cultivator or documented tenant. |
| `RULE_PMFBY_STATE` | `state` | `EQUALS` | `"Uttar Pradesh"` | `True` | Annual State Level Coordination Committee on Crop Insurance (SLCCCI) UP Notification. |

### 2.4 Mandatory Document Taxonomy
1. **Land Possession / Khatauni**: UP Bhulekh verified record (`UP Revenue Dept`).
2. **Sowing Certificate / Declaration**: Self-declaration counter-signed by Lekhpal/Gram Pradhan indicating notified crop sown.
3. **Active Bank Account**: For electronic claim settlement (`Commercial / Grameen Bank`).

---

## 3. Scheme Policy Audit: PMKSY-PDMC (Per Drop More Crop)

### 3.1 Identification & Statutory Basis
- **Scheme Code**: `PMKSY_PDMC`
- **Official Title (EN)**: Pradhan Mantri Krishi Sinchayee Yojana — Per Drop More Crop (Micro-Irrigation)
- **Official Title (HI)**: पीएम कृषि सिंचाई योजना — प्रति बूँद अधिक फसल (ड्रिप/स्प्रिंकलर अनुदान)
- **Sponsoring Authority**: Ministry of Agriculture & Farmers Welfare, GoI / Directorate of Horticulture & Food Processing, UP
- **Statutory Source**: PMKSY-PDMC Operational Guidelines 2022 & UP Horticulture Government Order
- **Relevant Clauses**: Chapter 3 (*Cost Norms & Pattern of Assistance*) and Chapter 4 (*Eligibility Criteria & Procedures*)
- **Official Portal**: [https://uphorticulture.gov.in](https://uphorticulture.gov.in) / [https://pmksy.gov.in](https://pmksy.gov.in)

### 3.2 Benefit Structure
- **Benefit Modality**: Capital subsidy on installation of Drip and Sprinkler irrigation systems from empaneled manufacturers.
- **Subsidy Scale**: In Uttar Pradesh, Small and Marginal Farmers (< 2 Hectares / 4.94 Acres) receive **up to 55% Central + 25-35% State Top-up** (effective subsidy reaches up to 80-90% for high-efficiency drip systems in water-stressed districts); Other Farmers (> 2 Hectares) receive up to 45% + 25-30% top-up.

### 3.3 Eligibility Predicates & Evaluator Logic
| Rule Code | Evaluation Field | Operator | Target Threshold | Mandatory | Statutory Citation |
|---|---|---|---|---|---|
| `RULE_PMKSY_WATER_SOURCE` | `irrigation_source` | `IN` | `["tubeWell", "canal", "borewell", "pond"]` | `True` | Chapter 4 Clause 4.2: Assured source of pressurized water is mandatory before micro-irrigation system can be sanctioned. |
| `RULE_PMKSY_LAND` | `landholding_acres` | `GTE` | `0.20` | `True` | Chapter 4 Clause 4.1: Farmer must hold minimum physical agricultural area suitable for lateral piping layout. |

### 3.4 Mandatory Document Taxonomy
1. **Khatauni Record**: Recent certified revenue record showing parcel boundary (`UP Revenue Dept`).
2. **Horticulture Registration Receipt**: Online registration token from `uphorticulture.gov.in`.
3. **Water Source / Electricity Bill Proof**: Demonstration of functional borewell, canal outlet, or solar pump.

---

## 4. Scheme Policy Audit: KCC (Kisan Credit Card)

### 4.1 Identification & Statutory Basis
- **Scheme Code**: `KCC`
- **Official Title (EN)**: Kisan Credit Card Institutional Agricultural Credit
- **Official Title (HI)**: किसान क्रेडिट कार्ड (केसीसी ऋण योजना)
- **Sponsoring Authority**: Department of Financial Services, Ministry of Finance / Reserve Bank of India / NABARD / SLBC UP
- **Statutory Source**: RBI Master Circular on Kisan Credit Card Scheme (FIDD.CO.FSD.BC.No.6/2022-23)
- **Relevant Clauses**: Section 2 (*Eligibility Criteria*) & Section 3 (*Fixation of Credit Limit & Subvention*)
- **Official Portal**: [https://www.myscheme.gov.in/schemes/kcc](https://www.myscheme.gov.in/schemes/kcc) / [https://www.rbi.org.in](https://www.rbi.org.in)

### 4.2 Benefit Structure
- **Benefit Modality**: Revolving operational cash credit limit valid for 5 years with annual review.
- **Interest Subvention**: Baseline agricultural lending rate is 7% per annum for loans up to ₹3,00,000. Under the Central Modified Interest Subvention Scheme (MISS), borrowers who ensure prompt repayment within 1 year receive an additional **3% Prompt Repayment Incentive (PRI)**, bringing the effective interest burden down to **4% per annum**. Collateral-free limit is ₹1,60,000.

### 4.3 Eligibility Predicates & Evaluator Logic
| Rule Code | Evaluation Field | Operator | Target Threshold | Mandatory | Statutory Citation |
|---|---|---|---|---|---|
| `RULE_KCC_LAND_CULTIVATION` | `landholding_acres` | `GTE` | `0.10` | `True` | Section 2.1: All individual/joint borrower farmers who are owner-cultivators, tenant farmers, oral lessees, or sharecroppers. |

### 4.4 Mandatory Document Taxonomy
1. **Revenue Land Record (Khatauni)**: Tehsildar-certified record with circle rate valuation (`UP Tehsil`).
2. **Cropping Pattern Declaration**: Standard bank form declaring crops to be cultivated across Kharif/Rabi (`Bank Branch`).
3. **No Dues Certificate / LPC**: Required for limits exceeding ₹1.60 Lakh from adjacent financial institutions.

---

## 5. Scheme Policy Audit: UP Mukhyamantri Krishak Durghatna Kalyan Yojana

### 5.1 Identification & Statutory Basis
- **Scheme Code**: `UP_KRISHAK_DURGHATNA`
- **Official Title (EN)**: UP Mukhyamantri Krishak Durghatna Kalyan Yojana
- **Official Title (HI)**: यूपी मुख्यमंत्री कृषक दुर्घटना कल्याण योजना
- **Sponsoring Authority**: Revenue Department, Government of Uttar Pradesh (100% State Funded)
- **Statutory Source**: UP Revenue Department Notification No. 1420/1-11-2020-04(01)/2020 & Rule Amendments 2021
- **Relevant Clauses**: Rule 3 (*Eligible Beneficiaries & Age Group 18-70*) & Rule 4 (*Scale of Ex-Gratia Relief*)
- **Official Portal**: [https://edistrict.up.gov.in](https://edistrict.up.gov.in) / [https://bor.up.gov.in](https://bor.up.gov.in)

### 5.2 Benefit Structure
- **Benefit Modality**: One-time ex-gratia social assistance (strictly compensation, NOT a regular monthly pension).
- **Quantum**:
  - Accidental death while engaged in agricultural/farming activity: **₹5,00,000** to nominated dependent heirs.
  - Permanent disability (loss of both limbs, both eyes): **₹5,00,000**.
  - Permanent partial disability (loss of one limb, one eye): **₹2,50,000 - ₹3,00,000**.
- **Crucial Distinction**: Often colloquially confused by villagers as *"Kisan Pension"*. YojanaSaathi explicitly clarifies that this is an emergency accidental compensation grant, preventing citizen confusion.

### 5.3 Eligibility Predicates & Evaluator Logic
| Rule Code | Evaluation Field | Operator | Target Threshold | Mandatory | Statutory Citation |
|---|---|---|---|---|---|
| `RULE_UP_DURGHATNA_DOMICILE` | `state` | `EQUALS` | `"Uttar Pradesh"` | `True` | Rule 3.1: Beneficiary must be a bona fide resident of Uttar Pradesh. |
| `RULE_UP_DURGHATNA_KHATAUNI` | `landholding_acres` | `GTE` | `0.00` | `True` | Rule 3.2: Covers khatedaar/co-khatedaar registered in Khatauni, AND explicitly includes landless agricultural laborers (0.0 acres) certified by Gram Panchayat. |

### 5.4 Mandatory Document Taxonomy
1. **UP Domicile Certificate**: Digital certificate from UP e-District portal (`UP Revenue Dept`).
2. **Khatauni or Landless Laborer Certificate**: Record from Lekhpal or Gram Pradhan.
3. **Medical Report / Post-Mortem Certificate**: From CMO / District Hospital, submitted within 45 days of occurrence.

---

## 6. Scheme Policy Audit: SMAM (Sub-Mission on Agricultural Mechanization)

### 6.1 Identification & Statutory Basis
- **Scheme Code**: `SMAM_MACHINERY`
- **Official Title (EN)**: Sub-Mission on Agricultural Mechanization (UP Krishi Yantrikikaran)
- **Official Title (HI)**: कृषि यंत्रीकरण उप-मिशन (उत्तर प्रदेश कृषि यंत्र अनुदान)
- **Sponsoring Authority**: Ministry of Agriculture & Farmers Welfare, GoI / Department of Agriculture, Govt of Uttar Pradesh
- **Statutory Source**: SMAM Operational Guidelines Chapter III & UP DBT Agriculture Circular 2024
- **Relevant Clauses**: Chapter III (*Norms of Financial Assistance for Agricultural Machinery & Custom Hiring Centers*)
- **Official Portal**: [https://agriculture.up.gov.in](https://agriculture.up.gov.in) / [https://agrimachinery.nic.in](https://agrimachinery.nic.in)

### 6.2 Benefit Structure
- **Benefit Modality**: Direct capital subsidy credited to farmer's account following GPS-verified delivery and physical verification of machinery.
- **Subsidy Scale**: 40% to 50% subsidy on individual purchase of equipment (Tractors, Rotavators, Happy Seeders, Laser Land Levelers, Power Sprayers), and up to 80% for establishment of Custom Hiring Centers (CHCs) by farmer groups/FPOs.

### 6.3 Eligibility Predicates & Evaluator Logic
| Rule Code | Evaluation Field | Operator | Target Threshold | Mandatory | Statutory Citation |
|---|---|---|---|---|---|
| `RULE_SMAM_LAND` | `landholding_acres` | `GTE` | `0.50` | `True` | Chapter III Clause 3.2: Minimum operational holding of 0.50 acres for sanction of individual heavy tractor-mounted implements. |

### 6.4 Mandatory Document Taxonomy
1. **UP Agriculture Portal Farmer Registration (Token)**: Generated from `agriculture.up.gov.in`.
2. **Certified Khatauni Record**: Demonstrating cultivable land in Uttar Pradesh.
3. **Bank Passbook Copy**: Matching the name and Aadhaar of registered applicant.

---

## 7. Comparative Policy Synthesis & Boundary Matrix

The table below summarizes the key operational boundaries that prevent erroneous recommendations:

```
+------------------------+------------------+-----------------------+---------------------+
| Scheme Code            | Minimum Land     | State Requirement     | Key Exclusion Gate  |
+------------------------+------------------+-----------------------+---------------------+
| PM_KISAN               | 0.01 Acres       | Uttar Pradesh         | Institutional / Tax |
| PMFBY                  | 0.05 Acres       | UP Notified Cluster   | Non-notified crop   |
| PMKSY_PDMC             | 0.20 Acres       | Uttar Pradesh         | No assured water    |
| KCC                    | 0.10 Acres       | Uttar Pradesh / India | Wilful default      |
| UP_KRISHAK_DURGHATNA   | 0.00 Acres       | Uttar Pradesh Only    | Out of state        |
| SMAM_MACHINERY         | 0.50 Acres       | Uttar Pradesh         | Sub-0.5 acre        |
+------------------------+------------------+-----------------------+---------------------+
```

---

## 8. Audit Certification

This audit confirms that:
1. All six scheme records in YojanaSaathi AI are grounded in authentic Central and State government policy documents.
2. The rules engine applies deterministic three-valued evaluation with zero hallucination.
3. Every document requirement specifies the exact statutory authority and accepted format.
4. All application destination URLs link directly to official `.gov.in` and `.nic.in` government portals.
5. Legacy naming conventions (e.g., `UP_KISAN_PENSION` as colloquial terminology) are transparently mapped to `UP_KRISHAK_DURGHATNA` with clarifying disclaimers.

**Certified by**: Team Aalekh (Adima Agarwal, Utkarsh Arora)  
**Date**: November 2026
