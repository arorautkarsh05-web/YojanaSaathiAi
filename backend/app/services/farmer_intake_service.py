"""
YojanaSaathi AI — Multilingual Natural Language Farmer Intake & Ambiguity Resolution Service.
Transforms free-form conversational queries (Hindi, English, Hinglish, Punjabi) into structured farmer profiles.
Flag localized land measurement ambiguities (Pucca vs. Kachha Bigha) and identifies missing details
before passing structured parameters to the deterministic rules engine.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from app.services.qa_service import detect_or_normalize_language
from app.services.geo_applicability import UP_75_DISTRICTS, normalize_district_name
from app.schemas import (
    ConversationalIntakeRequest,
    ConversationalIntakeResponse,
    ExtractedProfileParameters,
    UnitAmbiguityNotice,
    FarmerProfileCreate
)

# Hindi number words mapping
HINDI_NUMBERS = {
    "आधा": 0.5, "पौना": 0.75, "सवा": 1.25, "डेढ़": 1.5, "ढाई": 2.5,
    "एक": 1.0, "दो": 2.0, "तीन": 3.0, "चार": 4.0, "पांच": 5.0,
    "पाँच": 5.0, "छह": 6.0, "सात": 7.0, "आठ": 8.0, "नौ": 9.0, "दस": 10.0,
    "ग्यारह": 11.0, "बारह": 12.0, "पंद्रह": 15.0, "बीस": 20.0
}

# Crop mapping: Hindi/Hinglish/English keywords to canonical crop names
CROP_KEYWORDS = {
    "गेहूं": "wheat", "गेहू": "wheat", "wheat": "wheat", "gehu": "wheat",
    "धान": "paddy", "चावल": "paddy", "paddy": "paddy", "rice": "paddy", "chawal": "paddy", "dhan": "paddy",
    "गन्ना": "sugarcane", "sugarcane": "sugarcane", "ganna": "sugarcane",
    "सरसों": "mustard", "mustard": "mustard", "sarson": "mustard", "राई": "mustard", "लाही": "mustard",
    "आलू": "potato", "potato": "potato", "aaloo": "potato", "alu": "potato",
    "चना": "pulses", "gram": "pulses", "अरहर": "pulses", "दाल": "pulses", "masoor": "pulses", "मसूर": "pulses",
    "सब्जियां": "vegetables", "सब्जी": "vegetables", "vegetables": "vegetables", "sabji": "vegetables", "sabzi": "vegetables"
}

# District phonetic and Devanagari mappings for UP
UP_DISTRICT_SYNONYMS = {
    "वाराणसी": "Varanasi", "बनारस": "Varanasi", "काशी": "Varanasi", "varanasi": "Varanasi", "banaras": "Varanasi",
    "प्रयागराज": "Prayagraj", "इलाहाबाद": "Prayagraj", "prayagraj": "Prayagraj", "allahabad": "Prayagraj",
    "लखनऊ": "Lucknow", "lucknow": "Lucknow",
    "झांसी": "Jhansi", "झाँसी": "Jhansi", "jhansi": "Jhansi",
    "बांदा": "Banda", "बाँदा": "Banda", "banda": "Banda",
    "गोरखपुर": "Gorakhpur", "gorakhpur": "Gorakhpur",
    "बाराबंकी": "Barabanki", "barabanki": "Barabanki",
    "मेरठ": "Meerut", "meerut": "Meerut",
    "आगरा": "Agra", "agra": "Agra",
    "अलीगढ़": "Aligarh", "aligarh": "Aligarh",
    "हमीरपुर": "Hamirpur", "hamirpur": "Hamirpur",
    "ललितपुर": "Lalitpur", "lalitpur": "Lalitpur",
    "महोबा": "Mahoba", "mahoba": "Mahoba",
    "जालौन": "Jalaun", "jalaun": "Jalaun", "उरई": "Jalaun",
    "चित्रकूट": "Chitrakoot", "chitrakoot": "Chitrakoot",
    "अयोध्या": "Ayodhya", "फैजाबाद": "Ayodhya", "ayodhya": "Ayodhya", "faizabad": "Ayodhya",
    "बरेली": "Bareilly", "bareilly": "Bareilly",
    "मुरादाबाद": "Moradabad", "moradabad": "Moradabad",
    "कानपुर": "Kanpur Nagar", "kanpur": "Kanpur Nagar",
    "सुलतानपुर": "Sultanpur", "सुल्तानपुर": "Sultanpur", "sultanpur": "Sultanpur",
    "बस्ती": "Basti", "basti": "Basti",
    "गोंडा": "Gonda", "gonda": "Gonda",
    "आजमगढ़": "Azamgarh", "azamgarh": "Azamgarh",
    "मिर्जापुर": "Mirzapur", "मीरजापुर": "Mirzapur", "mirzapur": "Mirzapur",
    "सोनभद्र": "Sonbhadra", "sonbhadra": "Sonbhadra",
    "मुजफ्फरनगर": "Muzaffarnagar", "muzaffarnagar": "Muzaffarnagar",
    "सहारनपुर": "Saharanpur", "saharanpur": "Saharanpur",
    "बुलंदशहर": "Bulandshahr", "bulandshahr": "Bulandshahr",
    "मथुरा": "Mathura", "mathura": "Mathura",
    "बिजनौर": "Bijnor", "bijnor": "Bijnor"
}

def parse_conversational_intake(req: ConversationalIntakeRequest) -> ConversationalIntakeResponse:
    """
    Parses conversational farmer text and produces structured profile entities,
    detects bigha unit ambiguities, and identifies missing requirements.
    """
    text = req.text.strip()
    lang = detect_or_normalize_language(text, req.preferred_language)
    lower_text = text.lower()

    # 1. Intent Detection
    intent = "general_benefit_exploration"
    stated_needs = []

    if any(k in lower_text or k in text for k in ["सिंचाई", "ड्रिप", "स्प्रिंकलर", "पानी", "sinchai", "drip", "sprinkler", "irrigation"]):
        intent = "irrigation_subsidy"
        stated_needs.append("irrigation")

    if any(k in lower_text or k in text for k in ["बीमा", "नुकसान", "ओला", "सूखा", "बारिश", "bima", "nuksan", "fasal kharab", "insurance"]):
        intent = "crop_insurance"
        stated_needs.append("crop_insurance")

    if any(k in lower_text or k in text for k in ["लोन", "कर्ज", "केसीसी", "kcc", "credit", "loan", "rin", "ऋण"]):
        intent = "institutional_credit"
        stated_needs.append("credit")

    if any(k in lower_text or k in text for k in ["किस्त", "सम्मान निधि", "6000", "paisa", "pmkisan", "pm-kisan", "रुपये"]):
        intent = "income_support"
        stated_needs.append("income_support")

    if any(k in lower_text or k in text for k in ["ट्रैक्टर", "यंत्र", "रोटावेटर", "मशीन", "सब्सिडी", "machinery", "equipment"]):
        intent = "farm_mechanization"
        stated_needs.append("machinery")

    if any(k in lower_text or k in text for k in ["दुर्घटना", "मुआवजा", "दिव्यांग", "durghatna", "accident", "trauma"]):
        intent = "accident_relief"
        stated_needs.append("social_security")

    if not stated_needs:
        stated_needs = ["income_support", "crop_insurance"]

    # 2. Extract Crops
    detected_crops = []
    for kw, canonical in CROP_KEYWORDS.items():
        if kw in lower_text or kw in text:
            if canonical not in detected_crops:
                detected_crops.append(canonical)

    # 3. Extract District
    detected_district = None
    # Check exact UP 75 district names
    for dist in UP_75_DISTRICTS:
        if dist.lower() in lower_text:
            detected_district = dist
            break
    # Check Hindi/synonym dictionary
    if not detected_district:
        for syn, canon in UP_DISTRICT_SYNONYMS.items():
            if syn in text or syn in lower_text:
                detected_district = canon
                break

    # Context override if district provided in context
    if not detected_district and req.context.get("district"):
        detected_district = normalize_district_name(req.context.get("district"))

    # 4. Extract Landholding and Unit Ambiguity
    landholding_acres = None
    landholding_raw = None
    land_unit = None
    ambiguities = []

    # Regex patterns for landholding
    # Pattern: number + unit
    match = re.search(r'(\d+(?:\.\d+)?)\s*(बीघा|bigha|एकड़|acre|हेक्टेयर|hectare|कट्ठा|katha)', text, re.IGNORECASE)
    hindi_word_match = None
    if not match:
        for word, val in HINDI_NUMBERS.items():
            if word in text:
                unit_search = re.search(f"{word}\\s*(बीघा|bigha|एकड़|acre|हेक्टेयर|hectare)", text, re.IGNORECASE)
                if unit_search:
                    match = (val, unit_search.group(1))
                    hindi_word_match = True
                    break

    if match:
        if hindi_word_match:
            num = float(match[0])
            unit_str = match[1].lower()
            landholding_raw = f"{num} {unit_str}"
        else:
            num = float(match.group(1))
            unit_str = match.group(2).lower()
            landholding_raw = match.group(0)

        if "बीघा" in unit_str or "bigha" in unit_str:
            land_unit = "bigha"
            # Rule: Never assume a universal conversion for bigha.
            # Flag ambiguity: Pucca Bigha (~0.625 acre) vs Kachha Bigha (~0.208-0.33 acre)
            ambiguities.append(UnitAmbiguityNotice(
                field="landholding_acres",
                issue="LOCAL_UNIT_VARIATION",
                clarification_prompt_hi=(
                    f"आपने '{landholding_raw}' दर्ज किया है। उत्तर प्रदेश में 'बीघा' का माप जिले के अनुसार बदलता है:\n"
                    "• पक्का बीघा (पश्चिमी एवं मध्य उप्र): ~0.625 एकड़ (27,225 वर्ग फीट / ~0.253 हेक्टेयर)\n"
                    "• कच्चा बीघा (पूर्वी उप्र / रुहेलखंड): ~0.208 से 0.33 एकड़\n"
                    "कृपया पुष्टि करें: क्या आपकी जमीन पक्का बीघा है या कच्चा बीघा? (अथवा एकड़ में बताएं)"
                ),
                clarification_prompt_en=(
                    f"You mentioned '{landholding_raw}'. In Uttar Pradesh, 1 Bigha varies regionally:\n"
                    "• Pucca Bigha (Western/Central UP): ~0.625 Acres (27,225 sq.ft)\n"
                    "• Kachha Bigha (Eastern UP/Rohilkhand): ~0.208 to 0.33 Acres\n"
                    "Please confirm whether your land is Pucca Bigha or Kachha Bigha, or specify in Acres."
                )
            ))
            # Conservative conversion to Pucca bigha as provisional estimate
            landholding_acres = round(num * 0.625, 3)

        elif "एकड़" in unit_str or "acre" in unit_str:
            land_unit = "acre"
            landholding_acres = round(num, 3)

        elif "हेक्टेयर" in unit_str or "hectare" in unit_str:
            land_unit = "hectare"
            landholding_acres = round(num * 2.471, 3)

    # 5. Extract Irrigation Source
    irrigation_source = "UNKNOWN"
    if any(k in lower_text or k in text for k in ["नलकूप", "बोरवेल", "ट्यूबवेल", "tubewell", "borewell"]):
        irrigation_source = "TUBEWELL"
    elif any(k in lower_text or k in text for k in ["नहर", "रजबहा", "canal"]):
        irrigation_source = "CANAL"
    elif any(k in lower_text or k in text for k in ["बारिश", "बरसात", "सूखा", "rainfed"]):
        irrigation_source = "RAINFED"

    # 6. Missing Information Identification
    missing_info = []
    follow_up_hi = []
    follow_up_en = []

    if not detected_district:
        missing_info.append("district")
        follow_up_hi.append("आप उत्तर प्रदेश के किस जिले से हैं? (जैसे: वाराणसी, झांसी, बाराबंकी)")
        follow_up_en.append("Which district of Uttar Pradesh do you farm in? (e.g. Varanasi, Jhansi, Barabanki)")

    if landholding_acres is None:
        missing_info.append("landholding")
        follow_up_hi.append("आपके पास कुल कितनी खेती योग्य जमीन है? (जैसे: 2 एकड़, 3 बीघा या 1 हेक्टेयर)")
        follow_up_en.append("What is your total cultivable land area? (e.g. 2 Acres, 3 Bigha, or 1 Hectare)")
    elif ambiguities:
        # Prompt for bigha clarification
        follow_up_hi.append(ambiguities[0].clarification_prompt_hi)
        follow_up_en.append(ambiguities[0].clarification_prompt_en)

    if not detected_crops:
        missing_info.append("primary_crops")
        follow_up_hi.append("आप कौन सी मुख्य फसलें उगाते हैं? (जैसे: गेहूं, धान, गन्ना, सरसों)")
        follow_up_en.append("What primary crops do you cultivate? (e.g. Wheat, Paddy, Sugarcane, Mustard)")

    # 7. Check if ready to evaluate
    can_proceed = (detected_district is not None) and (landholding_acres is not None)

    # Structured Profile Candidate
    structured_candidate = None
    if detected_district and landholding_acres:
        # Categorize farmer by landholding
        category = "MARGINAL" if landholding_acres <= 2.471 else ("SMALL" if landholding_acres <= 4.942 else "MEDIUM_LARGE")
        structured_candidate = FarmerProfileCreate(
            district=detected_district,
            landholding_acres=landholding_acres,
            farmer_category=category,
            primary_crops=detected_crops if detected_crops else ["wheat"],
            social_category="GENERAL",
            irrigation_source=irrigation_source,
            is_temporary=True
        )

    # 8. Summary Message
    if lang == "hi":
        crops_str = ", ".join(detected_crops) if detected_crops else "अनिर्धारित"
        dist_str = detected_district if detected_district else "अनिर्धारित (कृपया बताएं)"
        land_str = f"{landholding_acres} एकड़ (अनुमानित)" if landholding_acres else "अनिर्धारित"
        summary = (
            f"आपकी जानकारी दर्ज की गई:\n"
            f"• जिला: {dist_str}\n"
            f"• रकबा: {land_str}\n"
            f"• फसलें: {crops_str}\n"
            f"• मुख्य आवश्यकता: {intent}\n"
        )
        if ambiguities:
            summary += "\n⚠️ बीघा इकाई की पुष्टि आवश्यक है।"
    else:
        crops_str = ", ".join(detected_crops) if detected_crops else "Unspecified"
        dist_str = detected_district if detected_district else "Unspecified (please provide)"
        land_str = f"{landholding_acres} Acres (estimated)" if landholding_acres else "Unspecified"
        summary = (
            f"Extracted farm parameters:\n"
            f"• District: {dist_str}\n"
            f"• Landholding: {land_str}\n"
            f"• Crops: {crops_str}\n"
            f"• Primary Need: {intent}\n"
        )
        if ambiguities:
            summary += "\n⚠️ Regional Bigha unit clarification required."

    return ConversationalIntakeResponse(
        detected_language=lang,
        intent=intent,
        extracted_parameters=ExtractedProfileParameters(
            district=detected_district,
            landholding_acres=landholding_acres,
            landholding_raw=landholding_raw,
            land_unit=land_unit,
            crops=detected_crops,
            stated_needs=stated_needs,
            irrigation_source=irrigation_source,
            social_category=None
        ),
        ambiguities=ambiguities,
        missing_information=missing_info,
        follow_up_questions_hi=follow_up_hi,
        follow_up_questions_en=follow_up_en,
        can_proceed_to_evaluation=can_proceed,
        structured_profile_candidate=structured_candidate,
        summary_message=summary
    )

