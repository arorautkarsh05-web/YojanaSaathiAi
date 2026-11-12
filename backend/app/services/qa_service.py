"""
Grounded Multilingual Scheme Q&A Service for YojanaSaathi AI.
Provides source-anchored answers strictly based on published official scheme gazettes.
Supports 4 communication modes:
  - Hindi (हिन्दी - Devanagari)
  - English (English)
  - Hinglish (Conversational Romanized Hindi/English)
  - Punjabi (ਪੰਜਾਬੀ - Gurmukhi)

Never fabricates facts, deadlines, amounts, or phone numbers. If evidence is missing, reports cannot_verify.
"""

import re
from typing import Optional, Dict, Any, Tuple, List
from app.services.scheme_catalogue import SCHEME_CATALOGUE
from app.schemas import AssistantQueryResponse

def detect_or_normalize_language(query: str, requested_lang: Optional[str] = None) -> str:
    """
    Normalizes requested language or infers language from query script and vocabulary.
    Returns one of: 'hi', 'en', 'hinglish', 'pa'.
    """
    if requested_lang:
        code = requested_lang.strip().lower()
        if code in ("hi", "hindi", "devanagari"):
            return "hi"
        if code in ("en", "english"):
            return "en"
        if code in ("hinglish", "hi-en", "roman"):
            return "hinglish"
        if code in ("pa", "punjabi", "gurmukhi"):
            return "pa"

    # Auto-detection from script characters
    # Gurmukhi unicode range: \u0A00-\u0A7F
    if re.search(r'[\u0A00-\u0A7F]', query):
        return "pa"
    
    # Devanagari unicode range: \u0900-\u097F
    if re.search(r'[\u0900-\u097F]', query):
        return "hi"

    # Hinglish detection via common Romanized Hindi keywords
    hinglish_markers = [
        "kya", "kaise", "kitna", "milega", "chahiye", "kisan", "kist", "paisa", "paise",
        "fasal", "kharab", "bima", "nuksan", "karwana", "kare", "hoga", "sarkari",
        "kagaz", "dastavez", "yojana", "bhai", "sabse", "kab", "aayega", "drip", "subsidy",
        "durghatna", "maut", "jamin", "khatauni", "bataidar"
    ]
    query_lower = query.lower()
    words = set(re.findall(r'[a-z]+', query_lower))
    matches = words.intersection(hinglish_markers)
    if len(matches) >= 1:
        return "hinglish"

    # Default to English if Latin characters without Hinglish markers
    return "en"


def _identify_scheme(q: str, scheme_code: Optional[str] = None) -> Optional[str]:
    """Identifies target scheme code from explicit param or multilingual keywords."""
    if scheme_code and scheme_code in SCHEME_CATALOGUE:
        return scheme_code

    # PM-KISAN
    if any(k in q for k in [
        "pm-kisan", "pmkisan", "pm kisan", "samman nidhi", "6000", "६०००", "६,०००",
        "सम्मान निधि", "किस्त", "ਕਿਸਾਨ ਸਨਮਾਨ", "ਪੀਐਮ ਕਿਸਾਨ", "ਪੀ.ਐਮ-ਕਿਸਾਨ", "kist",
        "पीएम किसान", "पीएम-किसान", "किसान सम्मान निधि", "किसान सम्मान"
    ]):
        return "PM_KISAN"

    # PMFBY Crop Insurance
    if any(k in q for k in [
        "pmfby", "fasal bima", "crop insurance", "bima", "फसल बीमा", "फसल नुकसान", "सूखा", "ओला",
        "ओलावृष्टि", "ਬੀਮਾ", "ਫ਼ਸਲ ਬੀਮਾ", "ਨੁਕਸਾਨ", "loss intimation", "72 ghante", "72 hours", "७२ घंटे",
        "fasal kharab", "fasal nuksan", "crop damage", "beema"
    ]):
        return "PMFBY"

    # PMKSY_PDMC Micro Irrigation
    if any(k in q for k in [
        "drip", "sprinkler", "irrigation", "pdmc", "pmksy", "सिंचाई", "ड्रिप", "स्प्रिंकलर",
        "फव्वारा", "सूक्ष्म सिंचाई", "ਡ੍ਰਿਪ", "ਸਪ੍ਰਿੰਕਲਰ", "ਸਿੰਚਾਈ", "fuhara"
    ]):
        return "PMKSY_PDMC"

    # KCC Kisan Credit Card
    if any(k in q for k in [
        "kcc", "kisan credit card", "credit card", "loan", "लोन", "कर्ज", "क्रेडिट कार्ड", "ब्याज दर",
        "4%", "४%", "ਕ੍ਰੈਡਿਟ ਕਾਰਡ", "ਕਰਜ਼ਾ", "ਵਿਆਜ"
    ]):
        return "KCC"

    # UP Krishak Durghatna
    if any(k in q for k in [
        "durghatna", "accident", "durghatna kalyan", "दुर्घटना", "दुर्घटना कल्याण", "मुआवजा",
        "५ लाख", "5 lakh", "divyang", "apang", "death relief", "ਦੁਰਘਟਨਾ", "ਹਾਦਸਾ", "ਮੁਆਵਜ਼ਾ"
    ]):
        return "UP_KRISHAK_DURGHATNA"

    # SMAM Machinery
    if any(k in q for k in [
        "machinery", "tractor", "smam", "yantra", "rotavator", "thresher", "ट्रैक्टर", "यंत्र",
        "रोटावेटर", "थ्रेशर", "उपकरण", "ਟ੍ਰੈਕਟਰ", "ਖੇਤੀ ਸੰਦ", "ਰੋਟਾਵੇਟਰ", "token booking", "टोकन बुकिंग"
    ]):
        return "SMAM_MACHINERY"

    return None


def _identify_topic(q: str) -> str:
    """Categorizes the nature of the user's inquiry."""
    # Amount / Subsidy / Money / Compensation / Relief / Pension
    if any(k in q for k in [
        "how much", "amount", "subsidy", "kitna", "paise", "paisa", "rupaye", "अनुदान", "राशि", "लाभ",
        "पैसा", "किस्त", "ਛੋਟ", "ਕਿੰਨੇ ਪੈਸੇ", "ਰਕਮ", "ਸਬਸਿਡੀ", "percentage", "%", "limit",
        "pension", "पेंशन", "relief", "compensation", "muavza", "मुआवजा", "सहायता", "one-time", "एकमुश्त"
    ]):
        return "BENEFIT_AMOUNT"

    # Documents Required
    if any(k in q for k in [
        "document", "documents", "paper", "papers", "kya chahiye", "dastavez", "kagaz", "दस्तावेज़",
        "कागज़", "प्रमाण", "ਕਿਹੜੇ ਕਾਗਜ਼", "ਦਸਤਾਵੇਜ਼", "khatauni", "aadhaar", "passbook"
    ]):
        return "DOCUMENTS_REQUIRED"

    # Application / Portal / Where to apply
    if any(k in q for k in [
        "portal", "website", "where to apply", "how to apply", "kahan apply", "kaise apply",
        "आवेदन कहाँ", "आवेदन कैसे", "पोर्टल", "वेबसाइट", "ਕਿੱਥੇ ਅਰਜ਼ੀ", "ਕਿਵੇਂ ਅਪਲਾਈ", "लिंक", "registration"
    ]):
        return "APPLICATION_PORTAL"

    # Deadlines / Timelines / When will it come
    if any(k in q for k in [
        "deadline", "timeline", "cutoff", "when", "kab aayega", "kab milega", "samay", "समय सीमा",
        "अंतिम तिथि", "72", "45", "दिन", "ਕਦੋਂ", "ਆਖਰੀ ਤਾਰੀਖ਼", "kitne din", "kitne samay",
        "last date", "intimate", "intimation"
    ]):
        return "TIMELINES"

    # Eligibility & Exclusions
    if any(k in q for k in [
        "eligible", "eligibility", "patrata", "who can", "kaun le sakta", "yogyata", "पात्रता", "नियम",
        "किसे मिलेगा", "शर्तें", "ਯੋਗਤਾ", "ਸ਼ਰਤਾਂ", "ਕੌਣ ਲੈ ਸਕਦਾ", "exclusion", "taxpayer"
    ]):
        return "ELIGIBILITY"

    # eKYC, Land Seeding & Common issues
    if any(k in q for k in [
        "ekyc", "e-kyc", "land seeding", "dbt", "npci", "khatauni feed", "status", "rejection",
        "पैसा रुका", "नहीं आया", "समस्या", "रुक गया", "ਸਮੱਸਿਆ", "ਸਟੇਟਸ"
    ]):
        return "ISSUES_AND_STATUS"

    # Grievance / Helpline / Phone
    if any(k in q for k in [
        "helpline", "toll free", "complaint", "shikayat", "number", "फोन नंबर", "हेल्पलाइन", "शिकायत", "ਟੋਲ ਫ੍ਰੀ"
    ]):
        return "HELPLINE"

    # Convergence / Combining
    if any(k in q for k in [
        "dono", "saath me", "combine", "together", "dono le sakte", "ek saath", "साथ में", "दोनों", "इकੱਠੇ"
    ]):
        return "CONVERGENCE"

    return "GENERAL_OVERVIEW"


# --- Grounded Knowledge Base by Scheme & Topic ---

