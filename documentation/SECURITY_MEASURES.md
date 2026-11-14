# 🛡️ YojanaSaathi AI — Security Architecture & Data Protection (सुरक्षा एवं डेटा संरक्षण)
> **Platform:** YojanaSaathi AI (योजना साथी AI)  
> **Team Name:** Aalekh | **Team Members:** Adima Agarwal (Team Leader), Utkarsh Arora  
> **Compliance Standard:** Digital Personal Data Protection (DPDP) Act, 2023 (India)

---

## 1. Zero-Aadhaar Persistence Architecture

### Statutory Mandate
Under the **Aadhaar (Targeted Delivery of Financial and Other Subsidies, Benefits and Services) Act, 2016** and the **DPDP Act, 2023**, storing raw 12-digit Aadhaar numbers without an authorized UIDAI-licensed core biometric repository is strictly prohibited.

### Our Engineering Defense
- **Client-Side Truncation & Masking:** Full 12-digit numbers are intercepted and truncated immediately.
- **Strict Regex Masking:** Only the last 4 digits are ever stored in audit metadata, formatted as `******1234`.
- **Database Column Enforcement:** The `FarmerDocument` table contains an explicit boolean flag `is_masked_aadhaar` and prohibits raw Aadhaar string columns.

---

## 2. Magic-Byte Binary File Inspection

### Threat Vector: MIME-Type & Extension Spoofing
Attackers can rename malicious executable files (`malware.exe`) to `my_document.pdf` to bypass standard web application file extensions.

### Our Binary Defense
Before writing any file to disk, the `validate_file_bytes` routine inspects the binary byte stream signature:
```python
if content.startswith(b"%PDF-"):
    return "application/pdf"
elif content.startswith(b"\xFF\xD8\xFF"):
    return "image/jpeg"
elif content.startswith(b"\x89PNG\r\n\x1a\n"):
    return "image/png"
else:
    raise HTTPException(status_code=415, detail="Unsupported Media Type")
```
Any file failing magic-byte inspection is rejected immediately with HTTP 415.

---

## 3. Isolated Document Storage Outside Web Root

- **UUID File Obfuscation:** Uploaded files are renamed using cryptographic UUIDs (`e.g., 91f81c85-1f78-4a17-8a31-0a6e2b7a939f.pdf`), erasing original client file paths and preventing path traversal attacks.
- **No Direct Web Execution:** Files are stored in a private directory located completely outside the public web root (`backend/storage/documents/`).
- **Controlled Retrieval:** Files can only be downloaded through authenticated, stream-validated FastAPI endpoints (`/documents/{doc_id}/download`) with strict MIME header enforcement.

---

## 4. Authentication, Session Replay & RBAC Security

- **Argon2 Password Hashing:** Industry-standard Argon2id hashing for user credential storage.
- **JWT Token Family Rotation:** Refresh tokens use session family rotation. If a compromised refresh token is re-submitted, the backend detects the replay attack and revokes the entire token family immediately.
- **Role-Based Access Control (RBAC):** Strict separation of privileges between `CITIZEN`, `OPERATOR`, and `ADMIN`. Departmental and administrative APIs are guarded by dependency-injected security gates (`get_current_admin_user`).
- **Complete Audit Trail:** Every critical lifecycle action (document toggle, upload, stage completion, final confirmation) writes an immutable record to the `AuditLog` table.
