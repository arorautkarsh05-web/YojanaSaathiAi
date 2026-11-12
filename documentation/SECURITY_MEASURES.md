# Security Architecture & Safeguards Specification
> **YojanaSaathi AI — Enterprise Security, Token Lifecycle & DPDP Act 2023 Compliance**

---

## 1. Authentication & Token Lifecycle Architecture

YojanaSaathi implements a hardened, dual-token authentication architecture designed to eliminate common vulnerabilities such as Cross-Site Scripting (XSS) credential theft, token replay, and unauthorized session extension.

```
       [ Client / Browser ]                     [ Auth Service ]                     [ Database ]
                |                                      |                                  |
                |--- POST /auth/login (credentials) -->|                                  |
                |                                      |--- PBKDF2 Password Verify ------>|
                |<-- Access Token (15m in JSON) + -----|                                  |
                |    Refresh Token (30d in HttpOnly) --|                                  |
                |                                      |--- Store Token Family & Hash --->|
                |                                                                         |
        [ On Token Expiry (15m) ]                                                         |
                |--- POST /auth/refresh (Cookie) ----->|                                  |
                |                                      |--- Check Used Status ----------->|
                |                                      |    [If previously used:          |
                |                                      |     REVOKE ENTIRE FAMILY!]       |
                |<-- New Access Token + New Refresh ---|--- Invalidate Old & Store New -->|
```