KNOWLEDGE_BASE: Dict[str, Dict[str, Dict[str, str]]] = {
    "PM_KISAN": {
        "BENEFIT_AMOUNT": {
            "hi": "प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान) के तहत पात्र किसान परिवारों को प्रति वर्ष ₹6,000 की वित्तीय सहायता मिलती है। यह राशि ₹2,000 की तीन समान किस्तों में हर चार महीने पर सीधे आधार-सीडेड बैंक खाते में (DBT द्वारा) भेजी जाती है।",
            "en": "Under Pradhan Mantri Kisan Samman Nidhi (PM-KISAN), eligible farmer families receive Rs. 6,000 per year paid in three equal four-monthly installments of Rs. 2,000 directly into Aadhaar-seeded bank accounts via DBT.",
            "hinglish": "PM-KISAN yojana ke tahat eligible kisan families ko saal me total ₹6,000 milte hain. Yeh paisa ₹2,000 ki 3 installments me har 4 mahine par direct aapke Aadhaar-linked bank account me transfer hota hai.",
            "pa": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕਿਸਾਨ ਸਨਮਾਨ ਨਿਧੀ (ਪੀ.ਐਮ-ਕਿਸਾਨ) ਤਹਿਤ ਯੋਗ ਕਿਸਾਨ ਪਰਿਵਾਰਾਂ ਨੂੰ ਹਰ ਸਾਲ ₹6,000 ਦੀ ਮਾਲੀ ਸਹਾਇਤਾ ਮਿਲਦੀ ਹੈ। ਇਹ ਰਕਮ ₹2,000 ਦੀਆਂ ਤਿੰਨ ਬਰਾਬਰ ਕਿਸ਼ਤਾਂ ਵਿੱਚ ਸਿੱਧੀ ਆਧਾਰ-ਲਿੰਕਡ ਬੈਂਕ ਖਾਤੇ ਵਿੱਚ ਡੀਬੀਟੀ ਰਾਹੀਂ ਆਉਂਦੀ ਹੈ।"
        },
        "ELIGIBILITY": {
            "hi": "पात्रता नियम:\n1. राज्य भूलेख (खतौनी) में नाम दर्ज कृषि भूमि होनी चाहिए।\n2. बहिष्करण (Exclusions): कोई भी परिवार सदस्य आयकर दाता (Income Tax Payer) नहीं होना चाहिए; सेवारत या सेवानिवृत्त सरकारी कर्मचारी, संवैधानिक पदधारक, ₹10,000 से अधिक मासिक पेंशनभोगी, एवं डॉक्टर/वकील/सीए/इंजीनियर इस योजना से बाहर हैं।",
            "en": "Eligibility & Exclusions:\n1. Must hold cultivable land registered in state land records (Khatauni).\n2. Exclusions: Institutional landholders, any family member who is an income tax payer, serving/retired government employees, pensioners with >= Rs. 10,000/month, and practicing doctors, lawyers, CAs, and engineers are strictly excluded.",
            "hinglish": "Eligibility rules:\n1. UP Bhulekh (Khatauni) me aapke naam par kheti ki jameen honi chahiye.\n2. Exclusions: Agar family me koi Income Tax bharta hai, government job me hai ya retired hai, ₹10,000 se zyada pension leta hai, ya Doctor/Lawyer/CA hai, to wo is yojana ke liye eligible nahi hain.",
            "pa": "ਯੋਗਤਾ ਦੇ ਨਿਯਮ:\n1. ਸੂਬੇ ਦੇ ਭੂਮੀ ਰਿਕਾਰਡ (ਖਤੌਨੀ) ਵਿੱਚ ਖੇਤੀਬਾੜੀ ਵਾਲੀ ਜ਼ਮੀਨ ਨਾਮ ਦਰਜ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ।\n2. ਬਾਹਰ ਰੱਖੇ ਗਏ: ਕੋਈ ਵੀ ਪਰਿਵਾਰਕ ਮੈਂਬਰ ਇਨਕਮ ਟੈਕਸ ਦਾਤਾ ਨਾ ਹੋਵੇ; ਸਰਕਾਰੀ ਮੁਲਾਜ਼ਮ/ਪੈਨਸ਼ਨਰ (₹10,000 ਤੋਂ ਵੱਧ ਪੈਨਸ਼ਨ), ਅਤੇ ਡਾਕਟਰ, ਵਕੀਲ, ਸੀ.ਏ. ਇਸ ਯੋਜਨਾ ਵਿੱਚ ਸ਼ਾਮਲ ਨਹੀਂ ਹੋ ਸਕਦੇ।"
        },
        "DOCUMENTS_REQUIRED": {
            "hi": "अनिवार्य दस्तावेज़:\n• खतौनी नकल (UP भूलेख से सत्यापित)\n• आधार कार्ड (मोबाइल नंबर से लिंक)\n• आधार-सीडेड एवं NPCI सक्रिय बैंक खाता पासबुक\n• घोषणा पत्र (गैर-आयकर दाता)",
            "en": "Mandatory Documents:\n• Land Record (UP Bhulekh verified Khatauni)\n• Aadhaar Card (linked with active mobile number)\n• Bank Passbook/Account enabled for Aadhaar seeding and NPCI mapper\n• Self-declaration regarding non-income-tax status",
            "hinglish": "Zaroori documents:\n• Jameen ki Khatauni nakal (UP Bhulekh verified)\n• Aadhaar Card (mobile number se link hona chahiye)\n• Bank passbook jo Aadhaar-seeded aur NPCI active ho\n• Self-declaration ki aap income tax payer nahi hain",
            "pa": "ਜ਼ਰੂਰੀ ਦਸਤਾਵੇਜ਼:\n• ਜ਼ਮੀਨ ਦੀ ਖਤੌਨੀ (ਯੂ.ਪੀ. ਭੂਲੇਖ ਤੋਂ ਤਸਦੀਕਸ਼ੁਦਾ)\n• ਆਧਾਰ ਕਾਰਡ (ਮੋਬਾਈਲ ਨੰਬਰ ਨਾਲ ਲਿੰਕ)\n• ਆਧਾਰ-ਸੀਡਿਡ ਅਤੇ NPCI ਐਕਟਿਵ ਬੈਂਕ ਖਾਤਾ\n• ਸਵੈ-ਘੋਸ਼ਣਾ ਪੱਤਰ (ਗ਼ੈਰ-ਇਨਕਮ ਟੈਕਸ ਦਾਤਾ)"
        },
        "APPLICATION_PORTAL": {
            "hi": "आवेदन प्रक्रिया:\n1. आधिकारिक पोर्टल pmkisan.gov.in पर जाएं।\n2. 'Farmers Corner' में 'New Farmer Registration' पर क्लिक करें।\n3. आधार नंबर और मोबाइल नंबर दर्ज कर ओटीपी सत्यापित करें और खतौनी विवरण भरें। नजदीकी सीएससी (CSC) या जनसेवा केंद्र से भी करा सकते हैं।",
            "en": "Official Application Destination:\n1. Visit the official portal: https://pmkisan.gov.in\n2. Go to 'Farmers Corner' -> 'New Farmer Registration'.\n3. Enter Aadhaar number and mobile OTP, upload Khatauni details. Alternatively, visit any authorized Common Service Centre (CSC) in UP.",
            "hinglish": "Apply karne ka tarika:\n1. Official portal pmkisan.gov.in par jayein.\n2. 'Farmers Corner' me jakar 'New Farmer Registration' choose karein.\n3. Aadhaar number aur mobile OTP enter karein aur Khatauni details daalein. Aap paas ke kisi bhi CSC Jan Seva Kendra se bhi apply karwa sakte hain.",
            "pa": "ਅਰਜ਼ੀ ਦੇਣ ਦਾ ਤਰੀਕਾ:\n1. ਅਧਿਕਾਰਤ ਪੋਰਟਲ https://pmkisan.gov.in 'ਤੇ ਜਾਓ।\n2. 'Farmers Corner' ਵਿੱਚ ਜਾ ਕੇ 'New Farmer Registration' 'ਤੇ ਕਲਿੱਕ ਕਰੋ।\n3. ਆਧਾਰ ਨੰਬਰ ਅਤੇ ਮੋਬਾਈਲ ਓ.ਟੀ.ਪੀ. ਦਰਜ ਕਰਕੇ ਖਤੌਨੀ ਦਾ ਵੇਰਵਾ ਭਰੋ ਜਾਂ ਨੇੜਲੇ ਸੀ.ਐਸ.ਸੀ. (CSC) ਸੈਂਟਰ 'ਤੇ ਜਾਓ।"
        },
        "ISSUES_AND_STATUS": {
            "hi": "यदि आपकी किस्त रुकी हुई है, तो pmkisan.gov.in पर 'Know Your Status' में 3 चीजें जांचें:\n1. e-KYC: 'YES' होना चाहिए (ओटीपी या बायोमेट्रिक द्वारा करें)।\n2. Land Seeding: 'YES' होना चाहिए (यदि 'NO' है तो लेखपाल/तहसील में खतौनी जमा करें)।\n3. Aadhaar Bank Account Seeding: 'YES' होना चाहिए (बैंक शाखा जाकर डीबीटी सक्रिय कराएं)।",
            "en": "If your PM-KISAN installment is stuck, check three vital items under 'Know Your Status' on pmkisan.gov.in:\n1. e-KYC: Must be 'YES' (complete via OTP on portal or biometric at CSC).\n2. Land Seeding: Must be 'YES' (if 'NO', submit Khatauni to your local Tehsil/Lekhpal).\n3. Aadhaar Bank Account Seeding: Must be 'YES' (ensure your bank has linked your account to NPCI mapper).",
            "hinglish": "Agar aapki kist ruki hui hai, to pmkisan.gov.in par 'Know Your Status' me check karein:\n1. e-KYC: 'YES' hona chahiye (portal par OTP se ya CSC par biometric se karayein).\n2. Land Seeding: 'YES' hona chahiye (agar 'NO' hai to Tehsil/Lekhpal ko Khatauni submit karein).\n3. Aadhaar Bank Seeding: 'YES' hona chahiye (Bank jakar NPCI DBT form bharein).",
            "pa": "ਜੇਕਰ ਤੁਹਾਡੀ ਕਿਸ਼ਤ ਰੁਕੀ ਹੈ, ਤਾਂ pmkisan.gov.in 'ਤੇ 'Know Your Status' ਵਿੱਚ ਇਹ 3 ਚੀਜ਼ਾਂ ਜਾਂਚੋ:\n1. e-KYC: 'YES' ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ (ਪੋਰਟਲ 'ਤੇ ਓ.ਟੀ.ਪੀ. ਜਾਂ ਸੀ.ਐਸ.ਸੀ. ਤੋਂ ਬਾਇਓਮੈਟ੍ਰਿਕ ਕਰਵਾਓ)।\n2. Land Seeding: 'YES' ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ (ਜੇ 'NO' ਹੈ ਤਾਂ ਪਟਵਾਰੀ/ਤਹਿਸੀਲ ਵਿੱਚ ਖਤੌਨੀ ਜਮ੍ਹਾਂ ਕਰੋ)।\n3. Aadhaar Bank Seeding: 'YES' ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ (ਬੈਂਕ ਵਿੱਚ ਡੀਬੀਟੀ ਚਾਲੂ ਕਰਵਾਓ)।"
        },
        "HELPLINE": {
            "hi": "पीएम-किसान आधिकारिक टोल-फ्री हेल्पलाइन:\n• 155261 / 1800115526\n• किसान कॉल सेंटर: 1800-180-1551\n• ईमेल: pmkisan-ict@gov.in",
            "en": "PM-KISAN Official Grievance & Toll-Free Helplines:\n• 155261 / 1800115526\n• Kisan Call Centre: 1800-180-1551\n• Official Email: pmkisan-ict@gov.in",
            "hinglish": "PM-KISAN official helpline numbers:\n• Toll Free: 155261 ya 1800115526\n• Kisan Call Centre: 1800-180-1551\n• Official Email: pmkisan-ict@gov.in",
            "pa": "ਪੀ.ਐਮ-ਕਿਸਾਨ ਅਧਿਕਾਰਤ ਟੋਲ-ਫ੍ਰੀ ਹੈਲਪਲਾਈਨ:\n• 155261 / 1800115526\n• ਕਿਸਾਨ ਕਾਲ ਸੈਂਟਰ: 1800-180-1551\n• ਈਮੇਲ: pmkisan-ict@gov.in"
        }
    },
    "PMFBY": {
        "BENEFIT_AMOUNT": {
            "hi": "प्रधानमंत्री फसल बीमा योजना (PMFBY) के तहत किसान को केवल नाममात्र प्रीमियम देना होता है:\n• खरीफ फसलें: बीमित राशि का 2%\n• रबी फसलें: बीमित राशि का 1.5%\n• वाणिज्यिक/बागवानी फसलें: 5%\nप्राकृतिक आपदा (बाढ़, सूखा, ओला, बेमौसम बारिश) से नुकसान होने पर वास्तविक नुकसान का शत-प्रतिशत क्लेम सीधे खाते में मिलता है।",
            "en": "Under PMFBY, farmers pay only nominal subsidized premium rates:\n• Kharif Crops: 2% of Sum Insured\n• Rabi Crops: 1.5% of Sum Insured\n• Annual Commercial/Horticultural Crops: 5%\nRemaining premium is paid by Central and State Governments. Full assessed loss due to non-preventable natural calamities is paid directly via DBT.",
            "hinglish": "PMFBY fasal bima me kisan ko bahut kam premium dena hota hai:\n• Kharif fasal: Total bima rashi ka sirf 2%\n• Rabi fasal: Sirf 1.5%\n• Baagwani/Commercial fasal: 5%\nAgar fasal baadh, sukha, ola ya bimari se barbad ho to bima company assessed nuksan ka poora paisa seedhe bank account me deti hai.",
            "pa": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫ਼ਸਲ ਬੀਮਾ ਯੋਜਨਾ ਤਹਿਤ ਕਿਸਾਨ ਨੂੰ ਬਹੁਤ ਘੱਟ ਪ੍ਰੀਮੀਅਮ ਦੇਣਾ ਪੈਂਦਾ ਹੈ:\n• ਸਾਉਣੀ (ਖਰੀਫ਼) ਫ਼ਸਲਾਂ: ਬੀਮਾ ਰਕਮ ਦਾ 2%\n• ਹਾੜ੍ਹੀ (ਰਬੀ) ਫ਼ਸਲਾਂ: ਬੀਮਾ ਰਕਮ ਦਾ 1.5%\n• ਬਾਗਬਾਨੀ/ਵਪਾਰਕ ਫ਼ਸਲਾਂ: 5%\nਕੁਦਰਤੀ ਆਫ਼ਤਾਂ (ਹੜ੍ਹ, ਸੋਕਾ, ਗੜੇਮਾਰੀ, ਬੇਮੌਸਮੀ ਮੀਂਹ) ਨਾਲ ਹੋਏ ਨੁਕਸਾਨ ਦੀ ਪੂਰੀ ਭਰਪਾਈ ਬੈਂਕ ਖਾਤੇ ਵਿੱਚ ਕੀਤੀ ਜਾਂਦੀ ਹੈ।"
        },
        "TIMELINES": {
            "hi": "अत्यंत महत्वपूर्ण समय-सीमा (72 घंटे का नियम):\nस्थानीयकृत आपदा (जैसे ओलावृष्टि, जलभराव, बादल फटना) या कटाई के बाद खेत में रखी फसल के नुकसान की सूचना घटना के 72 घंटे के भीतर देना अनिवार्य है। सूचना 'Crop Insurance App' पर दें या 14447 पर कॉल करें या बैंक/कृषि अधिकारी को लिखित दें।",
            "en": "Critical Deadline (The 72-Hour Rule):\nIn case of localized calamities (hailstorm, cloud burst, waterlogging) or post-harvest loss, the farmer MUST intimate loss within 72 hours of the occurrence via the Crop Insurance App, toll-free number 14447, or in writing to the insuring bank/district agriculture officer.",
            "hinglish": "Sabse zaroori deadline (72 Ghante ka Niyam):\nAgar oley padein, khet me paani bhar jaye ya fasal kharab ho jaye, to ghatna ke 72 ghante ke andar information dena compulsory hai. Aap 'Crop Insurance App' par photo daal sakte hain, toll-free 14447 par call kar sakte hain ya bank/krishi vibhag ko suchit kar sakte hain.",
            "pa": "ਸਭ ਤੋਂ ਜ਼ਰੂਰੀ ਸਮਾਂ-ਸੀਮਾ (72 ਘੰਟਿਆਂ ਦਾ ਨਿਯਮ):\nਜੇਕਰ ਗੜੇਮਾਰੀ, ਹੜ੍ਹ ਜਾਂ ਬੇਮੌਸਮੀ ਮੀਂਹ ਕਾਰਨ ਫ਼ਸਲ ਦਾ ਨੁਕਸਾਨ ਹੁੰਦਾ ਹੈ, ਤਾਂ ਘਟਨਾ ਦੇ 72 ਘੰਟਿਆਂ ਦੇ ਅੰਦਰ ਸੂਚਨਾ ਦੇਣਾ ਲਾਜ਼ਮੀ ਹੈ। ਇਹ ਸੂਚਨਾ 'Crop Insurance App' ਰਾਹੀਂ, ਟੋਲ-ਫ੍ਰੀ ਨੰਬਰ 14447 'ਤੇ, ਜਾਂ ਬੈਂਕ/ਖੇਤੀਬਾੜੀ ਵਿਭਾਗ ਨੂੰ ਦਿੱਤੀ ਜਾ ਸਕਦੀ ਹੈ।"
        },
        "DOCUMENTS_REQUIRED": {
            "hi": "फसल बीमा हेतु आवश्यक दस्तावेज़:\n• खतौनी / भूलेख रिकॉर्ड\n• बुवाई प्रमाण पत्र (पटवारी/लेखपाल या ग्राम प्रधान द्वारा जारी बोवनी प्रमाण)\n• बैंक पासबुक (जिसमें KCC या बचत खाता हो)\n• आधार कार्ड\n• बटाईदार होने पर सहमति पत्र / बटाईनामा",
            "en": "Documents Required for Crop Insurance:\n• Land Record (Khatauni)\n• Sowing Certificate (issued by Lekhpal, Gram Pradhan, or Village Officer)\n• Bank Passbook (KCC or DBT-enabled Savings account)\n• Aadhaar Card\n• Valid Tenancy Agreement (if applying as non-loanee sharecropper/tenant)",
            "hinglish": "Fasal bima ke zaroori documents:\n• Jameen ki Khatauni\n• Buaai praman patra (Sowing certificate by Lekhpal ya Gram Pradhan)\n• Bank Passbook\n• Aadhaar Card\n• Agar bataidar hain to bataidar agreement ya sahmati patra",
            "pa": "ਫ਼ਸਲ ਬੀਮਾ ਲਈ ਜ਼ਰੂਰੀ ਦਸਤਾਵੇਜ਼:\n• ਜ਼ਮੀਨ ਦੀ ਖਤੌਨੀ\n• ਬਿਜਾਈ ਸਰਟੀਫਿਕੇਟ (ਪਟਵਾਰੀ ਜਾਂ ਸਰਪੰਚ ਵੱਲੋਂ ਤਸਦੀਕ)\n• ਬੈਂਕ ਪਾਸਬੁੱਕ\n• ਆਧਾਰ ਕਾਰਡ\n• ਹਿੱਸੇਦਾਰ/ਕਾਸ਼ਤਕਾਰ ਹੋਣ ਦੀ ਸੂਰਤ ਵਿੱਚ ਸਮਝੌਤਾ ਪੱਤਰ"
        },
        "APPLICATION_PORTAL": {
            "hi": "आवेदन कहाँ और कैसे करें:\n• ऋणी किसान (KCC धारक): संबंधित बैंक शाखा द्वारा स्वतः बीमा किया जाता है (यदि नहीं चाहते तो कटऑफ से 7 दिन पूर्व ऑप्ट-आउट फॉर्म भरें)।\n• गैर-ऋणी किसान: आधिकारिक पोर्टल https://pmfby.gov.in या नजदीकी CSC केंद्र से सीधे ऑनलाइन आवेदन कर सकते हैं।",
            "en": "Official Application Process:\n• Loanee Farmers (with active KCC): Enrolled automatically by their lending bank branch unless they opt out in writing 7 days before season cutoff.\n• Non-loanee Farmers: Self-register via the national portal https://pmfby.gov.in or apply at any CSC centre before the seasonal cutoff.",
            "hinglish": "Kaise apply karein:\n• KCC wale kisan: Bank branch automatically bima kar deti hai (agar nahi karwana to cutoff date se 7 din pehle opt-out application dena padta hai).\n• Bina KCC wale kisan: Seedhe https://pmfby.gov.in portal par ya nearest CSC centre jakar cutoff se pehle apply karein.",
            "pa": "ਕਿਵੇਂ ਅਪਲਾਈ ਕਰੀਏ:\n• ਕੇ.ਸੀ.ਸੀ. ਵਾਲੇ ਕਿਸਾਨ: ਬੈਂਕ ਬ੍ਰਾਂਚ ਵੱਲੋਂ ਆਪਣੇ ਆਪ ਬੀਮਾ ਕੀਤਾ ਜਾਂਦਾ ਹੈ (ਜੇ ਨਹੀਂ ਕਰਵਾਉਣਾ ਤਾਂ ਆਖ਼ਰੀ ਤਾਰੀਖ਼ ਤੋਂ 7 ਦਿਨ ਪਹਿਲਾਂ ਆਪਟ-ਆਊਟ ਫ਼ਾਰਮ ਦਿਓ)।\n• ਬਿਨਾਂ ਕਰਜ਼ੇ ਵਾਲੇ ਕਿਸਾਨ: https://pmfby.gov.in 'ਤੇ ਜਾ ਕੇ ਜਾਂ ਕਿਸੇ ਵੀ ਸੀ.ਐਸ.ਸੀ. ਸੈਂਟਰ 'ਤੇ ਜਾ ਕੇ ਆਨਲਾਈਨ ਅਪਲਾਈ ਕਰ ਸਕਦੇ ਹਨ।"
        },
        "HELPLINE": {
            "hi": "फसल बीमा टोल-फ्री हेल्पलाइन:\n• राष्ट्रीय फसल बीमा हेल्पलाइन: 14447\n• किसान कॉल सेंटर: 1800-180-1551\n• ऐप: 'Crop Insurance' (गूगल प्ले स्टोर पर उपलब्ध)",
            "en": "PMFBY Official Helplines:\n• National Crop Insurance Helpline: 14447\n• Kisan Call Centre: 1800-180-1551\n• Mobile App: 'Crop Insurance' on Google Play Store",
            "hinglish": "PMFBY Official Helplines:\n• Toll Free Complaint & Intimation: 14447\n• Kisan Call Centre: 1800-180-1551\n• App: Download 'Crop Insurance' from Play Store",
            "pa": "ਫ਼ਸਲ ਬੀਮਾ ਟੋਲ-ਫ੍ਰੀ ਹੈਲਪਲਾਈਨ:\n• ਕੌਮੀ ਫ਼ਸਲ ਬੀਮਾ ਹੈਲਪਲਾਈਨ: 14447\n• ਕਿਸਾਨ ਕਾਲ ਸੈਂਟਰ: 1800-180-1551\n• ਮੋਬਾਈਲ ਐਪ: 'Crop Insurance'"
        }
    },
    "PMKSY_PDMC": {
        "BENEFIT_AMOUNT": {
            "hi": "प्रति बूंद अधिक फसल (PMKSY-PDMC) योजना के तहत सूक्ष्म सिंचाई (ड्रिप और स्प्रिंकलर) पर भारी अनुदान मिलता है:\n• लघु एवं सीमांत किसान (<= 5 एकड़): 55% लागत अनुदान\n• अन्य बड़े किसान (> 5 एकड़): 45% लागत अनुदान\nउत्तर प्रदेश में अतिरिक्त राज्य टॉप-अप अनुदान भी उपलब्ध होता है।",
            "en": "Under PMKSY Per Drop More Crop (Micro-Irrigation), farmers receive substantial subsidies for installing drip and sprinkler systems:\n• Small & Marginal Farmers (<= 5 acres / 2 hectares): 55% of indicative unit cost\n• Other/Larger Farmers: 45% of indicative unit cost\nAdditional top-up incentives are released periodically by the UP Agriculture Department.",
            "hinglish": "PMKSY Drip aur Sprinkler scheme me government zabardast subsidy deti hai:\n• Chhote aur seemant kisan (2 hectare tak): Unit cost par 55% subsidy\n• Bade kisan (2 hectare se zyada): 45% subsidy\nUP me water conservation ke liye drip lagwane par state top-up bhi milta hai.",
            "pa": "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕ੍ਰਿਸ਼ੀ ਸਿੰਚਾਈ ਯੋਜਨਾ (ਡ੍ਰਿਪ ਅਤੇ ਸਪ੍ਰਿੰਕਲਰ) ਤਹਿਤ ਵੱਡੀ ਸਬਸਿਡੀ ਮਿਲਦੀ ਹੈ:\n• ਛੋਟੇ ਅਤੇ ਸੀਮਾਂਤ ਕਿਸਾਨ (2 ਹੈਕਟੇਅਰ ਤੱਕ): ਲਾਗਤ 'ਤੇ 55% ਸਬਸਿਡੀ\n• ਵੱਡੇ ਕਿਸਾਨ: 45% ਸਬਸਿਡੀ\nਯੂ.ਪੀ. ਸਰਕਾਰ ਵੱਲੋਂ ਪਾਣੀ ਬਚਾਉਣ ਲਈ ਵਾਧੂ ਟਾਪ-ਅੱਪ ਗ੍ਰਾਂਟ ਵੀ ਦਿੱਤੀ ਜਾਂਦੀ ਹੈ।"
        },
        "ELIGIBILITY": {
            "hi": "पात्रता एवं शर्तें:\n1. उत्तर प्रदेश में कृषि भूमि की वैध खतौनी।\n2. खेत पर सुरक्षित एवं चालू जल स्रोत (बोरवेल, ट्यूबवेल, निजी तालाब या नहर कनेक्शन) होना अनिवार्य है। बिना जल स्रोत के आवेदन निरस्त हो जाता है।",
            "en": "Eligibility & Conditions:\n1. Valid Khatauni landholding in Uttar Pradesh.\n2. Mandatory assured and operational irrigation water source (tubewell, borewell, private farm pond, or canal outlet) at the farm plot. Applications without an active water source are rejected.",
            "hinglish": "Eligibility shart:\n1. UP me kheti ki jameen (Khatauni) honi chahiye.\n2. Sabse zaroori: Khet par apna chaloo paani ka source (tubewell, borewell, pump ya khet talab) hona zaroori hai. Bina water source ke subsidy sanction nahi hoti.",
            "pa": "ਯੋਗਤਾ ਅਤੇ ਸ਼ਰਤਾਂ:\n1. ਉੱਤਰ ਪ੍ਰਦੇਸ਼ ਵਿੱਚ ਖੇਤੀਬਾੜੀ ਜ਼ਮੀਨ ਦੀ ਵੈਧ ਖਤੌਨੀ ਹੋਵੇ।\n2. ਖੇਤ ਵਿੱਚ ਚਾਲੂ ਪਾਣੀ ਦਾ ਸਾਧਨ (ਬੋਰਵੈੱਲ, ਟਿਊਬਵੈੱਲ, ਜਾਂ ਫਾਰਮ ਪੌਂਡ) ਹੋਣਾ ਲਾਜ਼ਮੀ ਹੈ। ਬਿਨਾਂ ਪਾਣੀ ਦੇ ਸਰੋਤ ਤੋਂ ਅਰਜ਼ੀ ਰੱਦ ਹੋ ਜਾਂਦੀ ਹੈ।"
        },
        "APPLICATION_PORTAL": {
            "hi": "आवेदन पोर्टल एवं प्रक्रिया:\n1. उत्तर प्रदेश उद्यान विभाग के आधिकारिक पोर्टल https://uphorticulture.gov.in पर जाएं।\n2. 'सूक्ष्म सिंचाई (ड्रिप/स्प्रिंकलर) हेतु पंजीकरण एवं टोकन' का चयन करें।\n3. अधिकृत निर्माता/कंपनी का चयन करें और डिमांड ड्राफ्ट/टोकन राशि जमा करें।",
            "en": "Official Application Destination:\n1. Visit the UP Horticulture portal: https://uphorticulture.gov.in\n2. Select 'Micro Irrigation (Drip/Sprinkler) Registration & Token Generation'.\n3. Choose from authorized empanelled manufacturers and complete unit inspection.",
            "hinglish": "Apply kahan karein:\n1. UP Horticulture ki official website https://uphorticulture.gov.in par jayein.\n2. 'Drip/Sprinkler Token' booking link par click karein.\n3. Empanelled company choose karein. Verification ke baad subsidy direct bank ya vendor ledger me adjust hoti hai.",
            "pa": "ਅਰਜ਼ੀ ਕਿਵੇਂ ਦੇਣੀ ਹੈ:\n1. ਯੂ.ਪੀ. ਬਾਗਬਾਨੀ ਵਿਭਾਗ ਦੇ ਅਧਿਕਾਰਤ ਪੋਰਟਲ https://uphorticulture.gov.in 'ਤੇ ਜਾਓ।\n2. 'ਸੂਖਮ ਸਿੰਚਾਈ (ਡ੍ਰਿਪ/ਸਪ੍ਰਿੰਕਲਰ) ਟੋਕਨ ਬੁਕਿੰਗ' ਲਿੰਕ ਚੁਣੋ।\n3. ਸਰਕਾਰ ਵੱਲੋਂ ਮਨਜ਼ੂਰਸ਼ੁਦਾ ਕੰਪਨੀ ਚੁਣ ਕੇ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਪੂਰੀ ਕਰੋ।"
        },
        "DOCUMENTS_REQUIRED": {
            "hi": "आवश्यक दस्तावेज़:\n• खतौनी की नकल\n• आधार कार्ड\n• बैंक खाता पासबुक\n• सिंचाई जल स्रोत का प्रमाण (बिजली कनेक्शन बिल, बोरवेल घोषणा, या ट्यूबवेल प्रमाण पत्र)",
            "en": "Required Documents:\n• Copy of Khatauni\n• Aadhaar Card\n• Bank Passbook\n• Proof of Irrigation Source (Electricity connection receipt, tubewell certificate, or farm pond declaration)",
            "hinglish": "Zaroori papers:\n• Khatauni nakal\n• Aadhaar Card\n• Bank Passbook\n• Paani ke source ka proof (Tubewell electricity bill ya boring declaration)",
            "pa": "ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼:\n• ਖਤੌਨੀ ਦੀ ਕਾਪੀ\n• ਆਧਾਰ ਕਾਰਡ\n• ਬੈਂਕ ਪਾਸਬੁੱਕ\n• ਸਿੰਚਾਈ ਸਰੋਤ ਦਾ ਸਬੂਤ (ਟਿਊਬਵੈੱਲ ਦਾ ਬਿਜਲੀ ਬਿੱਲ ਜਾਂ ਬੋਰਵੈੱਲ ਦਾ ਸਰਟੀਫਿਕੇਟ)"
        }
    },
    "KCC": {
        "BENEFIT_AMOUNT": {
            "hi": "किसान क्रेडिट कार्ड (KCC) के तहत:\n• ₹3,00,000 तक की ऋण सीमा पर मात्र 4% प्रभावी वार्षिक ब्याज दर (7% सामान्य दर में से 3% समय पर भुगतान करने पर ब्याज छूट मिलती है)।\n• ₹1,60,000 तक का ऋण बिना किसी बंधक (Collateral-Free / गिरवी मुक्त) के दिया जाता है।",
            "en": "Kisan Credit Card (KCC) Loan Terms:\n• Concessional credit up to Rs. 3,00,000 at an effective interest rate of only 4% per annum (7% normal rate minus 3% Prompt Repayment Incentive subvention).\n• Collateral-free loan without pledging land up to Rs. 1,60,000.",
            "hinglish": "KCC Loan ke fayde:\n• ₹3 Lakh tak ka loan sirf 4% effective interest rate par milta hai (7% standard rate hota hai, aur time par repayment karne par 3% subsidy mil jati hai).\n• ₹1.6 Lakh tak ka loan bina jameen girvi rakhe (Collateral-free) milta hai.",
            "pa": "ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ (ਕੇ.ਸੀ.ਸੀ.) ਦੇ ਲਾਭ:\n• ₹3,00,000 ਤੱਕ ਦਾ ਕਰਜ਼ਾ ਕੇਵਲ 4% ਸਾਲਾਨਾ ਵਿਆਜ ਦਰ 'ਤੇ (7% ਮੁੱਢਲੀ ਦਰ 'ਚੋਂ ਸਮੇਂ ਸਿਰ ਭੁਗਤਾਨ 'ਤੇ 3% ਦੀ ਵਿਆਜ ਛੋਟ)।\n• ₹1,60,000 ਤੱਕ ਦਾ ਕਰਜ਼ਾ ਬਿਨਾਂ ਜ਼ਮੀਨ ਗਹਿਣੇ ਰੱਖੇ (ਬਿਨਾਂ ਗਾਰੰਟੀ) ਮਿਲਦਾ ਹੈ।"
        },
        "APPLICATION_PORTAL": {
            "hi": "आवेदन कहाँ करें:\n1. किसी भी नजदीकी सार्वजनिक बैंक, ग्रामीण बैंक (जैसे आर्यावर्त बैंक, बड़ौदा यूपी बैंक) या सहकारी बैंक में जाएं।\n2. एक पन्ने का सरलीकृत KCC फॉर्म भरें। यदि आप पीएम-किसान लाभार्थी हैं तो मात्र आधार व खतौनी से 14 दिनों के भीतर KCC जारी करने का निर्देश है।",
            "en": "Where to Apply:\n1. Visit any nearby Commercial Bank branch, Regional Rural Bank (Aryavart Bank, Baroda UP Bank), or District Cooperative Bank.\n2. Submit the one-page simplified KCC form. Banks are instructed to process and issue KCC within 14 working days for verified PM-KISAN beneficiaries.",
            "hinglish": "Apply kaise karein:\n1. Kisi bhi paas ke Gramin Bank (Aryavart, Baroda UP Bank) ya SBI/PNB branch me jayein.\n2. 1-page ka simplified KCC form bharein. Agar aap PM-KISAN ke beneficiary hain to sirf Aadhaar aur Khatauni se 14 din ke andar KCC ban jata hai.",
            "pa": "ਅਰਜ਼ੀ ਕਿੱਥੇ ਦੇਣੀ ਹੈ:\n1. ਕਿਸੇ ਵੀ ਨੇੜਲੀ ਬੈਂਕ ਬ੍ਰਾਂਚ, ਪੇਂਡੂ ਬੈਂਕ (ਆਰਿਆਵਰਤ, ਬੜੌਦਾ ਯੂ.ਪੀ. ਬੈਂਕ) ਜਾਂ ਸਹਿਕਾਰੀ ਬੈਂਕ ਵਿੱਚ ਜਾਓ।\n2. ਸਰਲ 1-ਪੰਨੇ ਵਾਲਾ ਕੇ.ਸੀ.ਸੀ. ਫ਼ਾਰਮ ਭਰੋ। ਪੀ.ਐਮ-ਕਿਸਾਨ ਲਾਭਪਾਤਰੀਆਂ ਲਈ 14 ਦਿਨਾਂ ਵਿੱਚ ਕਾਰਡ ਜਾਰੀ ਕਰਨ ਦੀਆਂ ਸਰਕਾਰੀ ਹਦਾਇਤਾਂ ਹਨ।"
        },
        "DOCUMENTS_REQUIRED": {
            "hi": "आवश्यक दस्तावेज़:\n• खतौनी नकल (फसल क्षेत्र निर्धारण हेतु)\n• आधार कार्ड एवं पैन कार्ड (या फॉर्म 60)\n• बोई गई फसल का विवरण\n• दो पासपोर्ट साइज फोटो\n• अन्य किसी बैंक में बकाया न होने का नो-ड्यूज शपथ पत्र",
            "en": "Required Documents:\n• Land Record (Khatauni) reflecting cultivated acreage\n• Aadhaar Card & PAN Card (or Form 60)\n• Current cropping pattern details\n• Two passport-sized photographs\n• No-dues declaration regarding no other pending agricultural dues",
            "hinglish": "Zaroori documents:\n• Jameen ki Khatauni\n• Aadhaar Card aur PAN Card\n• Khet me boi gayi fasal ka details\n• 2 passport size photos\n• No-dues declaration",
            "pa": "ਲੋੜੀਂਦੇ ਕਾਗਜ਼ਾਤ:\n• ਜ਼ਮੀਨ ਦੀ ਖਤੌਨੀ\n• ਆਧਾਰ ਕਾਰਡ ਅਤੇ ਪੈਨ ਕਾਰਡ\n• ਬੀਜੀ ਹੋਈ ਫ਼ਸਲ ਦਾ ਵੇਰਵਾ\n• 2 ਪਾਸਪੋਰਟ ਸਾਈਜ਼ ਫੋਟੋਆਂ\n• ਨੋ-ਡਿਊਜ਼ ਹਲਫੀਆ ਬਿਆਨ"
        }
    },
    "UP_KRISHAK_DURGHATNA": {
        "BENEFIT_AMOUNT": {
            "hi": "मुख्यमंत्री कृषक दुर्घटना कल्याण योजना (उत्तर प्रदेश):\n• किसान की दुर्घटना में मृत्यु या दोनों हाथ/पैर/आंखें पूर्णतः दिव्यांग होने पर: ₹5,00,000 की एकमुश्त अनुग्रह सहायता (Ex-Gratia)।\n• एक अंग स्थायी रूप से दिव्यांग होने पर: ₹2,50,000 से ₹3,75,000 की सहायता।\n• स्पष्टीकरण: यह एकमुश्त दुर्घटना सहायता है, कोई मासिक पेंशन नहीं है।",
            "en": "Mukhyamantri Krishak Durghatna Kalyan Yojana (Uttar Pradesh):\n• In the event of accidental death or permanent 100% disability (loss of both limbs/eyes): One-time ex-gratia relief of Rs. 5,00,000.\n• In case of partial permanent disability (loss of one limb): Rs. 2,50,000 to Rs. 3,75,000.\n• Clarification: This is a one-time relief payment, NOT an ongoing monthly pension.",
            "hinglish": "Mukhyamantri Krishak Durghatna Kalyan Yojana (UP):\n• Kheti ya kisi durghatna me kisan ki maut hone par ya 100% disability par: Ek-musht (one-time) ₹5,00,000 ki financial help milti hai.\n• Ek haath ya pair khone par: ₹2,50,000 se ₹3,75,000 tak help milti hai.\n• Note: Yeh one-time relief assistance hai, koi monthly pension nahi hai.",
            "pa": "ਮੁੱਖ ਮੰਤਰੀ ਕਿਸਾਨ ਦੁਰਘਟਨਾ ਕਲਿਆਣ ਯੋਜਨਾ (ਯੂ.ਪੀ.):\n• ਹਾਦਸੇ ਵਿੱਚ ਕਿਸਾਨ ਦੀ ਮੌਤ ਜਾਂ 100% ਅੰਗਹੀਣਤਾ ਹੋਣ 'ਤੇ: ₹5,00,000 ਦੀ ਇਕਮੁਸ਼ਤ (One-time) ਸਹਾਇਤਾ ਮਿਲਦੀ ਹੈ।\n• ਇੱਕ ਅੰਗ ਗਵਾਉਣ 'ਤੇ: ₹2,50,000 ਤੋਂ ₹3,75,000 ਤੱਕ ਦੀ ਸਹਾਇਤਾ।\n• ਸਪੱਸ਼ਟੀਕਰਨ: ਇਹ ਇੱਕ ਵਾਰ ਮਿਲਣ ਵਾਲੀ ਹਾਦਸਾ ਰਾਹਤ ਹੈ, ਕੋਈ ਮਹੀਨਾਵਾਰ ਪੈਨਸ਼ਨ ਨਹੀਂ ਹੈ।"
        },
        "ELIGIBILITY": {
            "hi": "पात्रता:\n1. पीड़ित किसान या उसके आश्रित (पति/पत्नी, पुत्र, पुत्री, पुत्रवधू, पौत्र/पौत्री) अथवा पंजीकृत बटाईदार की आयु 18 से 70 वर्ष के बीच होनी चाहिए।\n2. दुर्घटना उत्तर प्रदेश की सीमा में या खेती के कार्य के दौरान हुई हो (सर्पदंश, आकाशीय बिजली, डूबना, सड़क दुर्घटना आदि शामिल)।",
            "en": "Eligibility Criteria:\n1. Age of the victim (account-holding farmer, co-sharer, legal heir, spouse, son, daughter, daughter-in-law, or registered sharecropper/bataidar) must be between 18 and 70 years.\n2. Covers accidents occurring during agricultural work or daily life, including snakebite, lightning, drowning, tractor overturned, electrocution, and road mishaps within UP.",
            "hinglish": "Eligibility rules:\n1. Kisan ya uske family member (patni, beta, beti, bahu, pota/poti) ya bataidar ki age 18 se 70 saal ke beech honi chahiye.\n2. Durghatna me saamp kaatna, aakashiy bijli (lightning), khet me tractor palatna, ya road accident sabhi covered hain.",
            "pa": "ਯੋਗਤਾ ਦੇ ਨਿਯਮ:\n1. ਪੀੜਤ ਕਿਸਾਨ ਜਾਂ ਪਰਿਵਾਰਕ ਮੈਂਬਰ (ਪਤਨੀ, ਪੁੱਤਰ, ਧੀ, ਨੂੰਹ, ਪੋਤਾ/ਪੋਤੀ) ਜਾਂ ਹਿੱਸੇਦਾਰ ਦੀ ਉਮਰ 18 ਤੋਂ 70 ਸਾਲ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ।\n2. ਸੱਪ ਦੇ ਡੰਗਣ, ਅਸਮਾਨੀ ਬਿਜਲੀ ਡਿੱਗਣ, ਟਰੈਕਟਰ ਪਲਟਣ, ਡੁੱਬਣ ਜਾਂ ਸੜਕ ਹਾਦਸੇ ਕਾਰਨ ਹੋਇਆ ਨੁਕਸਾਨ ਇਸ ਵਿੱਚ ਸ਼ਾਮਲ ਹੈ।"
        },
        "TIMELINES": {
            "hi": "दावा प्रस्तुत करने की अनिवार्य समय-सीमा:\nदुर्घटना की तिथि से 45 दिनों के भीतर संबंधित तहसील में उपजिलाधिकारी (SDM) कार्यालय में आवेदन जमा करना अनिवार्य है। विशेष परिस्थितियों में जिलाधिकारी (DM) अधिकतम 75 दिनों तक की देरी को माफ कर सकते हैं। इसके बाद दावा स्वीकार नहीं होगा।",
            "en": "Mandatory Claim Timelines:\nClaim must be submitted within 45 days from the date of the accident to the Sub-Divisional Magistrate (SDM) Tehsil office. In exceptional circumstances, the District Magistrate (DM) can condone delay up to a maximum of 75 days. Claims beyond 75 days are time-barred.",
            "hinglish": "Claim submit karne ki last date:\nAccident hone ki date se 45 dino ke andar Tehsil me SDM office me claim form aur documents jama karna zaroori hai. Bahut zaroori reason hone par DM sahab maximum 75 din tak condone kar sakte hain. 75 din ke baad claim reject ho jayega.",
            "pa": "ਦਾਅਵਾ ਜਮ੍ਹਾਂ ਕਰਨ ਦੀ ਆਖ਼ਰੀ ਤਾਰੀਖ਼:\nਹਾਦਸੇ ਦੀ ਤਾਰੀਖ਼ ਤੋਂ 45 ਦਿਨਾਂ ਦੇ ਅੰਦਰ ਤਹਿਸੀਲ ਵਿੱਚ ਐਸ.ਡੀ.ਐਮ. (SDM) ਦਫ਼ਤਰ ਵਿੱਚ ਅਰਜ਼ੀ ਜਮ੍ਹਾਂ ਕਰਵਾਉਣੀ ਲਾਜ਼ਮੀ ਹੈ। ਖ਼ਾਸ ਹਾਲਤਾਂ ਵਿੱਚ ਡੀ.ਸੀ. (DM) ਸਾਹਿਬ ਵੱਧ ਤੋਂ ਵੱਧ 75 ਦਿਨਾਂ ਤੱਕ ਦੀ ਦੇਰੀ ਮਾਫ਼ ਕਰ ਸਕਦੇ ਹਨ।"
        },
        "DOCUMENTS_REQUIRED": {
            "hi": "दावा दस्तावेज़:\n• मृत्यु प्रमाण पत्र या मुख्य चिकित्सा अधिकारी (CMO) द्वारा जारी दिव्यांगता प्रमाण पत्र\n• पोस्टमार्टम रिपोर्ट एवं पंचनामा (मृत्यु के मामले में)\n• एफआईआर (FIR) की प्रति (यदि पुलिस केस हो)\n• खतौनी नकल एवं परिवार रजिस्टर नकल (नातेदारी सिद्ध करने हेतु)\n• आश्रित का आधार कार्ड एवं बैंक पासबुक",
            "en": "Required Claim Documents:\n• Death Certificate OR Permanent Disability Certificate issued by CMO\n• Post-Mortem Report and Police Panchnama (in case of death)\n• Copy of First Information Report (FIR) where applicable\n• Copy of Khatauni and Parivar Register Nakal (to prove legal heirship)\n• Aadhaar Card and Bank Passbook of the legal claimant/heir",
            "hinglish": "Zaroori claim documents:\n• Death certificate ya CMO dwara disability certificate\n• Post-mortem report aur police panchnama\n• FIR ki copy (agar road accident/police case ho)\n• Khatauni nakal aur Parivar register nakal (rishta prove karne ke liye)\n• Claimant ka Aadhaar aur bank passbook",
            "pa": "ਦਾਅਵੇ ਲਈ ਜ਼ਰੂਰੀ ਦਸਤਾਵੇਜ਼:\n• ਮੌਤ ਦਾ ਸਰਟੀਫਿਕੇਟ ਜਾਂ ਸੀ.ਐਮ.ਓ. (CMO) ਵੱਲੋਂ ਜਾਰੀ ਅੰਗਹੀਣਤਾ ਸਰਟੀਫਿਕੇਟ\n• ਪੋਸਟ-ਮਾਰਟਮ ਰਿਪੋਰਟ ਅਤੇ ਪੁਲਿਸ ਪੰਚਨਾਮਾ\n• ਐਫ.ਆਈ.ਆਰ. (ਜੇਕਰ ਲਾਗੂ ਹੋਵੇ)\n• ਜ਼ਮੀਨ ਦੀ ਖਤੌਨੀ ਅਤੇ ਪਰਿਵਾਰ ਰਜਿਸਟਰ ਦੀ ਨਕਲ\n• ਵਾਰਸ ਦਾ ਆਧਾਰ ਕਾਰਡ ਅਤੇ ਬੈਂਕ ਪਾਸਬੁੱਕ"
        }
    },
    "SMAM_MACHINERY": {
        "BENEFIT_AMOUNT": {
            "hi": "कृषि यंत्रीकरण (SMAM) योजना के तहत अनुदान:\n• व्यक्तिगत कृषि यंत्र (रोटावेटर, लेजर लैंड लेवलर, हैप्पी सीडर आदि): 40% से 50% तक का अनुदान।\n• कस्टम हायरिंग सेंटर (CHC) की स्थापना: ₹10 लाख तक की लागत पर 40% (अधिकतम ₹4 लाख) तक की छूट।",
            "en": "Under Sub-Mission on Agricultural Mechanization (SMAM):\n• Individual Farm Implements (Rotavator, Laser Leveller, Seed Drill): 40% to 50% unit cost subsidy.\n• Custom Hiring Centre (CHC) setup: 40% subsidy up to a project ceiling of Rs. 10 Lakhs (maximum Rs. 4 Lakh subsidy).",
            "hinglish": "Krishi Yantra / SMAM scheme me subsidy:\n• Individual machine (Rotavator, Happy Seeder, Laser Leveller, Thresher): 40% se 50% tak ki subsidy milti hai.\n• Custom Hiring Centre kholne ke liye: ₹10 lakh tak ke project par 40% (max ₹4 lakh) ki chhoot milti hai.",
            "pa": "ਖੇਤੀ ਮਸ਼ੀਨਰੀ (SMAM) ਯੋਜਨਾ ਤਹਿਤ ਸਬਸਿਡੀ:\n• ਨਿੱਜੀ ਸੰਦਾਂ (ਰੋਟਾਵੇਟਰ, ਲੇਜ਼ਰ ਲੈਵਲਰ, ਸੁਪਰ ਸੀਡਰ): 40% ਤੋਂ 50% ਤੱਕ ਦੀ ਸਬਸਿਡੀ।\n• ਕਸਟਮ ਹਾਇਰਿੰਗ ਸੈਂਟਰ (CHC) ਸਥਾਪਤ ਕਰਨ ਲਈ: ₹10 ਲੱਖ ਦੇ ਪ੍ਰੋਜੈਕਟ 'ਤੇ 40% (ਵੱਧ ਤੋਂ ਵੱਧ ₹4 ਲੱਖ) ਦੀ ਗ੍ਰਾਂਟ।"
        },
        "APPLICATION_PORTAL": {
            "hi": "आवेदन प्रक्रिया:\n1. उत्तर प्रदेश कृषि विभाग के पोर्टल https://agriculture.up.gov.in (अथवा agrimachinery.nic.in) पर जाएं।\n2. 'यंत्रों पर अनुदान हेतु टोकन निकालें' पर क्लिक करें।\n3. निर्धारित समयावधि में टोकन बुकिंग करें और बैंक चालान/सुरक्षा राशि जमा कर बिल अपलोड करें।",
            "en": "Application Process:\n1. Visit the UP Agriculture Portal: https://agriculture.up.gov.in (or https://agrimachinery.nic.in)\n2. Click on 'Generate Token for Machinery Subsidy'.\n3. Book token during announced booking windows, deposit the refundable security token amount, and upload purchase bill from authorized dealers.",
            "hinglish": "Token kaise book karein:\n1. UP Agriculture portal https://agriculture.up.gov.in (ya https://agrimachinery.nic.in) par jayein.\n2. 'Yantra Subsidy Token' par click karein.\n3. Jab portal khulta hai tab token book karein aur prescribed token money jama karke authorized dealer se machine lekar bill upload karein.",
            "pa": "ਅਰਜ਼ੀ ਦਾ ਤਰੀਕਾ:\n1. ਯੂ.ਪੀ. ਖੇਤੀਬਾੜੀ ਪੋਰਟਲ https://agriculture.up.gov.in (ਜਾਂ https://agrimachinery.nic.in) 'ਤੇ ਜਾਓ।\n2. 'ਮਸ਼ੀਨਰੀ ਸਬਸਿਡੀ ਟੋਕਨ' 'ਤੇ ਕਲਿੱਕ ਕਰੋ।\n3. ਟੋਕਨ ਬੁਕਿੰਗ ਕਰਵਾ ਕੇ ਸਕਿਓਰਿਟੀ ਜਮ੍ਹਾਂ ਕਰੋ ਅਤੇ ਮਨਜ਼ੂਰਸ਼ੁਦਾ ਡੀਲਰ ਤੋਂ ਬਿੱਲ ਅਪਲੋਡ ਕਰੋ।"
        }
    }
}


