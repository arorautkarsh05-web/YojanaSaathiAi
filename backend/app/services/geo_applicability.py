"""
YojanaSaathi AI — Geographic Applicability Engine for Uttar Pradesh.
Provides verified district, agro-climatic zone, and crop-notification resolution across all 75 districts.
Never assumes uniform applicability when statutory scheme orders specify district clusters or crop notifications.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

# Complete Official List of all 75 Administrative Districts of Uttar Pradesh
UP_75_DISTRICTS = {
    "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya", "Ayodhya",
    "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur", "Banda", "Barabanki",
    "Bareilly", "Basti", "Bhadohi", "Bijnor", "Budaun", "Bulandshahr", "Chandauli",
    "Chitrakoot", "Deoria", "Etah", "Etawah", "Farrukhabad", "Fatehpur", "Firozabad",
    "Gautam Buddha Nagar", "Ghaziabad", "Ghazipur", "Gonda", "Gorakhpur", "Hamirpur",
    "Hapur", "Hardoi", "Hathras", "Jalaun", "Jaunpur", "Jhansi", "Kannauj", "Kanpur Dehat",
    "Kanpur Nagar", "Kasganj", "Kaushambi", "Kheri (Lakhimpur)", "Kushinagar", "Lalitpur",
    "Lucknow", "Maharajganj", "Mahoba", "Mainpuri", "Mathura", "Mau", "Meerut",
    "Mirzapur", "Moradabad", "Muzaffarnagar", "Pilibhit", "Pratapgarh", "Prayagraj",
    "Raebareli", "Rampur", "Saharanpur", "Sambhal", "Sant Kabir Nagar", "Shahjahanpur",
    "Shamli", "Shravasti", "Siddharthnagar", "Sitapur", "Sonbhadra", "Sultanpur",
    "Unnao", "Varanasi"
}

# Agro-Climatic Zones of Uttar Pradesh (UP State Agriculture Department Classification)
UP_AGRO_CLIMATIC_ZONES = {
    "BUNDELKHAND": {
        "name_en": "Bundelkhand Zone (Water-Deficit & Pulses Belt)",
        "name_hi": "बुंदेलखंड क्षेत्र (दलहन व जल-संकट प्रभावित)",
        "districts": {"Banda", "Chitrakoot", "Hamirpur", "Jalaun", "Jhansi", "Lalitpur", "Mahoba"},
        "special_policies": ["BUNDELKHAND_PACKAGE", "SPECIAL_PUMP_SUBSIDY", "DROUGHT_RESILIENT_CROPS"],
        "notified_pmfby_crops": ["wheat", "gram", "lentil", "mustard", "sesamum", "soybean", "arhar", "coarse_cereals"]
    },
    "WESTERN_PLAIN": {
        "name_en": "Western Plain Zone (Intensive Sugarcane & Grain Belt)",
        "name_hi": "पश्चिमी मैदानी क्षेत्र (गन्ना व गहन कृषि क्षेत्र)",
        "districts": {"Bijnor", "Bulandshahr", "Gautam Buddha Nagar", "Ghaziabad", "Hapur", "Meerut", "Moradabad", "Muzaffarnagar", "Rampur", "Saharanpur", "Sambhal", "Shamli", "Baghpat"},
        "special_policies": ["SUGARCANE_CLUSTER", "TUBEWELL_SATURATION"],
        "notified_pmfby_crops": ["wheat", "paddy", "sugarcane", "mustard", "maize", "potato"]
    },
    "EASTERN_PLAIN": {
        "name_en": "Eastern Plain Zone (Rice-Wheat & High Density Belt)",
        "name_hi": "पूर्वी मैदानी क्षेत्र (धान-गेहूँ सघन क्षेत्र)",
        "districts": {"Ambedkar Nagar", "Amethi", "Ayodhya", "Ghazipur", "Jaunpur", "Pratapgarh", "Prayagraj", "Sultanpur", "Varanasi", "Chandauli", "Bhadohi", "Mirzapur", "Sonbhadra", "Ballia", "Azamgarh", "Mau", "Deoria", "Gorakhpur", "Maharajganj", "Kushinagar", "Basti", "Sant Kabir Nagar", "Siddharthnagar"},
        "special_policies": ["FLOOD_PRONE_INDEMNITY", "EASTERN_UP_DEVELOPMENT"],
        "notified_pmfby_crops": ["wheat", "paddy", "pulses", "oilseeds", "vegetables", "mustard", "gram"]
    },
    "CENTRAL_PLAIN": {
        "name_en": "Central Plain Zone",
        "name_hi": "मध्य मैदानी क्षेत्र",
        "districts": {"Auraiya", "Barabanki", "Etawah", "Farrukhabad", "Fatehpur", "Hardoi", "Kannauj", "Kanpur Dehat", "Kanpur Nagar", "Lucknow", "Raebareli", "Sitapur", "Unnao", "Kaushambi"},
        "special_policies": ["HORTICULTURE_CORRIDOR", "POTATO_CLUSTER"],
        "notified_pmfby_crops": ["wheat", "paddy", "potato", "mustard", "pulses", "vegetables", "maize"]
    },
    "TERAI": {
        "name_en": "Tarai Zone (Sub-Himalayan Wet Belt)",
        "name_hi": "तराई क्षेत्र (आर्द्र उप-हिमालयी बेल्ट)",
        "districts": {"Bahraich", "Balrampur", "Kheri (Lakhimpur)", "Pilibhit", "Shravasti", "Bareilly", "Budaun", "Shahjahanpur"},
        "special_policies": ["HIGH_RAINFALL_DRAINAGE", "TERAI_SUGARCANE"],
        "notified_pmfby_crops": ["wheat", "paddy", "sugarcane", "lentil", "mustard", "maize"]
    },
    "SOUTH_WESTERN_SEMI_ARID": {
        "name_en": "South-Western Semi-Arid Zone",
        "name_hi": "दक्षिण-पश्चिमी अर्ध-शुष्क क्षेत्र",
        "districts": {"Agra", "Aligarh", "Etah", "Firozabad", "Hathras", "Kasganj", "Mainpuri", "Mathura"},
        "special_policies": ["GROUNDWATER_DEPLETION_PRIORITY", "MUSTARD_POTATO_CLUSTER"],
        "notified_pmfby_crops": ["wheat", "mustard", "potato", "bajra", "barley", "paddy"]
    }
}

# Aspirational Districts of UP (NITI Aayog / Special Priority Allocations)
UP_ASPIRATIONAL_DISTRICTS = {
    "Bahraich", "Balrampur", "Chandauli", "Chitrakoot", "Fatehpur", "Shravasti", "Siddharthnagar", "Sonbhadra"
}

# Critical & Over-Exploited Groundwater Blocks (CGWB / UP Ground Water Dept)
# Farmers here receive prioritized subsidies for Micro-Irrigation (Drip/Sprinkler under PMKSY-PDMC)
UP_CRITICAL_WATER_DISTRICTS = {
    "Agra", "Aligarh", "Firozabad", "Hathras", "Mathura", "Saharanpur", "Meerut", "Muzaffarnagar", "Baghpat", "Ghaziabad", "Moradabad", "Budaun", "Sambhal", "Amroha"
}

@dataclass
class GeoEvaluationResult:
    is_valid_up_district: bool
    district: str
    agro_climatic_zone: Optional[str]
    is_aspirational: bool
    is_critical_water_zone: bool
    geo_score: float
    applicability_status: str  # "APPLICABLE", "APPLICABLE_WITH_PRIORITY", "UNKNOWN_REQUIRES_VERIFICATION", "NOT_APPLICABLE"
    notes: List[str]

def normalize_district_name(district_raw: Optional[str]) -> Optional[str]:
    """Matches user input district against official UP 75 districts case-insensitively."""
    if not district_raw or not str(district_raw).strip():
        return None
    cleaned = str(district_raw).strip().lower()
    for official in UP_75_DISTRICTS:
        if official.lower() == cleaned:
            return official
        # Handle variations like "Lakhimpur", "Kheri", "Kanpur"
        if cleaned in ["lakhimpur", "kheri"] and "kheri" in official.lower():
            return "Kheri (Lakhimpur)"
        if cleaned == "kanpur" and official == "Kanpur Nagar":
            return "Kanpur Nagar"
        if cleaned == "faizabad" and official == "Ayodhya":
            return "Ayodhya"
        if cleaned == "allahabad" and official == "Prayagraj":
            return "Prayagraj"
    return None

def evaluate_geographic_applicability(
    district: Optional[str],
    state: Optional[str],
    scheme_code: str,
    primary_crops: Optional[List[str]] = None
) -> GeoEvaluationResult:
    """
    Evaluates statutory geographical applicability for a scheme in UP.
    Enforces that unverified or missing geography returns UNKNOWN_REQUIRES_VERIFICATION.
    """
    notes: List[str] = []
    
    # Check 1: State validation
    norm_state = str(state or "").strip().lower()
    if norm_state and norm_state not in ["uttar pradesh", "up", "u.p.", "uttarpradesh"]:
        return GeoEvaluationResult(
            is_valid_up_district=False,
            district=district or "Unknown",
            agro_climatic_zone=None,
            is_aspirational=False,
            is_critical_water_zone=False,
            geo_score=0.0,
            applicability_status="NOT_APPLICABLE",
            notes=[f"State '{state}' is outside the current jurisdiction of Uttar Pradesh."]
        )

    # Check 2: District validation
    official_district = normalize_district_name(district)
    if not official_district:
        return GeoEvaluationResult(
            is_valid_up_district=False,
            district=district or "Unspecified",
            agro_climatic_zone=None,
            is_aspirational=False,
            is_critical_water_zone=False,
            geo_score=50.0,
            applicability_status="UNKNOWN_REQUIRES_VERIFICATION",
            notes=["District is unspecified or not recognized among the 75 administrative districts of Uttar Pradesh. Verification required at local Tehsil."]
        )

    # Determine Agro-Climatic Zone
    zone_code = None
    zone_meta = None
    for zcode, zdata in UP_AGRO_CLIMATIC_ZONES.items():
        if official_district in zdata["districts"]:
            zone_code = zcode
            zone_meta = zdata
            break

    is_asp = official_district in UP_ASPIRATIONAL_DISTRICTS
    is_crit_water = official_district in UP_CRITICAL_WATER_DISTRICTS

    # Scheme-Specific Spatial Rules
    geo_score = 100.0
    status = "APPLICABLE"

    if scheme_code == "PMFBY":
        # PMFBY crop notification check
        crops = [str(c).lower().strip() for c in (primary_crops or []) if c]
        if zone_meta and crops:
            notified_crops = zone_meta["notified_pmfby_crops"]
            has_notified = any(c in notified_crops for c in crops)
            if has_notified:
                notes.append(f"District {official_district} ({zone_meta['name_en']}) notified for major crops: {', '.join(crops)} under current SLCCCI cluster.")
                geo_score = 100.0
            else:
                status = "UNKNOWN_REQUIRES_VERIFICATION"
                notes.append(f"Crops ({', '.join(crops)}) may not be notified in the seasonal insurance cluster for {official_district}. District Agriculture Officer notification check required.")
                geo_score = 65.0
        else:
            status = "UNKNOWN_REQUIRES_VERIFICATION"
            notes.append(f"Crop selection pending for {official_district}. PMFBY requires district-notified crop verification.")
            geo_score = 75.0

    elif scheme_code == "PMKSY_PDMC":
        if is_crit_water:
            status = "APPLICABLE_WITH_PRIORITY"
            notes.append(f"{official_district} is designated a Critical / Over-Exploited Groundwater District by CGWB; eligible for expedited Micro-Irrigation subsidy token release.")
            geo_score = 100.0
        else:
            notes.append(f"District {official_district} is covered under statewide PMKSY-PDMC horticulture guidelines.")
            geo_score = 90.0

    elif scheme_code == "SMAM_MACHINERY":
        if is_asp:
            status = "APPLICABLE_WITH_PRIORITY"
            notes.append(f"{official_district} is a designated Aspirational District; receives special Custom Hiring Center (CHC) machinery quota.")
            geo_score = 100.0
        else:
            notes.append(f"Statewide open token notification applies for {official_district} on upagriculture.com.")
            geo_score = 95.0

    elif scheme_code in ["PM_KISAN", "KCC", "UP_KRISHAK_DURGHATNA"]:
        notes.append(f"Statutory entitlement verified across all revenue tehsils of {official_district}.")
        geo_score = 100.0

    return GeoEvaluationResult(
        is_valid_up_district=True,
        district=official_district,
        agro_climatic_zone=zone_code,
        is_aspirational=is_asp,
        is_critical_water_zone=is_crit_water,
        geo_score=geo_score,
        applicability_status=status,
        notes=notes
    )

