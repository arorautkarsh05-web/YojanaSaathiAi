# YojanaSaathi AI — Comprehensive API Reference

All backend API routes are prefixed under `/api` and conform to OpenAPI 3.1 specifications. Interactive Swagger documentation is available at `http://localhost:8000/docs` and ReDoc at `http://localhost:8000/redoc`.

---

## 1. Authentication & Session Management (`/api/auth`)

### 1.1 User Registration
- **Endpoint:** `POST /api/auth/register`
- **Request Body:**
  ```json
  {
    "email": "farmer@example.com",
    "password": "SecurePassword123!",
    "display_name": "Ramesh Kumar",
    "terms_consented": true
  }
  ```
- **Response:** `200 OK` with user details and access token.

### 1.2 User Login
- **Endpoint:** `POST /api/auth/login`
- **Request Body:**
  ```json
  {
    "email": "farmer@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response:** `200 OK` with JWT bearer token and user role payload.

### 1.3 User Logout & Token Revocation
- **Endpoint:** `POST /api/auth/logout`
- **Headers:** `Authorization: Bearer <TOKEN>`
- **Response:** `200 OK` (revokes session family).

---

## 2. Farmer Profiles (`/api/profiles`)

### 2.1 Create or Update Profile
- **Endpoint:** `POST /api/profiles/`
- **Request Body:**
  ```json
  {
    "district": "Varanasi",
    "landholding_acres": 1.25,
    "farmer_category": "MARGINAL",
    "primary_crops": ["wheat", "paddy"],
    "social_category": "OBC",
    "irrigation_source": "TUBEWELL",
    "is_temporary": true
  }
  ```
- **Response:** `200 OK` with profile UUID and timestamp.

---

## 3. Grounded AI Assistant & Natural Language Intake (`/api/assistant`)

### 3.1 Grounded Scheme Q&A
- **Endpoint:** `POST /api/assistant/query`
- **Request Body:**
  ```json
  {
    "query": "पीएम-किसान में ₹6000 की किस्त कब मिलती है?",
    "scheme_code": "PM_KISAN",
    "language": "hi"
  }
  ```
- **Response:**
  ```json
  {
    "answer": "पीएम-किसान योजना के तहत पात्र किसान परिवारों को प्रति वर्ष ₹6,000 की आर्थिक सहायता ₹2,000 की तीन समान किस्तों में दी जाती है।",
    "source_title": "PM-KISAN Operational Guidelines 2020",
    "authority": "Ministry of Agriculture & Farmers Welfare, GoI",
    "section": "Clause 3: Financial Benefit & Disbursement Cycle",
    "verified_at": "2026-01-15T10:00:00Z",
    "can_verify": true,
    "detected_language": "hi"
  }
  ```

### 3.2 Conversational Farmer Intake & Extraction
- **Endpoint:** `POST /api/assistant/intake`
- **Request Body:**
  ```json
  {
    "text": "मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।",
    "preferred_language": "hi"
  }
  ```
- **Response:**
  ```json
  {
    "detected_language": "hi",
    "intent": "irrigation_subsidy",
    "extracted_parameters": {
      "landholding_raw": "दो बीघा",
      "land_unit": "bigha",
      "crops": ["wheat"],
      "stated_needs": ["irrigation"]
    },
    "ambiguities": [
      {
        "field": "landholding",
        "issue": "LOCAL_UNIT_VARIATION",
        "prompt": "उत्तर प्रदेश में पक्का बीघा (~0.625 एकड़) और कच्चा बीघा (~0.21-0.33 एकड़) अलग होते हैं। कृपया स्पष्ट करें।"
      }
    ],
    "missing_information": ["district"],
    "follow_up_questions": [
      "आप उत्तर प्रदेश के किस जिले से हैं?",
      "क्या आपकी जमीन पक्का बीघा है या कच्चा बीघा?"
    ],
    "can_proceed_to_evaluation": false
  }
  ```

---

## 4. Deterministic Recommendations (`/api/recommendations`)

### 4.1 Evaluate Eligibility & Generate Recommendations
- **Endpoint:** `POST /api/recommendations/`
- **Request Body:**
  ```json
  {
    "stated_needs": ["irrigation", "income_support"],
    "profile": {
      "district": "Jhansi",
      "landholding_acres": 1.25,
      "primary_crops": ["wheat", "gram"],
      "irrigation_source": "RAINFED"
    }
  }
  ```
- **Response:** Evaluated schemes with deterministic outcomes (`LIKELY_ELIGIBLE`, `NEEDS_MORE_INFO`, `LIKELY_NOT_ELIGIBLE`), condition-level status (`PASS`, `FAIL`, `UNKNOWN`), ranking scores, and official citations.

---

## 5. Pairwise Scheme Convergence (`/api/convergence`)

### 5.1 Check Scheme Pairwise Compatibility
- **Endpoint:** `POST /api/convergence/check`
- **Request Body:**
  ```json
  {
    "scheme_codes": ["PM_KISAN", "KCC", "PMKSY_PDMC"]
  }
  ```
- **Response:** Array of evaluated pairs with evidence status (`COMPATIBLE_CONFIRMED`, `INCOMPATIBLE_CONFIRMED`, `UNKNOWN_REQUIRES_VERIFICATION`).

### 5.2 Convergence Network Graph
- **Endpoint:** `GET /api/convergence/graph`
- **Response:** Graph topology (`nodes`, `edges`) for interactive visual rendering.

---

## 6. Action Plans & Document Readiness (`/api/action-plans`)

### 6.1 Create Unified Action Plan
- **Endpoint:** `POST /api/action-plans/`
- **Request Body:**
  ```json
  {
    "selected_scheme_codes": ["PM_KISAN", "KCC", "PMKSY_PDMC"],
    "profile": {
      "district": "Barabanki",
      "landholding_acres": 2.5,
      "primary_crops": ["paddy", "mustard"]
    }
  }
  ```
- **Response:** Plan identifier (`UP-AP-2026-XXXXX`), deduplicated document checklist, official application navigation steps, and disclaimer.

---

## 7. Administrative Audit & Policy Impact (`/api/admin`)

- `GET /api/admin/overview`: System operational metrics and verified rule counts.
- `GET /api/admin/audit-logs`: Paginated security and change audit trails.
- `POST /api/admin/policy-impact`: Simulates downstream citizen impact when a policy rule changes.