def _build_convergence_answer(lang: str) -> AssistantQueryResponse:
    answers = {
        "hi": (
            "योजनाओं का एक साथ लाभ (अभिसरण / Convergence):\n"
            "हाँ, एक ही किसान परिवार एक साथ कई योजनाओं का लाभ ले सकता है, क्योंकि इनके उद्देश्य अलग-अलग हैं:\n"
            "1. PM-KISAN (आय सहायता: ₹6,000/वर्ष) + KCC (सस्ता फसली ऋण: 4% ब्याज पर) + PMFBY (फसल बर्बादी पर बीमा सुरक्षा) — ये तीनों योजनाएं एक साथ बिना किसी बाधा के ली जा सकती हैं।\n"
            "2. साथ ही, यदि आप सिंचाई प्रणाली लगाना चाहते हैं तो PMKSY-PDMC से 55% अनुदान भी मिल सकता है।\n"
            "प्रतिबंध: आप एक ही कार्य के लिए दो अलग-अलग योजनाओं से दोहरा अनुदान नहीं ले सकते (उदा. एक ही बोरवेल पर दो जगह सब्सिडी नहीं मिलेगी)।"
        ),
        "en": (
            "Multi-Scheme Convergence & Simultaneous Benefits:\n"
            "Yes, an eligible farmer family can pursue multiple complementary agricultural schemes simultaneously:\n"
            "1. PM-KISAN (Direct Income Support of Rs. 6,000/yr) + KCC (Concessional Crop Loan at 4%) + PMFBY (Natural Calamity Crop Insurance) are 100% mutually compatible and complementary.\n"
            "2. Farmers may additionally obtain 55% capital subsidy for drip/sprinkler micro-irrigation under PMKSY-PDMC.\n"
            "Strict Restriction: Double-subsidization for the exact same physical asset (e.g. claiming machinery subsidy twice for the same implement) is strictly prohibited by government audit rules."
        ),
        "hinglish": (
            "Multi-Scheme Convergence (Ek Saath Schemes Ka Labh):\n"
            "Haan kisan bhai, aap ek saath multiple schemes ka fayda utha sakte hain:\n"
            "1. PM-KISAN (saal ke ₹6,000) + KCC Card (4% byaj par ₹3 Lakh tak ka loan) + PMFBY (fasal ka bima) — yeh teeno ek saath chalu reh sakte hain aur ek doosre ko cancel nahi karte.\n"
            "2. Saath hi aap khet me Drip sinchai lagwane ke liye 55% subsidy (PMKSY) bhi le sakte hain.\n"
            "Rule: Sirf ek hi physical asset (jaise ek hi tractor ya borewell) par do alag yojanaon se double subsidy nahi li ja sakti."
        ),
        "pa": (
            "ਸਕੀਮਾਂ ਦਾ ਇਕੱਠਿਆਂ ਲਾਭ (Convergence):\n"
            "ਹਾਂਜੀ ਕਿਸਾਨ ਵੀਰੋ, ਇੱਕ ਪਰਿਵਾਰ ਕਈ ਵੱਖ-ਵੱਖ ਸਕੀਮਾਂ ਦਾ ਲਾਭ ਇਕੱਠੇ ਲੈ ਸਕਦਾ ਹੈ:\n"
            "1. ਪੀ.ਐਮ-ਕਿਸਾਨ (ਸਾਲਾਨਾ ₹6,000) + ਕੇ.ਸੀ.ਸੀ. (4% ਵਿਆਜ 'ਤੇ ਕਰਜ਼ਾ) + ਫ਼ਸਲ ਬੀਮਾ (PMFBY) — ਇਹ ਤਿੰਨੇ ਸਕੀਮਾਂ ਇਕੱਠੀਆਂ ਬਿਨਾਂ ਕਿਸੇ ਰੋਕ-ਟੋਕ ਦੇ ਲਈਆਂ ਜਾ ਸਕਦੀਆਂ ਹਨ।\n"
            "2. ਇਸਦੇ ਨਾਲ ਹੀ ਡ੍ਰਿਪ ਸਿੰਚਾਈ 'ਤੇ 55% ਸਬਸਿਡੀ ਵੀ ਲਈ ਜਾ ਸਕਦੀ ਹੈ।\n"
            "ਨਿਯਮ: ਇੱਕੋ ਸੰਦ ਜਾਂ ਇੱਕੋ ਬੋਰਵੈੱਲ 'ਤੇ ਦੋ ਵੱਖ-ਵੱਖ ਸਕੀਮਾਂ ਤੋਂ ਦੂਹਰੀ ਸਬਸਿਡੀ ਨਹੀਂ ਲਈ ਜਾ ਸਕਦੀ।"
        )
    }

    return AssistantQueryResponse(
        answer=answers.get(lang, answers["hi"]),
        source_title="Government Agricultural Convergence Framework & Gazette Register",
        authority="Ministry of Agriculture & Farmers Welfare, GoI / UP Dept of Agriculture",
        section="Inter-Scheme Synergy & Anti-Duplication Directives",
        verified_at="2026-01-20T10:00:00Z",
        can_verify=True,
        detected_language=lang,
        related_schemes=["PM_KISAN", "KCC", "PMFBY", "PMKSY_PDMC"]
    )


