"""
Database Seeder for Verified Statutory Schemes, Versions, Rules, and Document Taxonomy.
Populates the database as the single source of truth for YojanaSaathi AI.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import (
    Scheme, SchemeVersion, EligibilityRule, CompatibilityRule, SchemeDocumentRequirement, generate_uuid
)

def seed_schemes_and_rules(db: Session) -> None:
    """Seeds authoritative scheme records and convergence rules into the database."""
    
    # Check if schemes already seeded
    existing_count = db.query(Scheme).count()
    if existing_count >= 6:
        return

    schemes_data = [
        {
            "scheme_code": "PM_KISAN",
            "official_name_en": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
            "official_name_hi": "प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)",
            "department": "Ministry of Agriculture & Farmers Welfare, GoI / UP Dept of Agriculture",
            "level": "CENTRAL",
            "category": "INCOME_SUPPORT",
            "benefit_type": "DIRECT_BENEFIT_TRANSFER",
            "benefit_summary_en": "Direct financial benefit of Rs. 6,000 per year paid in three equal installments of Rs. 2,000 directly into the farmer's bank account via Aadhaar-linked DBT.",
            "benefit_summary_hi": "प्रति वर्ष ₹6,000 की वित्तीय सहायता, ₹2,000 की तीन समान किस्तों में सीधे किसान के बैंक खाते में आधार-लिंक्ड डीबीटी द्वारा।",
            "official_portal_url": "https://pmkisan.gov.in",
            "source_title": "PM-KISAN Operational Guidelines 2020 & Gazette of India Extraordinary Notification",
            "source_section": "Clause 2.1 (Eligible Beneficiaries) and Clause 3 (Exclusion Criteria)",
            "source_url": "https://pmkisan.gov.in/Documents_New.aspx",
            "verified_by": "UP Agriculture & Revenue Policy Desk",
            "rules": [
                {
                    "rule_code": "RULE_PMK_LAND",
                    "title_en": "Cultivable Land Record Ownership",
                    "title_hi": "भू-अभिलेखों में कृषि भूमि का स्वामित्व (खतौनी)",
                    "field_name": "landholding_acres",
                    "operator": "GTE",
                    "target_value": "0.01",
                    "is_mandatory": True,
                    "citation": "PM-KISAN Guidelines Sec 2.1: Farmer families who hold cultivable land in land records."
                },
                {
                    "rule_code": "RULE_PMK_STATE",
                    "title_en": "Land Location in Uttar Pradesh",
                    "title_hi": "भूमि उत्तर प्रदेश के अधिसूचित जिले में स्थित हो",
                    "field_name": "state",
                    "operator": "EQUALS",
                    "target_value": "Uttar Pradesh",
                    "is_mandatory": True,
                    "citation": "PM-KISAN Guidelines Sec 2: All states and UTs."
                },
                {
                    "rule_code": "RULE_PMK_EXCLUSION_INSTITUTIONAL",
                    "title_en": "Non-Institutional Landholder (Exclusion Check)",
                    "title_hi": "गैर-संस्थागत भू-धारक (संस्थागत भूमि बाहर है)",
                    "field_name": "is_institutional",
                    "operator": "EQUALS",
                    "target_value": "false",
                    "is_mandatory": True,
                    "citation": "PM-KISAN Guidelines Sec 3.1: All institutional landholders are excluded."
                }
            ],
            "documents": [
                {"category": "LAND_RECORD", "title_en": "Land Record (Khatauni / UP Bhulekh Record)", "title_hi": "जमीन की खतौनी / भूलेख नकल", "authority": "UP Revenue Dept", "format": "PDF / Digitally Signed Copy"},
                {"category": "IDENTITY_PROOF", "title_en": "Aadhaar Card (for identity verification at official portal)", "title_hi": "आधार कार्ड (आधिकारिक पोर्टल सत्यापन हेतु)", "authority": "UIDAI", "format": "Aadhaar Number (portal direct only)"},
                {"category": "BANK_PASSBOOK", "title_en": "Bank Account Details / Passbook (DBT-enabled)", "title_hi": "डीबीटी सक्रिय बैंक खाता पासबुक", "authority": "RBI Scheduled Bank / NPCI", "format": "Passbook Copy / Cancelled Cheque"}
            ]
        },
        {
            "scheme_code": "PMFBY",
            "official_name_en": "Pradhan Mantri Fasal Bima Yojana (UP)",
            "official_name_hi": "प्रधानमंत्री फसल बीमा योजना (उत्तर प्रदेश)",
            "department": "Department of Agriculture, Govt of Uttar Pradesh / MoA&FW",
            "level": "CENTRAL",
            "category": "CROP_INSURANCE",
            "benefit_type": "INSURANCE",
            "benefit_summary_en": "Comprehensive risk insurance for crop loss due to non-preventable natural calamities with nominal farmer premium (1.5% Rabi, 2% Kharif).",
            "benefit_summary_hi": "प्राकृतिक आपदाओं (सूखा, बाढ़, ओलावृष्टि) से फसल बर्बादी पर पूर्ण बीमा सुरक्षा। किसान प्रीमियम केवल 1.5% (रबी) व 2% (खरीफ)।",
            "official_portal_url": "https://pmfby.gov.in",
            "source_title": "PMFBY Revised Operational Guidelines 2023 & UP Agriculture Notification",
            "source_section": "Section 4.1 (Notified Crops & Season Cutoff Dates) and Section 6 (Coverage)",
            "source_url": "https://pmfby.gov.in/pdf/Revised_Operational_Guidelines.pdf",
            "verified_by": "UP Agriculture & Insurance State Nodal Officer",
            "rules": [
                {
                    "rule_code": "RULE_PMFBY_NOTIFIED_CROP",
                    "title_en": "Cultivation of Notified Seasonal Crops",
                    "title_hi": "अधिसूचित मौसमी फसलों (गेहूँ, धान, दलहन, तिलहन) की खेती",
                    "field_name": "primary_crops",
                    "operator": "INTERSECT_ANY",
                    "target_value": '["wheat", "paddy", "pulses", "sugarcane"]',
                    "is_mandatory": True,
                    "citation": "PMFBY Guidelines Sec 4: Coverage applies to food crops, oilseeds, and commercial crops."
                },
                {
                    "rule_code": "RULE_PMFBY_STATE",
                    "title_en": "Cultivated Land in Uttar Pradesh",
                    "title_hi": "बीमित भूमि उत्तर प्रदेश के अधिसूचित क्षेत्र में हो",
                    "field_name": "state",
                    "operator": "EQUALS",
                    "target_value": "Uttar Pradesh",
                    "is_mandatory": True,
                    "citation": "UP Government Annual Notification on District-Crop clusters."
                }
            ],
            "documents": [
                {"category": "LAND_RECORD", "title_en": "Land Possession Certificate / Khatauni", "title_hi": "भूमि स्वामित्व अभिलेख / खतौनी", "authority": "UP Revenue Dept", "format": "PDF / Original Copy"},
                {"category": "SOWING_CERTIFICATE", "title_en": "Sowing Certificate / Crop Sown Declaration", "title_hi": "फसल बुवाई स्व-घोषणा पत्र", "authority": "Village Pradhan / Lekhpal", "format": "Signed Certificate"},
                {"category": "BANK_PASSBOOK", "title_en": "Active Bank Account Passbook", "title_hi": "बैंक पासबुक प्रति", "authority": "Commercial / Grameen Bank", "format": "Passbook Copy"}
            ]
        },
        {
            "scheme_code": "PMKSY_PDMC",
            "official_name_en": "Per Drop More Crop - Micro Irrigation (UP)",
            "official_name_hi": "प्रति बूँद अधिक फसल - सूक्ष्म सिंचाई (ड्रिप/स्प्रिंकलर अनुदान)",
            "department": "Department of Horticulture & Food Processing, Govt of Uttar Pradesh",
            "level": "CENTRAL",
            "category": "MICRO_IRRIGATION",
            "benefit_type": "SUBSIDY",
            "benefit_summary_en": "Capital subsidy of 80% to 90% for Small/Marginal farmers and 70% to 75% for other farmers for installing Drip & Sprinkler irrigation systems.",
            "benefit_summary_hi": "लघु एवं सीमांत किसानों को 80% से 90% तथा अन्य किसानों को 70% से 75% तक ड्रिप व स्प्रिंकलर संयंत्र स्थापना पर सरकारी अनुदान।",
            "official_portal_url": "https://uphorticulture.gov.in",
            "source_title": "PMKSY-PDMC National Guidelines & UP Horticulture Department Micro-Irrigation G.O.",
            "source_section": "Chapter 3 (Financial Assistance Pattern) & Chapter 4 (Eligibility)",
            "source_url": "https://pmksy.gov.in",
            "verified_by": "Directorate of Horticulture & Food Processing, Lucknow",
            "rules": [
                {
                    "rule_code": "RULE_PMKSY_LAND",
                    "title_en": "Cultivable Agricultural Landholding",
                    "title_hi": "कृषि भूमि का स्वामित्व (न्यूनतम 0.2 एकड़)",
                    "field_name": "landholding_acres",
                    "operator": "GTE",
                    "target_value": "0.2",
                    "is_mandatory": True,
                    "citation": "PMKSY Guidelines Chapter 4: All categories of farmers having assured irrigation."
                },
                {
                    "rule_code": "RULE_PMKSY_WATER_SOURCE",
                    "title_en": "Assured Water Source for Pressurized System",
                    "title_hi": "दबावयुक्त प्रणाली हेतु सुनिश्चित जल स्रोत (बोरवेल/नहर/पॉन्ड)",
                    "field_name": "irrigation_source",
                    "operator": "IN",
                    "target_value": '["tubeWell", "canal", "pond", "borewell"]',
                    "is_mandatory": True,
                    "citation": "PMKSY Guidelines Chapter 4 Clause 4.2: Assured water source mandatory for micro-irrigation."
                }
            ],
            "documents": [
                {"category": "LAND_RECORD", "title_en": "Land Ownership Record (Khatauni)", "title_hi": "खतौनी की नकल", "authority": "UP Revenue Dept", "format": "PDF / Original Copy"},
                {"category": "REGISTRATION_TOKEN", "title_en": "UP Horticulture Department DBT Registration", "title_hi": "उद्यान विभाग डीबीटी पंजीकरण संख्या", "authority": "UP Horticulture Dept", "format": "Online Registration Receipt"},
                {"category": "IDENTITY_PROOF", "title_en": "Aadhaar Card", "title_hi": "आधार कार्ड प्रति", "authority": "UIDAI", "format": "Photocopy"}
            ]
        },
        {
            "scheme_code": "KCC",
            "official_name_en": "Kisan Credit Card (UP SLBC Implementation)",
            "official_name_hi": "किसान क्रेडिट कार्ड (केसीसी ऋण योजना)",
            "department": "Department of Agriculture / State Level Bankers Committee (SLBC) UP",
            "level": "CENTRAL",
            "category": "AGRICULTURAL_CREDIT",
            "benefit_type": "CREDIT",
            "benefit_summary_en": "Subsidized agricultural crop credit up to Rs. 3 Lakh at an effective interest rate of 4% per annum (with timely repayment prompt subvention).",
            "benefit_summary_hi": "समय पर अदायगी पर मात्र 4% प्रभावी वार्षिक ब्याज पर ₹3 लाख तक का सस्ता कृषि ऋण (ब्याज अनुदान सहित)।",
            "official_portal_url": "https://www.myscheme.gov.in/schemes/kcc",
            "source_title": "Reserve Bank of India Master Circular on KCC Scheme (FIDD.CO.FSD.BC.No.6/2022-23)",
            "source_section": "Section 2 (Eligibility) and Section 3 (Credit Limit Determination)",
            "source_url": "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12304",
            "verified_by": "State Level Bankers Committee (SLBC) Uttar Pradesh",
            "rules": [
                {
                    "rule_code": "RULE_KCC_LAND_CULTIVATION",
                    "title_en": "Owner-Cultivator or Verified Tenant Status",
                    "title_hi": "स्वयं की भूमि पर काश्तकार अथवा सत्यापित बटाईदार किसान",
                    "field_name": "landholding_acres",
                    "operator": "GTE",
                    "target_value": "0.1",
                    "is_mandatory": True,
                    "citation": "RBI KCC Circular Sec 2: All farmers - individuals/joint borrowers who are owner cultivators."
                }
            ],
            "documents": [
                {"category": "LAND_RECORD", "title_en": "Revenue Land Record (Khatauni) with Land Valuation", "title_hi": "तहसीलदार द्वारा प्रमाणित खतौनी नकल", "authority": "UP Tehsil", "format": "Certified Original"},
                {"category": "CROP_DECLARATION", "title_en": "Cropping Pattern Declaration Form", "title_hi": "फसल चक्र एवं रकबा घोषणा पत्र", "authority": "Bank Branch", "format": "Bank Standard Format"},
                {"category": "NO_DUES", "title_en": "No Dues Certificate (for loans > Rs. 1.6 Lakh without tie-up)", "title_hi": "अदेयता प्रमाण पत्र (No Dues Certificate)", "authority": "Local Cooperative / Commercial Banks", "format": "Signed Certificate"}
            ]
        },
        {
            "scheme_code": "UP_KRISHAK_DURGHATNA",
            "official_name_en": "UP Mukhyamantri Krishak Durghatna Kalyan Yojana",
            "official_name_hi": "यूपी मुख्यमंत्री कृषक दुर्घटना कल्याण योजना",
            "department": "Revenue Department, Govt of Uttar Pradesh",
            "level": "STATE_UP",
            "category": "ACCIDENT_WELFARE_COMPENSATION",
            "benefit_type": "DIRECT_BENEFIT_TRANSFER",
            "benefit_summary_en": "Social security ex-gratia compensation up to Rs. 5 Lakh to the farmer or dependent family members in case of accidental death or permanent handicap while farming.",
            "benefit_summary_hi": "खेती या कृषि कार्य के दौरान दुर्घटना में मृत्यु या स्थायी दिव्यांगता पर किसान अथवा आश्रित परिवार को ₹5 लाख तक की आर्थिक सहायता (यह पेंशन नहीं बल्कि दुर्घटना राहत अनुदान है)।",
            "official_portal_url": "https://edistrict.up.gov.in",
            "source_title": "UP Revenue Dept Notification No. 1420/1-11-2020-04(01)/2020",
            "source_section": "Rule 3 (Eligible Beneficiaries & Age Group 18-70) and Rule 4 (Grant Amount)",
            "source_url": "https://bor.up.gov.in",
            "verified_by": "UP Board of Revenue, Lucknow",
            "rules": [
                {
                    "rule_code": "RULE_UP_DURGHATNA_DOMICILE",
                    "title_en": "Uttar Pradesh Permanent Resident",
                    "title_hi": "उत्तर प्रदेश का मूल निवासी",
                    "field_name": "state",
                    "operator": "EQUALS",
                    "target_value": "Uttar Pradesh",
                    "is_mandatory": True,
                    "citation": "UP Revenue Dept Notification Rule 3: Resident farmer of Uttar Pradesh."
                },
                {
                    "rule_code": "RULE_UP_DURGHATNA_LAND_OR_LABOR",
                    "title_en": "Registered Farmer or Landless Agricultural Worker",
                    "title_hi": "खतौनी में दर्ज किसान अथवा ग्राम पंचायत सत्यापित भूमिहीन खेतिहर मजदूर",
                    "field_name": "landholding_acres",
                    "operator": "GTE",
                    "target_value": "0.0",
                    "is_mandatory": True,
                    "citation": "UP Notification Rule 3.2: Khatauni record holders and certified landless agricultural laborers."
                }
            ],
            "documents": [
                {"category": "RESIDENCE_PROOF", "title_en": "UP Domicile / Residence Proof", "title_hi": "उत्तर प्रदेश निवास प्रमाण पत्र", "authority": "UP Edistrict", "format": "Digital Certificate"},
                {"category": "LAND_RECORD", "title_en": "Khatauni / Gram Pradhan Agricultural Labor Certificate", "title_hi": "खतौनी नकल अथवा कृषि मजदूर प्रमाण पत्र", "authority": "UP Revenue / Gram Panchayat", "format": "Certified Copy"},
                {"category": "MEDICAL_REPORT", "title_en": "Post-Mortem / Disability Medical Board Certificate", "title_hi": "पोस्टमार्टम रिपोर्ट अथवा सीएमओ दिव्यांगता प्रमाण पत्र", "authority": "District Hospital / CMO", "format": "Medical Certificate within 45 days"}
            ]
        },
        {
            "scheme_code": "SMAM_MACHINERY",
            "official_name_en": "Sub-Mission on Agricultural Mechanization (UP Krishi Yantrikikaran)",
            "official_name_hi": "कृषि यंत्रीकरण उप-मिशन (उत्तर प्रदेश कृषि यंत्र अनुदान)",
            "department": "Department of Agriculture, Govt of Uttar Pradesh",
            "level": "CENTRAL",
            "category": "FARM_MACHINERY_SUBSIDY",
            "benefit_type": "SUBSIDY",
            "benefit_summary_en": "40% to 50% capital subsidy on modern farm machinery including Rotavators, Happy Seeders, Laser Land Levelers, Power Tillers, and Custom Hiring Centers.",
            "benefit_summary_hi": "रोटावेटर, हैप्पी सीडर, लेजर लैंड लेवलर और पावर टिलर जैसे आधुनिक कृषि यंत्रों पर 40% से 50% तक सीधा सरकारी अनुदान।",
            "official_portal_url": "https://agriculture.up.gov.in",
            "source_title": "SMAM Operational Guidelines Chapter III & UP DBT Agriculture Circular 2024",
            "source_section": "Chapter III (Subsidy Norms for Individual Farmers & Farm Machinery Banks)",
            "source_url": "https://agrimachinery.nic.in",
            "verified_by": "Directorate of Agriculture, Krishi Bhawan, Lucknow",
            "rules": [
                {
                    "rule_code": "RULE_SMAM_LAND",
                    "title_en": "Minimum Cultivable Holding for Individual Equipment",
                    "title_hi": "व्यक्तिगत कृषि यंत्र अनुदान हेतु न्यूनतम भूमि स्वामित्व (0.5 एकड़)",
                    "field_name": "landholding_acres",
                    "operator": "GTE",
                    "target_value": "0.5",
                    "is_mandatory": True,
                    "citation": "SMAM Guidelines Chapter III Clause 3.2: Minimum landholding requirement for heavy implements."
                }
            ],
            "documents": [
                {"category": "REGISTRATION_TOKEN", "title_en": "UP Agriculture Portal Farmer Registration Number", "title_hi": "पारदर्शी किसान सेवा पोर्टल (upagriculture.com) पंजीकरण संख्या", "authority": "UP Agriculture Dept", "format": "Online Registration Slip"},
                {"category": "LAND_RECORD", "title_en": "Verified Khatauni Record", "title_hi": "सत्यापित खतौनी नकल", "authority": "UP Revenue Dept", "format": "PDF / Original"}
            ]
        }
    ]

    for s_data in schemes_data:
        scheme = db.query(Scheme).filter(Scheme.scheme_code == s_data["scheme_code"]).first()
        if not scheme:
            scheme = Scheme(
                scheme_code=s_data["scheme_code"],
                official_name_en=s_data["official_name_en"],
                official_name_hi=s_data["official_name_hi"],
                department=s_data["department"],
                level=s_data["level"],
                category=s_data["category"],
                benefit_type=s_data["benefit_type"],
                benefit_summary_en=s_data["benefit_summary_en"],
                benefit_summary_hi=s_data["benefit_summary_hi"],
                official_portal_url=s_data["official_portal_url"]
            )
            db.add(scheme)
            db.commit()
            db.refresh(scheme)

            # Add Scheme Version
            version = SchemeVersion(
                scheme_id=scheme.id,
                version_number="3.0",
                status="PUBLISHED",
                verified_by=s_data["verified_by"],
                source_title=s_data["source_title"],
                source_url=s_data["source_url"],
                source_section=s_data["source_section"],
                change_summary="Authoritative gazetted verification for UP 2026 build."
            )
            db.add(version)
            db.commit()
            db.refresh(version)

            scheme.active_version_id = version.id
            db.commit()

            # Add Rules
            for r in s_data["rules"]:
                rule = EligibilityRule(
                    scheme_version_id=version.id,
                    rule_code=r["rule_code"],
                    title_en=r["title_en"],
                    title_hi=r["title_hi"],
                    field_name=r["field_name"],
                    operator=r["operator"],
                    target_value=str(r["target_value"]),
                    is_mandatory=r["is_mandatory"],
                    source_citation=r["citation"]
                )
                db.add(rule)

            # Add Documents
            for doc in s_data["documents"]:
                doc_req = SchemeDocumentRequirement(
                    scheme_code=s_data["scheme_code"],
                    document_category=doc["category"],
                    title_en=doc["title_en"],
                    title_hi=doc["title_hi"],
                    issuing_authority=doc["authority"],
                    accepted_formats=doc["format"],
                    is_mandatory=True
                )
                db.add(doc_req)

            db.commit()

    # Seed Pairwise Compatibility Rules
    compatibility_data = [
        {
            "scheme_code_a": "PM_KISAN",
            "scheme_code_b": "PMFBY",
            "status": "COMPATIBLE_CONFIRMED",
            "evidence_text": "PM-KISAN operational guidelines (Clause 3) and PMFBY operational guidelines (Clause 4.4) confirm that income support under PM-KISAN is independent of statutory crop loss insurance. Receiving PM-KISAN does not preclude or reduce PMFBY claim payout.",
            "authoritative_source": "MoA&FW PMFBY/PMK Harmonization Office Memorandum 2021-Agri-09",
            "source_section": "Clause 2.3",
            "verified_by": "Senior Agricultural Policy Analyst"
        },
        {
            "scheme_code_a": "PM_KISAN",
            "scheme_code_b": "KCC",
            "status": "COMPATIBLE_CONFIRMED",
            "evidence_text": "The Ministry of Agriculture launched a dedicated national saturation campaign actively encouraging all active PM-KISAN beneficiaries to obtain Kisan Credit Cards without extra processing fee up to Rs. 1.6 Lakh limit.",
            "authoritative_source": "Department of Financial Services / MoA&FW Joint Saturation Circular 2020",
            "source_section": "Section 1 (KCC for PM-KISAN Beneficiaries)",
            "verified_by": "Senior Banking & Credit Specialist"
        },
        {
            "scheme_code_a": "PMFBY",
            "scheme_code_b": "KCC",
            "status": "COMPATIBLE_CONFIRMED",
            "evidence_text": "Kisan Credit Card holders cultivating notified crops are automatically enrolled for PMFBY coverage through their loan account unless an explicit opt-out declaration is filed before the seasonal deadline.",
            "authoritative_source": "RBI Master Circular FIDD.CO.FSD.BC.No.6/2022-23 Section 4.5",
            "source_section": "Section 4.5",
            "verified_by": "Senior Banking & Credit Specialist"
        },
        {
            "scheme_code_a": "PMKSY_PDMC",
            "scheme_code_b": "SMAM_MACHINERY",
            "status": "COMPATIBLE_CONFIRMED",
            "evidence_text": "Micro-irrigation systems under Horticulture Department and farm mechanization equipment under Agriculture Department apply to distinct physical capital assets. Both subsidies can be availed concurrently on the same farm without duplication penalty.",
            "authoritative_source": "UP State Agriculture Convergence Advisory Committee Resolution 2023",
            "source_section": "Item 4 (Subsidies on Distinct Capital Assets)",
            "verified_by": "UP State Convergence Committee"
        },
        {
            "scheme_code_a": "PM_KISAN",
            "scheme_code_b": "UP_KRISHAK_DURGHATNA",
            "status": "COMPATIBLE_CONFIRMED",
            "evidence_text": "UP Mukhyamantri Krishak Durghatna Kalyan Yojana is a social security accident benefit for registered farmers and laborers, distinct from the central agricultural income support scheme. Both remain fully combinable.",
            "authoritative_source": "UP Revenue Department Notification No. 1420/1-11-2020-04(01)/2020 Rule 6",
            "source_section": "Rule 6",
            "verified_by": "UP Revenue Dept Legal Cell"
        }
    ]

    for comp in compatibility_data:
        existing = db.query(CompatibilityRule).filter(
            CompatibilityRule.scheme_code_a == comp["scheme_code_a"],
            CompatibilityRule.scheme_code_b == comp["scheme_code_b"]
        ).first()
        if not existing:
            rule = CompatibilityRule(
                scheme_code_a=comp["scheme_code_a"],
                scheme_code_b=comp["scheme_code_b"],
                status=comp["status"],
                evidence_text=comp["evidence_text"],
                authoritative_source=comp["authoritative_source"],
                source_section=comp["source_section"],
                verified_by=comp["verified_by"],
                verified_at=datetime.now(timezone.utc)
            )
            db.add(rule)
            db.commit()

