import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.qa_service import answer_scheme_question, detect_or_normalize_language

client = TestClient(app)

def test_language_detection():
    # Explicit language tags
    assert detect_or_normalize_language("anything", "hi") == "hi"
    assert detect_or_normalize_language("anything", "en") == "en"
    assert detect_or_normalize_language("anything", "hinglish") == "hinglish"
    assert detect_or_normalize_language("anything", "pa") == "pa"

    # Gurmukhi script auto-detection
    assert detect_or_normalize_language("ਪੀ.ਐਮ-ਕਿਸਾਨ ਯੋਜਨਾ ਵਿੱਚ ਕਿੰਨੇ ਪੈਸੇ ਮਿਲਦੇ ਹਨ?") == "pa"

    # Devanagari script auto-detection
    assert detect_or_normalize_language("पीएम-किसान में ₹6000 की किस्त कब मिलती है?") == "hi"

    # Hinglish auto-detection
    assert detect_or_normalize_language("pm kisan ka paisa kab aayega aur kyc kaise kare") == "hinglish"

    # English default
    assert detect_or_normalize_language("What is the interest rate for KCC loan?") == "en"


def test_pm_kisan_queries_multilingual():
    # Hindi query
    res_hi = answer_scheme_question("पीएम किसान में कितना पैसा मिलता है?", language="hi")
    assert res_hi.can_verify is True
    assert "₹6,000" in res_hi.answer
    assert "PM_KISAN" in res_hi.related_schemes
    assert res_hi.detected_language == "hi"

    # English query
    res_en = answer_scheme_question("What is the benefit amount under PM-KISAN?", language="en")
    assert res_en.can_verify is True
    assert "6,000" in res_en.answer
    assert res_en.detected_language == "en"

    # Hinglish query
    res_hgl = answer_scheme_question("pm kisan me kitna paisa milega?", language="hinglish")
    assert res_hgl.can_verify is True
    assert "₹6,000" in res_hgl.answer
    assert "installment" in res_hgl.answer or "installments" in res_hgl.answer
    assert res_hgl.detected_language == "hinglish"

    # Punjabi query
    res_pa = answer_scheme_question("ਪੀ.ਐਮ-ਕਿਸਾਨ ਯੋਜਨਾ ਵਿੱਚ ਕਿੰਨੇ ਪੈਸੇ ਮਿਲਦੇ ਹਨ?", language="pa")
    assert res_pa.can_verify is True
    assert "₹6,000" in res_pa.answer
    assert res_pa.detected_language == "pa"


def test_pmfby_72_hour_rule():
    # Test critical 72-hour crop loss intimation rule
    query_hi = "फसल नुकसान होने पर बीमा क्लेम की समय सीमा क्या है?"
    res = answer_scheme_question(query_hi, language="hi")
    assert res.can_verify is True
    assert "72 घंटे" in res.answer or "७२ घंटे" in res.answer
    assert "PMFBY" in res.related_schemes

    query_hgl = "fasal kharab ho gayi to claim kitne samay me kare"
    res_hgl = answer_scheme_question(query_hgl, language="hinglish")
    assert res_hgl.can_verify is True
    assert "72 ghante" in res_hgl.answer.lower() or "72" in res_hgl.answer


def test_kcc_loan_terms():
    query_en = "What is the interest rate and limit for KCC credit card?"
    res_en = answer_scheme_question(query_en, language="en")
    assert res_en.can_verify is True
    assert "4%" in res_en.answer
    assert "3,00,000" in res_en.answer or "300000" in res_en.answer

    query_pa = "ਕੇਸੀਸੀ ਕਰਜ਼ੇ ਉੱਤੇ ਵਿਆਜ ਦਰ ਕਿੰਨੀ ਹੈ?"
    res_pa = answer_scheme_question(query_pa, language="pa")
    assert res_pa.can_verify is True
    assert "4%" in res_pa.answer


def test_up_krishak_durghatna_clarification():
    # Durghatna is a one-time ex-gratia relief of 5 Lakhs, not an ongoing pension
    res_hi = answer_scheme_question("दुर्घटना कल्याण योजना में क्या लाभ मिलता है?", language="hi")
    assert res_hi.can_verify is True
    assert "₹5,00,000" in res_hi.answer
    assert "पेंशन नहीं" in res_hi.answer or "एकमुश्त" in res_hi.answer

    res_en = answer_scheme_question("Does Krishak Durghatna provide a monthly pension or one-time relief?", language="en")
    assert res_en.can_verify is True
    assert "5,00,000" in res_en.answer
    assert "NOT an ongoing monthly pension" in res_en.answer or "One-time" in res_en.answer


def test_convergence_combination():
    # Can PM-KISAN, KCC, and PMFBY be availed together?
    res_hgl = answer_scheme_question("kya pm kisan aur kcc dono ek saath le sakte hain?", language="hinglish")
    assert res_hgl.can_verify is True
    assert "teeno ek saath" in res_hgl.answer or "multiple schemes" in res_hgl.answer or "ek saath" in res_hgl.answer
    assert "PM_KISAN" in res_hgl.related_schemes


def test_out_of_domain_safeguard():
    # Query about cryptocurrency / stocks / non-existent schemes
    res = answer_scheme_question("How do I invest in Bitcoin cryptocurrency?", language="en")
    assert res.can_verify is False
    assert "not covered by verified government agricultural gazettes" in res.answer


def test_assistant_api_endpoint():
    # Test the FastAPI endpoint directly with multilingual payloads
    payload = {
        "query": "Drip sinchai par kitna anudan milta hai?",
        "language": "hinglish"
    }
    response = client.post("/api/v1/assistant/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["can_verify"] is True
    assert "55%" in data["answer"]
    assert data["authority"] is not None
    assert data["source_title"] is not None