def _build_general_scheme_answer(scheme_code: str, lang: str) -> AssistantQueryResponse:
    scheme = SCHEME_CATALOGUE[scheme_code]

    if lang == "hi":
        answer = (
            f"योजना: {scheme['official_name_hi']}\n\n"
            f"मुख्य लाभ: {scheme['benefit_summary_hi']}\n\n"
            f"आधिकारिक पोर्टल: {scheme['official_portal_url']}\n"
            f"प्रशासनिक विभाग: {scheme['department']}\n"
            f"सत्यापित स्रोत: {scheme['source_title']} ({scheme['source_section']})"
        )
    elif lang == "en":
        answer = (
            f"Scheme: {scheme['official_name_en']}\n\n"
            f"Primary Benefit: {scheme['benefit_summary_en']}\n\n"
            f"Official Destination: {scheme['official_portal_url']}\n"
            f"Administering Authority: {scheme['department']}\n"
            f"Source Citation: {scheme['source_title']} ({scheme['source_section']})"
        )
    elif lang == "hinglish":
        answer = (
            f"Scheme: {scheme['official_name_hi']}\n\n"
            f"Fayde: {scheme['benefit_summary_hi']}\n\n"
            f"Official Website: {scheme['official_portal_url']}\n"
            f"Department: {scheme['department']}\n"
            f"Grounded Source: {scheme['source_title']}"
        )
    elif lang == "pa":
        answer = (
            f"ਸਕੀਮ ਦਾ ਨਾਮ: {scheme['official_name_hi']}\n\n"
            f"ਮੁੱਖ ਲਾਭ: {scheme['benefit_summary_hi']}\n\n"
            f"ਅਧਿਕਾਰਤ ਪੋਰਟਲ: {scheme['official_portal_url']}\n"
            f"ਵਿਭਾਗ: {scheme['department']}\n"
            f"ਪ੍ਰਮਾਣਿਤ ਸਰੋਤ: {scheme['source_title']}"
        )
    else:
        answer = f"{scheme['official_name_hi']}: {scheme['benefit_summary_hi']} Portal: {scheme['official_portal_url']}"

    return AssistantQueryResponse(
        answer=answer,
        source_title=scheme["source_title"],
        authority=scheme["department"],
        section=scheme["source_section"],
        verified_at=scheme["verified_at"],
        can_verify=True,
        detected_language=lang,
        related_schemes=[scheme_code]
    )


