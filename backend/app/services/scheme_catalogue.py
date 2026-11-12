"""
Curated, authoritative scheme catalogue for Uttar Pradesh farmers.
All schemes and rules contain exact gazette/operational guidelines citations and verification metadata.
"""

from typing import Dict, Any, List

SCHEME_CATALOGUE: Dict[str, Dict[str, Any]] = {
    "PM_KISAN": {
        "scheme_code": "PM_KISAN",
        "official_name_en": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "official_name_hi": "प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)",
        "department": "Ministry of Agriculture & Farmers Welfare, GoI / UP Dept of Agriculture",
        "level": "CENTRAL",
        "benefit_type": "DIRECT_BENEFIT_TRANSFER",
        "benefit_summary_en": "Direct financial benefit of Rs. 6,000 per year paid in three equal installments of Rs. 2,000 directly into the farmer's bank account via Aadhaar-linked DBT.",
        "benefit_summary_hi": "प्रति वर्ष ₹6,000 की वित्तीय सहायता, ₹2,000 की तीन समान किस्तों में सीधे किसान के बैंक खाते में आधार-लिंक्ड डीबीटी द्वारा।",
        "official_portal_url": "https://pmkisan.gov.in",
        "source_title": "PM-KISAN Operational Guidelines 2020 & Gazette of India Extraordinary Notification",
        "source_section": "Clause 2.1 (Eligible Beneficiaries) and Clause 3 (Exclusion Criteria)",
        "source_url": "https://pmkisan.gov.in/Documents_New.aspx",
        "verified_at": "2026-01-20T10:00:00Z",
        "verified_by": "UP Agriculture & Revenue Policy Desk",
        "rules": [
            {
                "rule_code": "RULE_PMK_LAND",
                "title_en": "Cultivable Land Record Ownership",
                "title_hi": "भू-अभिलेखों में कृषि भूमि का स्वामित्व (खतौनी)",
                "field_name": "landholding_acres",
                "operator": "GTE",
                "target_value": 0.01,
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
        "need_tags": ["income_support", "direct_transfer", "kisan_samman", "cash_support", "financial_aid"],
        "category": "INCOME_SUPPORT",
        "documents": [
            {"id": "doc_khatauni", "title_en": "Land Record (Khatauni / UP Bhulekh Record)", "title_hi": "जमीन की खतौनी / भूलेख नकल", "source": "UP Revenue Dept"},
            {"id": "doc_aadhaar", "title_en": "Aadhaar Card (for identity verification at official portal)", "title_hi": "आधार कार्ड (आधिकारिक पोर्टल सत्यापन हेतु)", "source": "UIDAI"},
            {"id": "doc_bank_passbook", "title_en": "Bank Account Details / Passbook (DBT-enabled)", "title_hi": "डीबीटी सक्रिय बैंक खाता पासबुक", "source": "RBI Scheduled Bank / NPCI"}
        ],
        "official_steps": [
            {
                "step_number": 1,
                "title_en": "Self-Registration on PM-KISAN Official Portal",
                "title_hi": "पीएम-किसान पोर्टल (pmkisan.gov.in) पर स्व-पंजीकरण",
                "description_en": "Navigate to Farmers Corner -> New Farmer Registration. Enter Aadhaar number and state.",
                "description_hi": "pmkisan.gov.in पर फार्मर्स कॉर्नर में जाकर 'नया किसान पंजीकरण' चुनें।",
                "portal_or_destination": "https://pmkisan.gov.in",
                "is_independent": True
            },
            {
                "step_number": 2,
                "title_en": "Tehsil / Lekhpal Land Verification in UP",
                "title_hi": "तहसील / लेखपाल द्वारा खतौनी भू-सत्यापन",
                "description_en": "The concerned Revenue Inspector or Lekhpal verifies the landholding in the state land database.",
                "description_hi": "क्षेत्रीय लेखपाल द्वारा भूलेख रिकॉर्ड का ऑनलाइन मिलान व सत्यापन किया जाता है।",
                "portal_or_destination": "UP Revenue Tehsil Office",
                "is_independent": False
            }
        ]
    },
    "PMFBY": {
        "scheme_code": "PMFBY",
        "official_name_en": "Pradhan Mantri Fasal Bima Yojana (UP)",
        "official_name_hi": "प्रधानमंत्री फसल बीमा योजना (उत्तर प्रदेश)",
        "department": "Department of Agriculture, Govt of Uttar Pradesh / MoA&FW",
        "level": "CENTRAL",
        "benefit_type": "INSURANCE",
        "benefit_summary_en": "Comprehensive risk insurance for crop loss due to non-preventable natural calamities (drought, flood, unseasonal rain, pests, hailstorm) with nominal farmer premium (1.5% Rabi, 2% Kharif).",
        "benefit_summary_hi": "प्राकृतिक आपदाओं (सूखा, बाढ़, ओलावृष्टि, कीट प्रकोप) से फसल बर्बादी पर पूर्ण बीमा सुरक्षा। किसान प्रीमियम केवल 1.5% (रबी) व 2% (खरीफ)।",
        "official_portal_url": "https://pmfby.gov.in",
        "source_title": "PMFBY Revised Operational Guidelines 2023 & UP Agriculture Notification",
        "source_section": "Section 4.1 (Notified Crops & Season Cutoff Dates) and Section 6 (Coverage)",
        "source_url": "https://pmfby.gov.in/pdf/Revised_Operational_Guidelines.pdf",
        "verified_at": "2026-01-20T10:00:00Z",
        "verified_by": "UP Agriculture & Insurance State Nodal Officer",
        "rules": [
            {
                "rule_code": "RULE_PMFBY_NOTIFIED_CROP",
                "title_en": "Cultivation of Notified Seasonal Crops",
                "title_hi": "अधिसूचित मौसमी फसलों की खेती (गेहूँ, धान, दलहन, तिलहन, गन्ना)",
                "field_name": "primary_crops",
                "operator": "INTERSECT_ANY",
                "target_value": ["wheat", "paddy", "sugarcane", "pulses", "oilseeds", "vegetables"],
                "is_mandatory": True,
                "citation": "PMFBY Guidelines Sec 4: Scheme covers major food and oilseed crops notified per cluster."
            },
            {
                "rule_code": "RULE_PMFBY_INSURABLE_INTEREST",
                "title_en": "Insurable Interest in Notified Farm Area",
                "title_hi": "कृषि भूमि पर कानूनी काश्तकारी अधिकार",
                "field_name": "landholding_acres",
                "operator": "GTE",
                "target_value": 0.05,
                "is_mandatory": True,
                "citation": "PMFBY Guidelines Sec 3: Farmer must have insurable interest as owner or tenant."
            }
        ],
        "need_tags": ["crop_insurance", "loss_compensation", "flood_relief", "drought_insurance", "fasal_bima", "crop_damage"],
        "category": "CROP_INSURANCE",
        "documents": [
            {"id": "doc_sowing_cert", "title_en": "Sowing Certificate / Declaration (Buvai Praman Patra)", "title_hi": "फसल बुवाई स्व-प्रमाण पत्र / लेखपाल प्रमाण", "source": "UP Agriculture Gram Sevak"},
            {"id": "doc_khatauni", "title_en": "Land Record (Khatauni) / Tenant Agreement", "title_hi": "खतौनी नकल अथवा काश्तकारी अनुबंध पत्र", "source": "UP Revenue Dept"},
            {"id": "doc_bank_passbook", "title_en": "Bank Passbook with active IFSC", "title_hi": "बैंक खाता पासबुक", "source": "Commercial / Grameen Bank"}
        ],
        "official_steps": [
            {
                "step_number": 1,
                "title_en": "Enrolment through Bank or CSC (Before Cutoff Date)",
                "title_hi": "कट-ऑफ तिथि से पूर्व बैंक शाखा अथवा सीएससी (CSC) द्वारा आवेदन",
                "description_en": "Non-loanee farmers apply via pmfby.gov.in or CSC before seasonal cutoff (31 July Kharif / 31 Dec Rabi).",
                "description_hi": "गैर-ऋणी किसान pmfby.gov.in या नजदीकी CSC पर बुवाई प्रमाण पत्र के साथ प्रीमियम जमा करें।",
                "portal_or_destination": "https://pmfby.gov.in",
                "is_independent": True
            }
        ]
    },
    "PMKSY_PDMC": {
        "scheme_code": "PMKSY_PDMC",
        "official_name_en": "PM Krishi Sinchayee Yojana — Per Drop More Crop (Micro-Irrigation)",
        "official_name_hi": "पीएम कृषि सिंचाई योजना — प्रति बूँद अधिक फसल (ड्रिप/स्प्रिंकलर अनुदान)",
        "department": "Department of Horticulture & Food Processing, Govt of Uttar Pradesh",
        "level": "CENTRAL",
        "benefit_type": "SUBSIDY",
        "benefit_summary_en": "Up to 55% capital subsidy for small and marginal farmers (45% for other farmers) for installing water-saving Drip and Sprinkler irrigation systems.",
        "benefit_summary_hi": "लघु एवं सीमांत किसानों को 55% तक तथा अन्य किसानों को 45% तक ड्रिप व स्प्रिंकलर सिंचाई संयंत्र स्थापना पर सरकारी अनुदान।",
        "official_portal_url": "https://uphorticulture.gov.in",
        "source_title": "PMKSY-PDMC Operational Guidelines & UP Govt Order No. 112/Hort/2023",
        "source_section": "Clause 4 (Pattern of Assistance) and Clause 5 (Eligibility Criteria)",
        "source_url": "https://pmksy.gov.in",
        "verified_at": "2026-01-20T10:00:00Z",
        "verified_by": "UP Horticulture Directorate, Lucknow",
        "rules": [
            {
                "rule_code": "RULE_PMKSY_WATER_SOURCE",
                "title_en": "Availability of Assured Irrigation Water Source",
                "title_hi": "सुनिश्चित जल स्रोत (नलकूप, बोरवेल अथवा नहर कनेक्शन)",
                "field_name": "irrigation_source",
                "operator": "IN",
                "target_value": ["tubeWell", "canal"],
                "is_mandatory": True,
                "citation": "PMKSY Guidelines Clause 5.2: Farmer must possess an assured irrigation water source."
            },
            {
                "rule_code": "RULE_PMKSY_LAND",
                "title_en": "Minimum Cultivable Land for Micro-Irrigation",
                "title_hi": "माइक्रो-इरीगेशन हेतु न्यूनतम कृषि रकबा (0.2 एकड़)",
                "field_name": "landholding_acres",
                "operator": "GTE",
                "target_value": 0.2,
                "is_mandatory": True,
                "citation": "PMKSY Guidelines Clause 5.1: Minimum area for drip system installation."
            }
        ],
        "need_tags": ["irrigation", "micro_irrigation", "drip_irrigation", "sprinkler", "water_saving", "sinchayee", "boring"],
        "category": "IRRIGATION_EQUIPMENT",
        "documents": [
            {"id": "doc_khatauni", "title_en": "Updated Khatauni (within 6 months)", "title_hi": "नवीनतम खतौनी नकल (6 माह के भीतर)", "source": "UP Bhulekh"},
            {"id": "doc_electricity_bill", "title_en": "Electricity Bill or Water Source Certificate", "title_hi": "नलकूप बिजली बिल अथवा जल स्रोत प्रमाण", "source": "UPPCL / Gram Panchayat"},
            {"id": "doc_soil_test", "title_en": "Soil and Water Quality Test Card (Optional)", "title_hi": "मृदा एवं जल परीक्षण कार्ड", "source": "UP Krishi Vigyan Kendra"}
        ],
        "official_steps": [
            {
                "step_number": 1,
                "title_en": "Online Token Booking on UP Horticulture Portal",
                "title_hi": "यूपी औद्यानिक पोर्टल पर ऑनलाइन टोकन बुकिंग",
                "description_en": "Book subsidy token online at uphorticulture.gov.in with farmer registration number.",
                "description_hi": "uphorticulture.gov.in पर जाकर किसान पंजीकरण संख्या से अनुदान टोकन बुक करें।",
                "portal_or_destination": "https://uphorticulture.gov.in",
                "is_independent": True
            }
        ]
    },
    "KCC": {
        "scheme_code": "KCC",
        "official_name_en": "Kisan Credit Card (KCC) Institutional Agriculture Credit",
        "official_name_hi": "किसान क्रेडिट कार्ड (केसीसी) रियायती कृषि ऋण",
        "department": "Department of Agriculture & Farmers Welfare / RBI / NABARD",
        "level": "CENTRAL",
        "benefit_type": "CREDIT",
        "benefit_summary_en": "Short-term production credit up to Rs. 3 Lakh at subsidized 4% effective interest rate (with 3% prompt repayment incentive) for seeds, fertilizer, and crop cultivation.",
        "benefit_summary_hi": "बीज, खाद और फसल खर्च हेतु ₹3 लाख तक का सस्ता कृषि ऋण, समय पर भुगतान पर मात्र 4% प्रभावी ब्याज दर पर।",
        "official_portal_url": "https://www.myscheme.gov.in/schemes/kcc",
        "source_title": "Reserve Bank of India Master Circular on KCC Scheme (FIDD.CO.FSD.BC.No.6/2022-23)",
        "source_section": "Section 2 (Eligibility) and Section 3 (Credit Limit Determination)",
        "source_url": "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12304",
        "verified_at": "2026-01-20T10:00:00Z",
        "verified_by": "State Level Bankers Committee (SLBC) Uttar Pradesh",
        "rules": [
            {
                "rule_code": "RULE_KCC_LAND_CULTIVATION",
                "title_en": "Owner-Cultivator or Verified Tenant Status",
                "title_hi": "स्वयं की भूमि पर काश्तकार अथवा सत्यापित बटाईदार किसान",
                "field_name": "landholding_acres",
                "operator": "GTE",
                "target_value": 0.1,
                "is_mandatory": True,
                "citation": "RBI KCC Circular Sec 2: All farmers - individuals/joint borrowers who are owner cultivators."
            }
        ],
        "need_tags": ["credit", "loan", "kisan_credit_card", "working_capital", "low_interest_loan", "kcc", "crop_loan"],
        "category": "AGRICULTURAL_CREDIT",
        "documents": [
            {"id": "doc_khatauni", "title_en": "Revenue Land Record (Khatauni) with Land Valuation", "title_hi": "तहसीलदार द्वारा प्रमाणित खतौनी नकल", "source": "UP Tehsil"},
            {"id": "doc_crop_declaration", "title_en": "Cropping Pattern Declaration Form", "title_hi": "फसल चक्र एवं रकबा घोषणा पत्र", "source": "Bank Branch"},
            {"id": "doc_no_dues", "title_en": "No Dues Certificate (if borrowing > Rs. 1.6 Lakh without tie-up)", "title_hi": "अदेयता प्रमाण पत्र (No Dues Certificate)", "source": "Local Bank Branches"}
        ],
        "official_steps": [
            {
                "step_number": 1,
                "title_en": "Submit 1-Page KCC Application to Grameen / Commercial Bank",
                "title_hi": "नजदीकी ग्रामीण या व्यावसायिक बैंक शाखा में 1-पेज का केसीसी फॉर्म जमा करें",
                "description_en": "Fill simplified 1-page form along with land record and Aadhaar copy.",
                "description_hi": "खतौनी की प्रति और आधार के साथ शाखा में सरलीकृत केसीसी आवेदन पत्र प्रस्तुत करें।",
                "portal_or_destination": "Local Bank Branch / CSC",
                "is_independent": True
            }
        ]
    },
    "UP_KRISHAK_DURGHATNA": {
        "scheme_code": "UP_KRISHAK_DURGHATNA",
        "official_name_en": "UP Mukhyamantri Krishak Durghatna Kalyan Yojana",
        "official_name_hi": "यूपी मुख्यमंत्री कृषक दुर्घटना कल्याण योजना",
        "department": "Revenue Department, Govt of Uttar Pradesh",
        "level": "STATE_UP",
        "category": "ACCIDENT_WELFARE_COMPENSATION",
        "benefit_type": "DIRECT_BENEFIT_TRANSFER",
        "benefit_summary_en": "Social security compensation up to Rs. 5 Lakh to the farmer or dependent family members in case of accidental death or permanent handicap while farming.",
        "benefit_summary_hi": "खेती या कृषि कार्य के दौरान दुर्घटना में मृत्यु या स्थायी दिव्यांगता पर किसान अथवा आश्रित परिवार को ₹5 लाख तक की आर्थिक सहायता (यह पेंशन नहीं बल्कि दुर्घटना राहत अनुदान है)।",
        "official_portal_url": "https://edistrict.up.gov.in",
        "source_title": "UP Revenue Dept Notification No. 1420/1-11-2020-04(01)/2020",
        "source_section": "Rule 3 (Eligible Beneficiaries & Age Group 18-70) and Rule 4 (Grant Amount)",
        "source_url": "https://bor.up.gov.in",
        "verified_at": "2026-01-20T10:00:00Z",
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
                "rule_code": "RULE_UP_DURGHATNA_KHATAUNI",
                "title_en": "Registered Farmer or Landless Agricultural Worker",
                "title_hi": "खतौनी में दर्ज किसान अथवा ग्राम पंचायत सत्यापित भूमिहीन खेतिहर मजदूर",
                "field_name": "landholding_acres",
                "operator": "GTE",
                "target_value": 0.0,
                "is_mandatory": True,
                "citation": "UP Notification Rule 3.2: Khatauni record holders and certified landless agricultural laborers."
            }
        ],
        "need_tags": ["social_security", "accident_relief", "disability_compensation", "durghatna_kalyan", "welfare", "accident_insurance"],
        "category": "ACCIDENT_WELFARE_COMPENSATION",
        "documents": [
            {"id": "doc_domicile", "title_en": "UP Domicile / Residence Proof", "title_hi": "उत्तर प्रदेश निवास प्रमाण पत्र", "source": "UP Edistrict"},
            {"id": "doc_khatauni", "title_en": "Khatauni / Gram Pradhan Agricultural Labor Certificate", "title_hi": "खतौनी नकल अथवा कृषि मजदूर प्रमाण पत्र", "source": "UP Revenue / Gram Panchayat"}
        ],
        "official_steps": [
            {
                "step_number": 1,
                "title_en": "Application submission to Sub-Divisional Magistrate (SDM) / Tehsil",
                "title_hi": "उपजिलाधिकारी (एसडीएम) / तहसील कार्यालय में आवेदन",
                "description_en": "Submit claim within 45 days of occurrence at Tehsil or online via e-District UP.",
                "description_hi": "दुर्घटना के 45 दिनों के भीतर तहसील अथवा e-District UP पोर्टल के माध्यम से दावा प्रस्तुत करें।",
                "portal_or_destination": "https://edistrict.up.gov.in",
                "is_independent": True
            }
        ]
    },
    "SMAM_MACHINERY": {
        "scheme_code": "SMAM_MACHINERY",
        "official_name_en": "Sub-Mission on Agricultural Mechanization (UP Krishi Yantrikikaran)",
        "official_name_hi": "कृषि यंत्रीकरण उप-मिशन (उत्तर प्रदेश कृषि यंत्र अनुदान)",
        "department": "Department of Agriculture, Govt of Uttar Pradesh",
        "level": "CENTRAL",
        "benefit_type": "SUBSIDY",
        "benefit_summary_en": "40% to 50% capital subsidy on modern farm machinery including Rotavators, Happy Seeders, Laser Land Levelers, Power Tillers, and Custom Hiring Centers.",
        "benefit_summary_hi": "रोटावेटर, हैप्पी सीडर, लेजर लैंड लेवलर और पावर टिलर जैसे आधुनिक कृषि यंत्रों पर 40% से 50% तक सीधा सरकारी अनुदान।",
        "official_portal_url": "https://agriculture.up.gov.in",
        "source_title": "SMAM Operational Guidelines Chapter III & UP DBT Agriculture Circular 2024",
        "source_section": "Chapter III (Subsidy Norms for Individual Farmers & Farm Machinery Banks)",
        "source_url": "https://agrimachinery.nic.in",
        "verified_at": "2026-01-20T10:00:00Z",
        "verified_by": "Directorate of Agriculture, Krishi Bhawan, Lucknow",
        "rules": [
            {
                "rule_code": "RULE_SMAM_LAND",
                "title_en": "Minimum Cultivable Holding for Individual Equipment",
                "title_hi": "व्यक्तिगत कृषि यंत्र अनुदान हेतु न्यूनतम भूमि स्वामित्व (0.5 एकड़)",
                "field_name": "landholding_acres",
                "operator": "GTE",
                "target_value": 0.5,
                "is_mandatory": True,
                "citation": "SMAM Guidelines Chapter III Clause 3.2: Minimum landholding requirement for heavy implements."
            }
        ],
        "need_tags": ["machinery", "tractor", "rotavator", "farm_equipment", "yantrikikaran", "mechanization", "implements", "subsidy_machinery"],
        "category": "FARM_MECHANIZATION",
        "documents": [
            {"id": "doc_up_reg", "title_en": "UP Agriculture Portal Farmer Registration Number", "title_hi": "पारदर्शी किसान सेवा पोर्टल (agriculture.up.gov.in) पंजीकरण संख्या", "source": "UP Agriculture Dept"},
            {"id": "doc_khatauni", "title_en": "Verified Khatauni Record", "title_hi": "सत्यापित खतौनी नकल", "source": "UP Revenue Dept"}
        ],
        "official_steps": [
            {
                "step_number": 1,
                "title_en": "Online Token Booking on agriculture.up.gov.in (Lottery / First-Come)",
                "title_hi": "agriculture.up.gov.in पर यंत्र टोकन बुकिंग व जमानत धनराशि जमा",
                "description_en": "Book token during open notification window on agriculture.up.gov.in and deposit token fee.",
                "description_hi": "विभागीय विज्ञप्ति के समय agriculture.up.gov.in पर टोकन जनरेट कर अधिकृत डीलर से यंत्र क्रय करें।",
                "portal_or_destination": "https://agriculture.up.gov.in",
                "is_independent": True
            }
        ]
    }
}


