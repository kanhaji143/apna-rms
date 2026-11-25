#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
APNA COMPUTER RMS — VENDOR MASTER LICENSE KEY GENERATOR (PRIVATE & CONFIDENTIAL)
Platform Owner & Developer: APNA Computer (कृष्णा जी) | Helpline: 8504985149
================================================================================
Use this tool to generate 10-day/15-day extension keys, annual licenses, and lifetime keys
for any client coaching or institute computer.
================================================================================
"""

import sys
import os
import hashlib

SALT = "APNA_COMPUTER_RMS_8504985149"

DURATION_OPTIONS = {
    "1": (365, "1 वर्ष (365 दिन) — वार्षिक एक्टिवेशन लाइसेंस (Annual License)"),
    "2": (3650, "आजीवन / 10 वर्ष (Lifetime Commercial License — पूर्ण परमानेंट एक्टिवेशन)"),
    "3": (15, "15 दिन एक्सटेंशन (अधिकतम 15 दिन अतिरिक्त VIP ट्रायल — New Batch Demo)"),
    "4": (30, "30 दिन VIP ट्रायल (30 दिन अतिरिक्त VIP ट्रायल)"),
    "5": (730, "2 वर्ष (730 दिन) — द्वि-वार्षिक लाइसेंस"),
    "6": (1095, "3 वर्ष (1095 दिन) — त्रि-वार्षिक लाइसेंस")
}

def generate_key(installation_id: str, validity_days: int) -> str:
    clean_id = installation_id.strip().upper()
    raw = f"{clean_id}_{validity_days}_{SALT}"
    h = hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()
    return f"APNA-{h[:4]}-{h[4:8]}-{h[8:12]}"

def main():
    print("=" * 72)
    print("  🔑 APNA COMPUTER RMS — मास्टर लाइसेंस व एक्सटेंशन की जनरेटर")
    print("  अधिकृत वेंडर: APNA Computer (कृष्णा जी) | हेल्पलाइन: 8504985149")
    print("  गोपनीय: केवल वेंडर के निजी उपयोग हेतु (Confidential)")
    print("=" * 72)
    print()

    if len(sys.argv) > 1:
        install_id = sys.argv[1].strip()
    else:
        install_id = input("👉 क्लाइंट कंप्यूटर की Installation ID दर्ज करें (उदा. ACR-8542): ").strip()

    if not install_id:
        print("❌ त्रुटि: Installation ID दर्ज करना अनिवार्य है!")
        return

    print()
    print("लाइसेंस / एक्सटेंशन अवधि चुनें (Select Validity Duration):")
    for k, (days, label) in DURATION_OPTIONS.items():
        print(f"  [{k}] {label}")
    print()

    choice = input("विकल्प चुनें [1-6, डिफ़ॉल्ट 1]: ").strip()
    if not choice:
        choice = "1"

    days, label = DURATION_OPTIONS.get(choice, (365, "1 वर्ष (365 दिन) — वार्षिक एक्टिवेशन लाइसेंस"))
    key = generate_key(install_id, days)

    print()
    print("=" * 72)
    print("  ✅ जनरेट की गई आधिकारिक मास्टर की (Key):")
    print("  " + "-" * 56)
    print(f"  🔑 {key}")
    print("  " + "-" * 56)
    print(f"  🏢 क्लाइंट Installation ID : {install_id.upper()}")
    print(f"  ⏳ लाइसेंस वैधता           : {label}")
    print(f"  ⚡ यूनिवर्सल वेंडर मास्टर कोड : APNA8504985149")
    print("=" * 72)
    print()
    print("📋 WhatsApp शेयर मैसेज:")
    print("-" * 72)
    msg = (
        f"नमस्ते! APNA Computer RMS सॉफ़्टवेयर को सक्रिय करने हेतु आपकी आधिकारिक की है:\n\n"
        f"🔑 {key}\n\n"
        f"वैधता: {label}\n"
        f"Installation ID: {install_id.upper()}\n\n"
        f"सॉफ़्टवेयर में 'लाइसेंस की दर्ज करें' बॉक्स में पेस्ट करके सक्रिय करें।\n"
        f"हेल्पलाइन: 8504985149 (APNA Computer)"
    )
    print(msg)
    print("-" * 72)
    print()

if __name__ == '__main__':
    main()