def _build_unverified_fallback(lang: str) -> AssistantQueryResponse:
    fallbacks = {
        "hi": (
            "यह प्रश्न वर्तमान में सत्यापित सरकारी नियमों में दर्ज नहीं है अथवा अपुष्ट है।\n"
            "योजना साथी किसानों को केवल 100% प्रमाणित सरकारी जानकारी प्रदान करता है और किसी भी अप्रमाणित दावे से बचता है।\n"
            "कृपया अपने प्रश्न को विशिष्ट योजना (जैसे पीएम-किसान, फसल बीमा, केसीसी, ड्रिप सिंचाई या दुर्घटना कल्याण) से जोड़कर पूछें, "
            "अथवा अपने विकास खंड (Block) कृषि प्रसार अधिकारी से संपर्क करें।"
        ),
        "en": (
            "This query is not covered by verified government agricultural gazettes or statutory scheme records in Uttar Pradesh.\n"
            "YojanaSaathi strictly enforces an anti-hallucination policy and never speculates on government benefits.\n"
            "Please ask specifically about supported UP schemes (PM-KISAN, PMFBY Crop Insurance, KCC, PMKSY Drip Irrigation, UP Krishak Durghatna, or SMAM Machinery), "
            "or contact your Block Agriculture Extension Officer."
        ),
        "hinglish": (
            "Yeh sawal verified government agricultural records ya official gazette me directly match nahi ho raha hai.\n"
            "YojanaSaathi par hum kisan bhaiyon ko sirf 100% official aur sachhi jankari dete hain bina kisi farzi daawe ke.\n"
            "Kripya apna question kisi scheme (jaise PM-KISAN, Fasal Bima, KCC loan, Drip sinchai, ya Durghatna kalyan) ke baare me poochein, "
            "ya apne Block Agriculture Office se sampark karein."
        ),
        "pa": (
            "ਇਹ ਸਵਾਲ ਇਸ ਵੇਲੇ ਸਰਕਾਰੀ ਖੇਤੀਬਾੜੀ ਗਜ਼ਟ ਜਾਂ ਪ੍ਰਮਾਣਿਤ ਨਿਯਮਾਂ ਵਿੱਚ ਦਰਜ ਨਹੀਂ ਹੈ।\n"
            "ਯੋਜਨਾ ਸਾਥੀ ਕਿਸਾਨਾਂ ਨੂੰ ਸਿਰਫ਼ 100% ਅਧਿਕਾਰਤ ਅਤੇ ਪੁਸ਼ਟੀ ਕੀਤੀ ਜਾਣਕਾਰੀ ਪ੍ਰਦਾਨ ਕਰਦਾ ਹੈ।\n"
            "ਕਿਰਪਾ ਕਰਕੇ ਆਪਣਾ ਸਵਾਲ ਪ੍ਰਮੁੱਖ ਸਕੀਮਾਂ (ਪੀ.ਐਮ-ਕਿਸਾਨ, ਫ਼ਸਲ ਬੀਮਾ, ਕੇ.ਸੀ.ਸੀ., ਡ੍ਰਿਪ ਸਿੰਚਾਈ, ਜਾਂ ਦੁਰਘਟਨਾ ਕਲਿਆਣ) ਨਾਲ ਸੰਬੰਧਿਤ ਪੁੱਛੋ, "
            "ਜਾਂ ਆਪਣੇ ਬਲਾਕ ਖੇਤੀਬਾੜੀ ਅਫ਼ਸਰ ਨਾਲ ਰਾਬਤਾ ਕਾਇਮ ਕਰੋ।"
        )
    }

    return AssistantQueryResponse(
        answer=fallbacks.get(lang, fallbacks["hi"]),
        source_title="YojanaSaathi Policy Audit Desk",
        authority="Independent Policy Safeguard",
        section="Unverified Content & Anti-Hallucination Gate",
        verified_at="2026-01-20T00:00:00Z",
        can_verify=False,
        detected_language=lang,
        related_schemes=[]
    )