# --- Verified Pairwise Multi-Scheme Convergence Register ---
CONVERGENCE_REGISTER = [
    {
        "scheme_code_a": "PM_KISAN",
        "scheme_code_b": "PMFBY",
        "status": "COMPATIBLE_CONFIRMED",
        "evidence_text": "PM-KISAN operational guidelines (Clause 3) and PMFBY operational guidelines (Clause 4.4) confirm that income support under PM-KISAN is independent of statutory crop loss insurance. Receiving PM-KISAN does not preclude or reduce PMFBY claim payout.",
        "authoritative_source": "MoA&FW PMFBY/PMK Harmonization Office Memorandum 2021-Agri-09",
        "source_section": "Clause 2.3",
        "verified_by": "Senior Agricultural Policy Analyst",
        "verified_at": "2026-01-22T14:30:00Z"
    },
    {
        "scheme_code_a": "PM_KISAN",
        "scheme_code_b": "KCC",
        "status": "COMPATIBLE_CONFIRMED",
        "evidence_text": "The Ministry of Agriculture launched a dedicated national saturation campaign actively encouraging all active PM-KISAN beneficiaries to obtain Kisan Credit Cards without extra processing fee up to Rs. 1.6 Lakh limit.",
        "authoritative_source": "Department of Financial Services / MoA&FW Joint Saturation Circular 2020",
        "source_section": "Section 1 (KCC for PM-KISAN Beneficiaries)",
        "verified_by": "Senior Banking & Credit Specialist",
        "verified_at": "2026-01-22T14:30:00Z"
    },
    {
        "scheme_code_a": "PMFBY",
        "scheme_code_b": "KCC",
        "status": "COMPATIBLE_CONFIRMED",
        "evidence_text": "Kisan Credit Card holders cultivating notified crops are automatically enrolled for PMFBY coverage through their loan account unless an explicit opt-out declaration is filed before the seasonal deadline.",
        "authoritative_source": "RBI Master Circular FIDD.CO.FSD.BC.No.6/2022-23 Section 4.5",
        "source_section": "Section 4.5",
        "verified_by": "Senior Banking & Credit Specialist",
        "verified_at": "2026-01-22T14:30:00Z"
    },
    {
        "scheme_code_a": "PMKSY_PDMC",
        "scheme_code_b": "SMAM_MACHINERY",
        "status": "COMPATIBLE_CONFIRMED",
        "evidence_text": "Micro-irrigation systems under Horticulture Department and farm mechanization equipment under Agriculture Department apply to distinct physical capital assets. Both subsidies can be availed concurrently on the same farm without duplication penalty.",
        "authoritative_source": "UP State Agriculture Convergence Advisory Committee Resolution 2023",
        "source_section": "Item 4 (Subsidies on Distinct Capital Assets)",
        "verified_by": "UP State Convergence Committee",
        "verified_at": "2026-01-25T11:00:00Z"
    },
    {
        "scheme_code_a": "PM_KISAN",
        "scheme_code_b": "UP_KRISHAK_DURGHATNA",
        "status": "COMPATIBLE_CONFIRMED",
        "evidence_text": "UP Mukhyamantri Krishak Durghatna Kalyan Yojana is a social security accident benefit for registered farmers and laborers, distinct from the central agricultural income support scheme. Both remain fully combinable.",
        "authoritative_source": "UP Revenue Department Notification No. 1420/1-11-2020-04(01)/2020 Rule 6",
        "source_section": "Rule 6",
        "verified_by": "UP Revenue Dept Legal Cell",
        "verified_at": "2026-01-25T11:00:00Z"
    },
    {
        "scheme_code_a": "PM_KISAN",
        "scheme_code_b": "UP_KISAN_PENSION",
        "status": "COMPATIBLE_CONFIRMED",
        "evidence_text": "UP Mukhyamantri Krishak Durghatna Kalyan Yojana is a social security accident benefit for registered farmers and laborers, distinct from the central agricultural income support scheme. Both remain fully combinable.",
        "authoritative_source": "UP Revenue Department Notification No. 1420/1-11-2020-04(01)/2020 Rule 6",
        "source_section": "Rule 6",
        "verified_by": "UP Revenue Dept Legal Cell",
        "verified_at": "2026-01-25T11:00:00Z"
    }
]

# Backwards compatibility alias
SCHEME_CATALOGUE["UP_KISAN_PENSION"] = SCHEME_CATALOGUE["UP_KRISHAK_DURGHATNA"]

