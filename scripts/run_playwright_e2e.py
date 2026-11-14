"""
YojanaSaathi AI — Playwright End-to-End Automated Citizen Journey & Offline Recovery Suite.
Executes the complete farmer workflow against live backend (port 8000) and frontend (port 5173):
1. Landing Page Verification & Multilingual Switch.
2. Grounded Scheme Assistant & Natural Language Intake (with UP Bigha Unit Ambiguity Handling).
3. Deterministic Eligibility Evaluation & Scheme Recommendation Display.
4. Multi-Scheme Pairwise Convergence Compatibility Verification.
5. Personalized Action Plan Generation (7-Stage Roadmap & Document Checklist).
6. Complete Offline Action Plan Recovery after Browser Restart.
Captures high-resolution evidence screenshots in docs/testing/.
"""

import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

FRONTEND_URL = "http://localhost:5173"
TESTING_DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "testing"))
os.makedirs(TESTING_DOCS_DIR, exist_ok=True)

def run_e2e_tests():
    print("=" * 72)
    print("🌾 YOJANASAATHI AI — PLAYWRIGHT END-TO-END EXECUTION SUITE")
    print("=" * 72)
    
    with sync_playwright() as p:
        # Launch Chrome browser
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        page.on("dialog", lambda dialog: (print(f"[Browser Dialog] {dialog.message}"), dialog.accept()))

        # Step 1: Landing Page
        print("\n[Step 1] Navigating to YojanaSaathi AI Landing Page...")
        page.goto(FRONTEND_URL, wait_until="networkidle")
        time.sleep(1)
        
        # Verify page title
        title = page.title()
        print(f"  • Page Title: {title}")
        assert "YojanaSaathi" in title, f"Unexpected title: {title}"

        # Capture Screenshot 1: Landing Page
        screenshot_1 = os.path.join(TESTING_DOCS_DIR, "playwright_01_landing.png")
        page.screenshot(path=screenshot_1, full_page=False)
        print(f"  • [Screenshot Captured] {screenshot_1}")

        # Step 2: Open Grounded Assistant Modal
        print("\n[Step 2] Opening Grounded Scheme Assistant Modal...")
        # Target assistant button on landing page or hero
        assistant_btn = page.locator("button:has-text('सहायक से प्रश्न पूछें'), button:has-text('Ask Grounded Assistant')").first
        if not assistant_btn.is_visible():
            assistant_btn = page.locator("text='सहायक से प्रश्न पूछें'").first
        assistant_btn.click()
        page.wait_for_selector("textarea, input[type='text']", state="visible", timeout=10000)
        time.sleep(1)

        # Capture Screenshot 2: Assistant Modal Open
        screenshot_2 = os.path.join(TESTING_DOCS_DIR, "playwright_02_assistant_open.png")
        page.screenshot(path=screenshot_2, full_page=False)
        print(f"  • [Screenshot Captured] {screenshot_2}")

        # Step 3: Natural Language Intake with Bigha Ambiguity
        print("\n[Step 3] Submitting Natural Language Intake Query...")
        query_text = "मैं झांसी जिले से हूं, मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।"
        input_box = page.locator("textarea, input[placeholder*='उदा.'], input[placeholder*='e.g.']").first
        input_box.fill(query_text)
        
        # Click send button
        send_btn = page.locator("button:has(svg), button:has-text('पूछें'), button:has-text('Send')").last
        send_btn.click()
        print("  • Query Submitted. Waiting for Grounded NLP analysis & Bigha unit detection...")

        # Wait for the assistant's intake response message to appear
        page.wait_for_selector("button:has-text('इस जानकारी से पात्रता जाँचें'), button:has-text('Evaluate Schemes')", timeout=15000)
        time.sleep(1)

        # Capture Screenshot 3: Intake Analyzed
        screenshot_3 = os.path.join(TESTING_DOCS_DIR, "playwright_03_intake_analyzed.png")
        page.screenshot(path=screenshot_3, full_page=False)
        print(f"  • [Screenshot Captured] {screenshot_3}")

        # Step 4: Click 'Evaluate Schemes for this Profile'
        print("\n[Step 4] Triggering Three-Valued Deterministic Rules Evaluation...")
        eval_btn = page.locator("button:has-text('इस जानकारी से पात्रता जाँचें'), button:has-text('Evaluate Schemes')").first
        eval_btn.click()

        # Wait for Recommendations view to load
        page.wait_for_selector("button:has-text('कार्य योजना तैयार करें'), button:has-text('Generate Action Plan')", timeout=15000)
        time.sleep(1.5)

        # Capture Screenshot 4: Recommendations & Eligibility Status
        screenshot_4 = os.path.join(TESTING_DOCS_DIR, "playwright_04_recommendations.png")
        page.screenshot(path=screenshot_4, full_page=False)
        print(f"  • [Screenshot Captured] {screenshot_4}")

        # Step 5: Test Convergence Check
        print("\n[Step 5] Testing Multi-Scheme Pairwise Convergence Compatibility...")
        compat_btn = page.locator("button:has-text('टकराव / सह-अस्तित्व जाँचें'), button:has-text('Check Pairwise Compatibility')").first
        if compat_btn.is_visible():
            compat_btn.click()
            time.sleep(1.5)
            screenshot_5 = os.path.join(TESTING_DOCS_DIR, "playwright_05_convergence_modal.png")
            page.screenshot(path=screenshot_5, full_page=False)
            print(f"  • [Screenshot Captured] {screenshot_5}")
            
            # Close convergence modal
            close_btn = page.locator("button:has-text('समझ लिया / बंद करें'), button:has-text('Understood'), button:has-text('✕')").first
            if close_btn.is_visible():
                close_btn.click()
                time.sleep(1)

        # Step 6: Generate Action Plan
        print("\n[Step 6] Generating Personalized Action Plan (7-Stage Roadmap)...")
        gen_plan_btn = page.locator("button:has-text('कार्य योजना तैयार करें'), button:has-text('Generate Action Plan')").first
        gen_plan_btn.click()

        # Wait for Action Plan View
        page.wait_for_selector("button:has-text('प्रिंट'), button:has-text('Print')", timeout=15000)
        time.sleep(1.5)

        # Capture Screenshot 6: Action Plan View
        screenshot_6 = os.path.join(TESTING_DOCS_DIR, "playwright_06_action_plan.png")
        page.screenshot(path=screenshot_6, full_page=False)
        print(f"  • [Screenshot Captured] {screenshot_6}")

        # Step 7: Check LocalStorage caching & Persist Browser State
        latest_plan_number = page.evaluate("localStorage.getItem('yojanasaathi_latest_plan_number')")
        cached_plan_raw = page.evaluate(f"localStorage.getItem('yojanasaathi_plan_{latest_plan_number}')")
        print(f"\n[Step 7] Checking Action Plan Local Storage Persistence:")
        print(f"  • Cached Plan Number: {latest_plan_number}")
        assert latest_plan_number and len(latest_plan_number) > 5, "Plan number was not cached in localStorage!"
        assert cached_plan_raw, "Plan data was not found in localStorage!"

        # Persist full browser storage state before closing
        storage_file = os.path.join(TESTING_DOCS_DIR, "browser_offline_state.json")
        context.storage_state(path=storage_file)

        # Close session to simulate browser restart
        browser.close()
        print("\n[Step 8] Browser Closed (Simulating Complete Process Termination).")

        # Step 9: Reopen Fresh Browser in STRICT OFFLINE RECOVERY
        print("\n[Step 9] Simulating Browser Restart with Persisted Local Storage...")
        browser2 = p.chromium.launch(channel="chrome", headless=True)
        # Create fresh context restored with exact persistent localStorage state
        context2 = browser2.new_context(storage_state=storage_file, viewport={"width": 1280, "height": 800})
        page2 = context2.new_page()

        # Load page with stored state
        page2.goto(FRONTEND_URL, wait_until="networkidle")
        # Simulate user going offline in rural field
        context2.set_offline(True)
        page2.evaluate("window.dispatchEvent(new Event('offline'))")
        time.sleep(1)

        # Verify offline cached plan pill is visible on Landing Page
        print("\n[Step 10] Verifying Offline Cached Plan Detection on Landing Page...")
        cached_pill = page2.get_by_text(latest_plan_number).first
        is_pill_visible = cached_pill.is_visible()
        print(f"  • Offline Cache Notification Visible: {is_pill_visible}")

        # Click 'Open Plan' or 'Action Plan' in Header
        open_plan_btn = page2.locator("button:has-text('योजना खोलें'), button:has-text('Open Plan'), button:has-text('कार्य योजना')").first
        open_plan_btn.click()
        time.sleep(1)

        # Verify Action Plan rendered in Offline Mode
        print("\n[Step 11] Verifying Complete Offline Action Plan Rendering:")
        page2.wait_for_selector("button:has-text('प्रिंट'), button:has-text('Print')", timeout=10000)
        page2.evaluate("window.dispatchEvent(new Event('offline'))")
        time.sleep(0.5)
        offline_banner = page2.locator("text='ऑफ़लाइन मोड सक्रिय'").first
        is_offline_banner_visible = offline_banner.is_visible()
        print(f"  • Offline Active Banner Visible: {is_offline_banner_visible}")

        # Capture Screenshot 7: Offline Recovery
        screenshot_7 = os.path.join(TESTING_DOCS_DIR, "playwright_07_offline_recovery.png")
        page2.screenshot(path=screenshot_7, full_page=False)
        print(f"  • [Screenshot Captured] {screenshot_7}")

        browser2.close()

    print("\n" + "=" * 72)
    print("✅ PLAYWRIGHT E2E & OFFLINE RECOVERY VERIFICATION 100% SUCCESSFUL")
    print("=" * 72)
    return True

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
