# Offline Action-Plan Recovery & Low-Bandwidth Reliability Report
## YojanaSaathi AI — Rural Offline Resilience Architecture

**Date**: November 2026  
**Audience**: Technical Evaluation Committee, Spark2Scale 2026 Jury  
**Target Geography**: Uttar Pradesh (All 75 Districts, Rural & Remote Blocks)  
**Authors**: Team Aalekh (Adima Agarwal, Team Leader; Utkarsh Arora)  
**Execution Evidence**: [`docs/testing/playwright_07_offline_recovery.png`](file:///d:/YojanaSaathi/docs/testing/playwright_07_offline_recovery.png)

---

## 1. Context & The Rural Connectivity Problem

In rural Uttar Pradesh (e.g., Bundelkhand, Purvanchal, Terai border districts), smallholder farmers face severe network connectivity challenges:
- High packet drop rates and intermittent 2G/3G connectivity in agricultural fields.
- Power cuts leading to browser tab closures or phone restarts.
- Farmers losing complex eligibility results or document checklists upon losing signal.

### YojanaSaathi AI's Architectural Response
YojanaSaathi AI implements **Zero-Loss Client-Side Offline Persistence**:
1. When an Action Plan is generated, the entire plan payload—including the 7-stage roadmap, document checklist, readiness scores, and verified portal URLs—is cached in the client's `localStorage`.
2. The platform continuously monitors online/offline network transition events (`window.addEventListener('online')`, `window.addEventListener('offline')`).
3. If the farmer closes the browser, reboots their device, or loses cellular signal, the platform automatically detects the saved action plan upon reopening and enables full offline navigation.

---

## 2. Storage Architecture & Data Schema

YojanaSaathi AI writes two primary keys into the browser's origin-scoped `localStorage`:

### Key 1: `yojanasaathi_latest_plan_number`
Stores the identifier of the most recently generated plan (e.g., `YS-UP-20261114-B2896F`).

### Key 2: `yojanasaathi_plan_<PLAN_NUMBER>`
Stores the complete, self-contained JSON serialization of the citizen's personalized roadmap:

```json
{
  "plan_number": "YS-UP-20261114-B2896F",
  "created_at": "2026-11-14T08:53:35.005712+00:00",
  "selected_schemes": [
    {
      "scheme_code": "PMFBY",
      "official_name_hi": "प्रधानमंत्री फसल बीमा योजना (उत्तर प्रदेश)",
      "overall_status": "LIKELY_ELIGIBLE",
      "conditions": [ ... ]
    },
    {
      "scheme_code": "KCC",
      "official_name_hi": "किसान क्रेडिट कार्ड (केसीसी) रियायती कृषि ऋण",
      "overall_status": "LIKELY_ELIGIBLE",
      "conditions": [ ... ]
    }
  ],
  "convergence_summary": [
    {
      "scheme_code_a": "PMFBY",
      "scheme_code_b": "KCC",
      "status": "COMPATIBLE_CONFIRMED",
      "evidence_text": "Kisan Credit Card holders cultivating notified crops are automatically enrolled..."
    }
  ],
  "checklist_items": [
    {
      "id": "doc_khatauni",
      "title_hi": "खतौनी नकल अथवा काश्तकारी अनुबंध पत्र",
      "required_for_schemes": ["PMFBY", "KCC"],
      "is_ready": false,
      "source_authority": "UP Revenue Dept"
    }
  ],
  "official_steps": [
    {
      "step_number": 1,
      "title_hi": "[PMFBY] कट-ऑफ तिथि से पूर्व बैंक शाखा अथवा सीएससी द्वारा आवेदन",
      "portal_or_destination": "https://pmfby.gov.in"
    }
  ]
}
```

---

## 3. Automated Playwright Restart Verification

The offline recovery pipeline was tested via Playwright (`scripts/run_playwright_e2e.py`):

### Phase A: Generation & Caching
1. Citizen completes natural language intake and generates Action Plan `#YS-UP-20261114-B2896F`.
2. Verified that `localStorage.getItem('yojanasaathi_latest_plan_number')` contains the valid plan number.
3. Playwright exports the complete browser storage state to `docs/testing/browser_offline_state.json`.

### Phase B: Complete Process Termination
1. `browser.close()` terminates the Chrome process completely, closing all tabs and memory allocations.

### Phase C: Offline Launch & Recovery
1. A new Chrome browser is launched with the persisted `storage_state`.
2. The network context is strictly forced offline (`context.set_offline(True)`).
3. The citizen navigates to `http://localhost:5173`.
4. **Result 1 (Landing Page)**: The platform detects the cached plan in `localStorage` and displays:
   > 🟢 **सहेजी गई कार्य योजना (#YS-UP-20261114-B2896F) उपलब्ध है [योजना खोलें]**
5. **Result 2 (Action Plan View)**: Clicking `योजना खोलें` loads the full 7-stage roadmap and 6 document checklist items with zero network requests.
6. **Result 3 (Offline Banner)**: The top banner alerts the farmer:
   > ⚠️ **ऑफ़लाइन मोड सक्रिय: यह कार्य योजना आपके ब्राउज़र में सुरक्षित है और बिना इंटरनेट के उपलब्ध रहेगी।**
7. **Result 4 (Print Accessibility)**: The farmer can trigger `window.print()` to save a physical paper copy or PDF while offline.

---

## 4. Verification Evidence

- **Browser Storage Snapshot**: [`docs/testing/browser_offline_state.json`](file:///d:/YojanaSaathi/docs/testing/browser_offline_state.json)
- **Visual Screenshot Evidence**: [`docs/testing/playwright_07_offline_recovery.png`](file:///d:/YojanaSaathi/docs/testing/playwright_07_offline_recovery.png)
- **Execution Script**: [`scripts/run_playwright_e2e.py`](file:///d:/YojanaSaathi/scripts/run_playwright_e2e.py)

---

## 5. Summary Matrix: Offline Guarantees

```
+-----------------------------------+---------------------------------------------+
| Feature                           | Offline Availability Guarantee              |
+-----------------------------------+---------------------------------------------+
| Full Action Plan Viewing          | 100% Available without internet             |
| 7-Stage Application Tracker       | 100% Available without internet             |
| Interactive Document Checklist    | Toggles & state changes stored in memory     |
| Official Scheme Guidelines View   | Cached in plan payload                      |
| Print to Paper / Save to PDF      | Functional via native browser print dialogue|
| Re-launch After Device Reboot     | Automatically restored from localStorage    |
+-----------------------------------+---------------------------------------------+
```

**Certified by**: Team Aalekh (Adima Agarwal, Utkarsh Arora)  
**Date**: November 2026