def answer_scheme_question(
    query: str,
    scheme_code: Optional[str] = None,
    language: Optional[str] = None
) -> AssistantQueryResponse:
    """
    Main entry point for grounded multilingual Q&A.
    """
    q_raw = query.strip()
    if not q_raw:
        lang = detect_or_normalize_language("", language)
        return _build_unverified_fallback(lang)

    q = q_raw.lower()
    lang = detect_or_normalize_language(q_raw, language)

    # Check for multi-scheme convergence question
    if _identify_topic(q) == "CONVERGENCE" or (
        ("saath" in q or "combine" in q or "together" in q or "ek saath" in q or "ਦੋਵੇਂ" in q or "ਦੋਨੋ" in q)
        and ("pm-kisan" in q or "kisan" in q or "kcc" in q or "bima" in q)
    ):
        return _build_convergence_answer(lang)

    # Identify Scheme
    target_code = _identify_scheme(q, scheme_code)

    if not target_code or target_code not in SCHEME_CATALOGUE:
        # Check if they are asking about all schemes generally
        if any(k in q for k in ["kaun kaun si", "konsi", "all schemes", "list", "sab yojana", "ਸਾਰੀਆਂ ਸਕੀਮਾਂ", "योजनाएं"]):
            schemes_text = {
                "hi": "उत्तर प्रदेश में 6 प्रमुख सत्यापित कृषि योजनाएं उपलब्ध हैं:\n1. पीएम-किसान (PM-KISAN) - ₹6,000 वार्षिक आय सहायता\n2. पीएम फसल बीमा (PMFBY) - 1.5%/2% प्रीमियम पर आपदा सुरक्षा\n3. पीएम कृषि सिंचाई (PMKSY-PDMC) - ड्रिप/स्प्रिंकलर पर 55% अनुदान\n4. किसान क्रेडिट कार्ड (KCC) - 4% ब्याज पर ₹3 लाख तक ऋण\n5. मुख्यमंत्री कृषक दुर्घटना कल्याण - ₹5 लाख तक की दुर्घटना सहायता\n6. कृषि यंत्रीकरण (SMAM) - ट्रैक्टर व कृषि यंत्रों पर 40-50% छूट।\n\nआप इनमें से किसी भी योजना के बारे में विस्तार से पूछ सकते हैं।",
                "en": "6 verified agricultural schemes are actively supported in Uttar Pradesh:\n1. PM-KISAN - Rs. 6,000/yr direct income support\n2. PMFBY - Comprehensive natural crop insurance at 1.5%/2% premium\n3. PMKSY-PDMC - 55% capital subsidy for drip & sprinkler micro-irrigation\n4. KCC - Concessional farm credit up to Rs. 3 Lakhs at 4% effective interest\n5. UP Krishak Durghatna Kalyan - Up to Rs. 5 Lakhs ex-gratia accidental death relief\n6. SMAM Machinery - 40% to 50% subsidy on tractors and farm implements.\n\nYou can ask detailed questions regarding any of these schemes.",
                "hinglish": "UP me 6 main verified kisan yojanayein available hain:\n1. PM-KISAN: Saal me ₹6,000 ki income support\n2. PMFBY: Fasal kharab hone par 1.5%/2% premium par poora bima\n3. PMKSY-PDMC: Drip aur sprinkler sinchai par 55% tak ki subsidy\n4. KCC Loan: ₹3 Lakh tak ka loan sirf 4% annual byaj par\n5. UP Krishak Durghatna: Kisan ki accidental death ya disability par ₹5 Lakh relief\n6. SMAM Machinery: Tractor aur krishi yantron par 40-50% subsidy.\n\nAap inme se kisi bhi yojana ke documents, eligibility ya apply karne ka process pooch sakte hain.",
                "pa": "ਉੱਤਰ ਪ੍ਰਦੇਸ਼ ਵਿੱਚ ਕਿਸਾਨਾਂ ਲਈ 6 ਮੁੱਖ ਪ੍ਰਮਾਣਿਤ ਸਕੀਮਾਂ ਉਪਲਬਧ ਹਨ:\n1. ਪੀ.ਐਮ-ਕਿਸਾਨ: ਸਾਲਾਨਾ ₹6,000 ਸਿੱਧੀ ਆਮਦਨ ਸਹਾਇਤਾ\n2. ਪੀ.ਐਮ. ਫ਼ਸਲ ਬੀਮਾ (PMFBY): 1.5%/2% ਪ੍ਰੀਮੀਅਮ 'ਤੇ ਕੁਦਰਤੀ ਆਫ਼ਤ ਸੁਰੱਖਿਆ\n3. ਡ੍ਰਿਪ ਸਿੰਚਾਈ (PMKSY): ਡ੍ਰਿਪ/ਸਪ੍ਰਿੰਕਲਰ 'ਤੇ 55% ਤੱਕ ਸਬਸਿਡੀ\n4. ਕਿਸਾਨ ਕ੍ਰੈਡਿਟ ਕਾਰਡ (KCC): 4% ਵਿਆਜ 'ਤੇ ₹3 ਲੱਖ ਤੱਕ ਕਰਜ਼ਾ\n5. ਮੁੱਖ ਮੰਤਰੀ ਕਿਸਾਨ ਦੁਰਘਟਨਾ ਕਲਿਆਣ: ₹5 ਲੱਖ ਤੱਕ ਹਾਦਸਾ ਰਾਹਤ\n6. ਖੇਤੀ ਮਸ਼ੀਨਰੀ (SMAM): ਟਰੈਕਟਰ ਤੇ ਸੰਦਾਂ 'ਤੇ 40-50% ਸਬਸਿਡੀ।\n\nਤੁਸੀਂ ਕਿਸੇ ਵੀ ਸਕੀਮ ਬਾਰੇ ਹੋਰ ਜਾਣਕਾਰੀ ਪੁੱਛ ਸਕਦੇ ਹੋ।"
            }
            return AssistantQueryResponse(
                answer=schemes_text.get(lang, schemes_text["hi"]),
                source_title="UP Agriculture Official Scheme Portfolio Register",
                authority="Department of Agriculture, Govt of Uttar Pradesh",
                section="Active Statutory Scheme Catalogue",
                verified_at="2026-01-20T10:00:00Z",
                can_verify=True,
                detected_language=lang,
                related_schemes=list(SCHEME_CATALOGUE.keys())
            )

        return _build_unverified_fallback(lang)

    # Scheme is identified
    topic = _identify_topic(q)
    scheme_info = SCHEME_CATALOGUE[target_code]

    # Look up specific grounded topic response
    scheme_kb = KNOWLEDGE_BASE.get(target_code, {})
    if topic in scheme_kb and lang in scheme_kb[topic]:
        content = scheme_kb[topic][lang]
        return AssistantQueryResponse(
            answer=content,
            source_title=scheme_info["source_title"],
            authority=scheme_info["department"],
            section=scheme_info["source_section"],
            verified_at=scheme_info["verified_at"],
            can_verify=True,
            detected_language=lang,
            related_schemes=[target_code]
        )

    # Fallback to general grounded scheme overview in the target language
    return _build_general_scheme_answer(target_code, lang)
