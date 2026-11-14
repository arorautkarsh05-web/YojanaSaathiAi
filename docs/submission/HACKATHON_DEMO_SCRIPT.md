# YojanaSaathi AI — Hackathon Live Demonstration Script (5-Minute Winning Flow)

**Team Name:** Team Aalekh  
**Team Members:** Adima Agarwal (Team Leader), Utkarsh Arora  
**Target Audience:** Hackathon Jury, Technical Evaluators, Public Policy Judges  
**Duration:** 5 Minutes  
**Live URL / Port:** `http://localhost:5173` (Frontend) | `http://localhost:8000` (Backend API)

---

## 1. Demo Narrative Arc & Timing

```
[0:00 - 0:45] The Problem & The Non-Chatbot Proposition
[0:45 - 2:00] Live Conversational Hindi Intake & Bigha Ambiguity Resolution
[2:00 - 3:15] Deterministic 3-Valued Rules & Pairwise Multi-Scheme Convergence
[3:15 - 4:15] 7-Stage Benefit Journey & Unified Document Deduplication
[4:15 - 5:00] Technical Rigor, Verification Suite, and Q&A Transition
```

---

## 2. Step-by-Step Demonstration Walkthrough

### Part 1: The Problem & Opening Hook (0:00 - 0:45)
- **Speaker:** *"Judges, every year the Indian government allocates over ₹3 Lakh Crores to agricultural welfare. Yet small farmers in Uttar Pradesh struggle across fragmented portals, while general AI chatbots hallucinate fake deadlines or give false promises of approval. Welcome to YojanaSaathi AI — not a generic chatbot, but an evidence-grounded benefit intelligence platform for all 75 districts of Uttar Pradesh."*
- **Action on Screen:** Show the landing page with the muted background video and custom agricultural field illustration. Note the prominent language selector with Hindi, English, Hinglish, and Punjabi modes.

---

### Part 2: Natural Language Hindi Intake & Bigha Ambiguity (0:45 - 2:00)
- **Speaker:** *"Instead of asking a farmer to fill out complex administrative forms, they simply speak or type their situation in their mother tongue."*
- **Action on Screen:**
  1. Click **"Ask Grounded Assistant"** on the home banner.
  2. Click the prompt suggestion chip:
     `"मेरे पास दो बीघा जमीन है, गेहूं उगाता हूं, सिंचाई चाहिए"` (or type it live).
  3. **Point out the response to judges:**
     - The assistant extracted crops (`wheat`), need (`irrigation`), and landholding (`2.0 बीघा`).
     - **Crucial Differentiator:** Show the **Regional Unit Ambiguity Notice** on screen!
       *"Notice this, judges! In Uttar Pradesh, 1 Bigha in Western UP (Pucca Bigha) is 0.625 acres, but in Eastern UP (Kachha Bigha) it is only 0.21-0.33 acres. Converting with a flat multiplier would cause statutory disqualification. Our engine detects this ambiguity, explains the difference in clear Hindi, and asks for confirmation!"*
     - Point out the missing district detection (`district: unconfirmed`).
  4. Type in the follow-up response:
     `"मैं झांसी से हूं और यह पक्का बीघा है"`
  5. The assistant confirms the profile and presents the green action button:
     **"👉 इस जानकारी से पात्रता जाँचें (Evaluate Schemes Now)"**.
  6. Click the button — it transitions directly into the results view!

---

### Part 3: Deterministic Rules & Pairwise Convergence (2:00 - 3:15)
- **Speaker:** *"This is where our engineering architecture sets us apart. The LLM does not make eligibility decisions. Our Python rules engine evaluates confirmed parameters against statutory gazettes using three-valued logic: PASS, FAIL, or UNKNOWN."*
- **Action on Screen:**
  1. Show the evaluated schemes:
     - **PMKSY-PDMC:** Evaluates correctly based on the farmer's irrigation status.
     - **KCC & PMFBY:** Displays `LIKELY_ELIGIBLE` with condition-by-condition citations.
     - **PM-KISAN:** Displays `NEEDS_MORE_INFO` because institutional exclusion status remains unverified — missing info is **never** assumed to be `PASS`.
  2. Point out the **Pairwise Convergence Badge**:
     *"Judges, notice the convergence engine. We strictly enforce pairwise independent verification ($A \sim B \land B \sim C \not\implies A \sim C$). PM-KISAN and KCC are confirmed compatible via the Ministry saturation circular; however, combinations lacking inter-departmental circulars are conservatively tagged UNKNOWN_REQUIRES_VERIFICATION."*

---

### Part 4: 7-Stage Benefit Journey & Document Deduplication (3:15 - 4:15)
- **Speaker:** *"Once the farmer selects their relevant schemes, we generate a unified, printable Action Plan."*
- **Action on Screen:**
  1. Click **"कार्य योजना तैयार करें (Generate Action Plan)"**.
  2. Point out the **7-Stage Benefit Tracker** at the top of the plan:
     - Stages 1-3: Completed ✓
     - Stage 4: Document Preparation In Progress
     - Stages 5-7: Navigation, Farmer Self-Reported, and Official Disbursement.
  3. Point out the **Document Deduplication Checklist**:
     *"Rather than gathering duplicate papers, Aadhaar and Khatauni are identified as shared across multiple schemes. The farmer checks them off, and the progress counter updates."*
  4. Note the **Offline Resilience**:
     *"If the farmer's mobile connection drops in rural Bundelkhand, this plan is cached in localStorage and opens instantly offline."*

---

### Part 5: Technical Rigor & Conclusion (4:15 - 5:00)
- **Speaker:** *"Under the hood: 57 automated tests covering full farmer lifecycles, bilingual groundings, and PostgreSQL/SQLite dual compatibility. 100% verified live government URLs, zero hallucinated statutory circulars, and strict adherence to WCAG 2.2 AA accessibility. YojanaSaathi transforms complex public policy into clear, trustworthy intelligence for every farmer in Uttar Pradesh. Thank you!"*
