# YojanaSaathi AI — Technical & Architectural Differentiators

**Document Version:** 3.0.0  
**Comparison:** YojanaSaathi AI vs. Generic Conversational Chatbots vs. Static Government Portals

---

## 1. Architectural Comparison Matrix

| Dimension | Generic AI Chatbot (e.g. ChatGPT wrapper) | Static Government Portal (e.g. MyScheme, State DBT) | **YojanaSaathi AI (Team Aalekh)** |
|---|---|---|---|
| **Eligibility Decision Logic** | Probabilistic token generation (High hallucination risk) | Rigid hardcoded forms; fails on missing/unstructured data | **Deterministic Three-Valued Logic (`PASS`, `FAIL`, `UNKNOWN`) in Python rules engine** |
| **Multi-Scheme Convergence** | Frequently hallucinates double-dipping claims or false transitivity | No inter-departmental convergence; each scheme lives in a silo | **Pairwise independent verification with documentary gazette citations ($\binom{N}{2}$ matrix)** |
| **Regional Land Measurements** | Converts Bigha with a single arbitrary constant (e.g. 0.4 or 0.62) | Only accepts numeric numbers in Acres/Hectares | **Detects regional Bigha variations (Pucca ~0.625 ac vs Kachha ~0.21-0.33 ac) and prompts farmer** |
| **Document Processing** | Generates generic lists; no cross-scheme deduplication | Farmer re-uploads same document on 5 different department portals | **Automated shared document deduplication across selected scheme portfolios** |
| **Evidence Traceability** | Fabricates circular numbers, dead links, or phone numbers | Links exist but often broken or outdated (404/503) | **100% verified, live 200 OK official government destination links with exact clause citations** |
| **Conversational Intake** | Unstructured chat; cannot transition into verified rules evaluation | No conversational intake; farmer must fill tabular dropdowns | **Multilingual NLP extracts parameters and feeds directly into deterministic rules engine** |
| **Offline Rural Accessibility** | Requires high-speed internet connection for every prompt | Heavy web pages; crashes on network disconnects | **Client-side localStorage caching; action plans accessible fully offline** |
| **Sovereign Non-Claimant Distinction** | Claims "You are eligible for Rs 50,000" (Misleading approval) | Administrative portal; processes official claim | **Explicitly separates citizen preparation/guidance from sovereign government approval** |

---

## 2. Key Engineering Innovations

1. **Decoupled LLM Architecture:** The LLM is restricted to its strengths (natural language understanding, language detection, intent classification, and explanation generation). It is strictly barred from making statutory eligibility determinations.
2. **Anti-Transitive Convergence Theory:** Formal implementation of multi-scheme graph compatibility:
   $$\text{Compatibility}(A, C) \neq \text{Compatibility}(A, B) \land \text{Compatibility}(B, C)$$
   Ensures that no farmer is advised to pursue an illegal subsidy combination based on invalid algorithmic assumptions.
3. **57-Scenario Automated Test Battery:** Full coverage of boundary conditions, negative numbers, missing profile fields, role-based security, and dual database dialect compatibility.