### 1.1 Stateless Short-Lived Access Tokens
- **Lifespan:** 15 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 15`).
- **Encoding:** JSON Web Token (JWT) with HMAC-SHA256 signature using an entropy-tested `SECRET_KEY`.
- **Payload:** Contains `sub` (User ID), `email`, `roles` (`FARMER`, `ASSISTANCE_WORKER`, `ADMIN`), and expiration timestamp (`exp`).
- **Transport:** Delivered in the Authorization header (`Bearer <token>`).

### 1.2 Long-Lived Refresh Tokens in `HttpOnly` Cookies
- **Lifespan:** 30 days (`REFRESH_TOKEN_EXPIRE_DAYS = 30`).
- **Cookie Security Attributes:**
  - `HttpOnly = True` — Completely inaccessible to JavaScript, eliminating token exfiltration via client-side XSS.
  - `SameSite = "Lax"` (or `"Strict"` in production) — Defends against Cross-Site Request Forgery (CSRF).
  - `Secure = True` (in HTTPS production environments).
  - Explicit path scoping (`Path=/api/v1/auth`).

### 1.3 Automatic Token Replay Attack Detection & Session Family Revocation
To protect against stolen refresh tokens, the platform implements **Token Family Tracking** (RFC 6749 Section 10.4):
1. Every issued refresh token belongs to a cryptographically tracked `family_id`.
2. When a refresh token is used, it is immediately marked as `used = True` and rotated into a new token.
3. If an attacker attempts to reuse an already-used refresh token (a replay attack):
   - The security engine detects `used == True`.
   - **Immediate Revocation:** The system immediately revokes **every token in that entire family**.
   - The legitimate user's active session is terminated, forcing re-authentication and rendering the attacker's stolen token worthless.

### 1.4 Cryptographic Password Storage
- Passwords are never stored in plaintext or with reversible encryption.
- Passwords are hashed using **PBKDF2 with SHA-256**, utilizing a unique 16-byte cryptographically secure salt per user and a minimum iteration count of 100,000 rounds.
- Passwords must meet minimum complexity criteria (minimum 8 characters, checked at registration via Pydantic).

---

## 2. Authorization & Role-Based Access Control (RBAC)

YojanaSaathi defines three distinct security personas enforced via FastAPI dependency injection:

| Role | Permissions | Security Boundary |
| :--- | :--- | :--- |
| **`GUEST`** | Discover schemes, evaluate rule eligibility, check convergence, view consolidated action plan, interact with Grounded Assistant. | **No persistence without explicit consent.** Evaluated entirely in-memory. |
| **`FARMER`** | Save evaluated profiles, generate persistent action plans, update landholding, exercise DPDP data erasure and portability rights. | Can only read and mutate records where `user_id == current_user.id`. |
| **`ASSISTANCE_WORKER`** | Help community farmers, evaluate profiles on behalf of illiterate farmers, access aggregated regional analytics. | Operates in sandboxed multi-profile mode with mandatory consent acknowledgments. |
| **`ADMIN`** | View scheme audit registers, update gazette source citations, view security audit logs, trigger policy change evaluations. | Enforced by `require_admin` dependency; unauthenticated or farmer requests receive immediate `403 Forbidden`. |

---

## 3. Privacy & Digital Personal Data Protection (DPDP) Act 2023 Compliance

YojanaSaathi was architected from inception to adhere to the statutory principles of India's **Digital Personal Data Protection Act (DPDP), 2023**:

### 3.1 Zero-Login Guest Mode (Data Minimization — Section 6(1))
Farmers can utilize 100% of the platform's core decision-support capabilities (discovering schemes, testing eligibility, viewing documents, getting an action plan) **without ever registering an account, providing an email, or entering a mobile number**. Data is processed in-memory and discarded upon session end unless the farmer explicitly requests storage.

### 3.2 Explicit & Granular Consent (Section 6(2))
Profile persistence requires affirmative, unbundled consent:
- `terms_consented`: Mandatory acknowledgement of terms and privacy guidelines.
- `profile_storage_consented`: Separate, optional toggle specifically authorizing the platform to store profile attributes across sessions.
- In guest mode, `is_temporary = True` is enforced by default.

### 3.3 Right to Erasure / "Right to be Forgotten" (Section 12(3))
Farmers retain complete sovereignty over their data:
- **API Endpoint:** `DELETE /api/v1/auth/me/data`
- **Execution:** Permanently cascades and removes all farmer profile records, evaluation histories, action plans, and active session tokens.
- **Audit Trace:** An anonymized audit log is written recording the erasure timestamp without retaining personal data.

### 3.4 Right to Data Portability (Section 12(1))
Farmers can download their entire stored record in a structured, machine-readable JSON format via `GET /api/v1/auth/me/export`.

### 3.5 No Direct Aadhaar Ingestion
To comply with UIDAI statutory restrictions and avoid storing sensitive personally identifiable information (PII):
- The platform **never collects, ingests, or stores 12-digit Aadhaar numbers** or biometric data.
- The platform merely tracks the *readiness checklist state* (e.g., `Aadhaar-seeded bank account ready: Yes/No`), ensuring zero risk of Aadhaar data leakage.

---

## 4. Input Validation & Infrastructure Defense

### 4.1 SQL Injection Defense
- 100% of database interactions are orchestrated via **SQLAlchemy ORM** using parameterized queries and strictly typed columns.
- Raw SQL string interpolation is strictly banned across the codebase.

### 4.2 Cross-Site Scripting (XSS) & Content Security
- React 19's virtual DOM natively escapes HTML entities in rendered text.
- External links rendered dynamically from scheme portals strictly enforce `target="_blank" rel="noopener noreferrer"` to prevent tab-nabbing vulnerabilities.

### 4.3 Cross-Origin Resource Sharing (CORS) Policy
- Backend CORS middleware is explicitly configured to whitelist approved origins (`http://localhost:5173`, `http://127.0.0.1:5173`). Wildcard `*` origins are rejected when credentials (`allow_credentials=True`) are enabled.

### 4.4 Automated Security Verification
The security and auth implementation is continuously validated by automated tests in [`backend/tests/test_auth.py`](file:///d:/YojanaSaathi/backend/tests/test_auth.py) and [`backend/tests/test_ranking_and_security.py`](file:///d:/YojanaSaathi/backend/tests/test_ranking_and_security.py), including:
- Generic login failure responses (preventing user enumeration).
- Unauthorized admin endpoint rejection (`403 Forbidden`).
- Token replay session family revocation.
- DPDP data deletion and portability verification.

