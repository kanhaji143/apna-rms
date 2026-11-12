import os
import re
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
import tkinter.filedialog as fd
import customtkinter as ctk
from PIL import Image
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    load_config
)
from core.translations import t
from core.database import DatabaseManager
from core.image_utils import ImageOptimizer
from core.receipt_generator import ReceiptGenerator

class AdmissionView(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_record_saved_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.on_record_saved = on_record_saved_callback
        self.config = load_config()

        self.selected_screenshot_path = ""
        self.selected_courses = []
        self.course_checkboxes = {}
        self.admission_source = "Telecalling"

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")
        db = DatabaseManager.get_instance()

        # Responsive Scrollable Container (fits any screen resolution perfectly)
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8, pady=4)

        # Header Bar with Source Pills
        top_bar = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1",
            height=48
        )
        top_bar.pack(fill="x", padx=4, pady=(0, 6))

        title_lbl = ctk.CTkLabel(
            top_bar,
            text=f"📝 {t('adm_title', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        )
        title_lbl.pack(side="left", padx=14, pady=8)

        # Source Toggle Pills: [ 📞 Telecalling | 🏢 Direct Walk-in ]
        source_frame = ctk.CTkFrame(top_bar, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, corner_radius=14)
        source_frame.pack(side="right", padx=10, pady=8)

        self.btn_src_tele = ctk.CTkButton(
            source_frame,
            text=t("adm_mode_telecalling", lang),
            height=26,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color=COLOR_CYAN,
            text_color="#001633",
            hover_color=COLOR_CYAN_HOVER,
            command=lambda: self.set_source("Telecalling")
        )
        self.btn_src_tele.pack(side="left", padx=2, pady=2)

        self.btn_src_walk = ctk.CTkButton(
            source_frame,
            text=t("adm_mode_walkin", lang),
            height=26,
            corner_radius=12,
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            fg_color="transparent",
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK,
            hover_color=COLOR_CYAN_HOVER,
            command=lambda: self.set_source("Walk-in")
        )
        self.btn_src_walk.pack(side="left", padx=2, pady=2)

        # Warning Banner (Dynamic)
        self.warning_banner = ctk.CTkLabel(
            scroll,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_WARNING,
            wraplength=800
        )
        self.warning_banner.pack(anchor="w", padx=10, pady=(0, 2))

        # TWO-COLUMN COMPACT RESPONSIVE CONTAINER
        columns_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=2, pady=2)
        columns_frame.grid_columnconfigure(0, weight=1)
        columns_frame.grid_columnconfigure(1, weight=1)

        # =========================================================================
        # LEFT COLUMN: Student Details + Course Selection
        # =========================================================================
        col_left = ctk.CTkFrame(
            columns_frame,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        col_left.grid(row=0, column=0, sticky="nsew", padx=4, pady=2)

        # --- Section 1: Student Information ---
        ctk.CTkLabel(
            col_left,
            text="👤 1. छात्र का विवरण (Student Information)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=12, pady=(8, 4))

        s1_grid = ctk.CTkFrame(col_left, fg_color="transparent")
        s1_grid.pack(fill="x", padx=10, pady=(0, 6))

        # Name
        ctk.CTkLabel(s1_grid, text="Student Name *:", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, sticky="w", pady=2, padx=4)
        self.name_entry = ctk.CTkEntry(s1_grid, height=30, placeholder_text="पूरा नाम दर्ज करें", font=ctk.CTkFont(size=11))
        self.name_entry.grid(row=0, column=1, columnspan=3, sticky="ew", pady=2, padx=4)

        # Phone
        ctk.CTkLabel(s1_grid, text="Phone (10 Digits) *:", font=ctk.CTkFont(size=10, weight="bold")).grid(row=1, column=0, sticky="w", pady=2, padx=4)
        self.phone_entry = ctk.CTkEntry(s1_grid, height=30, placeholder_text="10 अंकों का मोबाइल नंबर", font=ctk.CTkFont(size=11))
        self.phone_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=4)
        self.phone_entry.bind("<KeyRelease>", self.sanitize_phone)

        # Date
        ctk.CTkLabel(s1_grid, text="Date (YYYY-MM-DD) *:", font=ctk.CTkFont(size=10, weight="bold")).grid(row=1, column=2, sticky="w", pady=2, padx=4)
        self.date_entry = ctk.CTkEntry(s1_grid, height=30, placeholder_text="YYYY-MM-DD", font=ctk.CTkFont(size=11))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=3, sticky="ew", pady=2, padx=4)
        self.date_entry.bind("<KeyRelease>", self.validate_date_field)

        # Email
        ctk.CTkLabel(s1_grid, text="Email Address *:", font=ctk.CTkFont(size=10, weight="bold")).grid(row=2, column=0, sticky="w", pady=2, padx=4)
        self.email_entry = ctk.CTkEntry(s1_grid, height=30, placeholder_text="student@email.com", font=ctk.CTkFont(size=11))
        self.email_entry.grid(row=2, column=1, columnspan=3, sticky="ew", pady=2, padx=4)
        self.email_entry.bind("<KeyRelease>", self.on_contact_changed)

        s1_grid.grid_columnconfigure((1, 3), weight=1)

        # --- Section 2: Course Selection ---
        ctk.CTkLabel(
            col_left,
            text=f"📚 2. {t('field_courses', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=12, pady=(6, 2))

        courses_box = ctk.CTkFrame(col_left, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, corner_radius=8)
        courses_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        available_courses = db.get_courses()
        for idx, c_name in enumerate(available_courses):
            r = idx // 2
            c = idx % 2
            var = ctk.BooleanVar(value=False)
            chk = ctk.CTkCheckBox(
                courses_box,
                text=c_name,
                variable=var,
                font=ctk.CTkFont(size=10),
                border_color=COLOR_CYAN,
                fg_color=COLOR_CYAN,
                checkmark_color="#001633",
                checkbox_height=18,
                checkbox_width=18
            )
            chk.grid(row=r, column=c, sticky="w", padx=6, pady=2)
            self.course_checkboxes[c_name] = var
            courses_box.grid_columnconfigure((0, 1), weight=1)

        # =========================================================================
        # RIGHT COLUMN: Fees, Concessions, Screenshot & Submit Action
        # =========================================================================
        col_right = ctk.CTkFrame(
            columns_frame,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        col_right.grid(row=0, column=1, sticky="nsew", padx=4, pady=2)

        # --- Section 3: Fees & Payment ---
        ctk.CTkLabel(
            col_right,
            text="💵 3. फीस, भुगतान व रियायत (Payment & Concession)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w", padx=12, pady=(8, 4))

        s3_grid = ctk.CTkFrame(col_right, fg_color="transparent")
        s3_grid.pack(fill="x", padx=10, pady=(0, 6))

        # Payment Mode
        ctk.CTkLabel(s3_grid, text="Payment Mode:", font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=0, sticky="w", pady=2, padx=4)
        self.mode_option = ctk.CTkOptionMenu(
            s3_grid,
            values=["UPI QR", "Cash / नकद", "Card Swipe", "Net Banking", "Cheque"],
            height=30,
            font=ctk.CTkFont(size=11),
            fg_color=COLOR_NAVY_CARD if is_dark else "#FFFFFF",
            button_color=COLOR_CYAN,
            button_hover_color=COLOR_CYAN_HOVER,
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK,
            command=self.on_payment_mode_changed
        )
        self.mode_option.grid(row=0, column=1, sticky="ew", pady=2, padx=4)

        # Account / Beneficiary
        self.acc_label = ctk.CTkLabel(s3_grid, text="Account / नाम *:", font=ctk.CTkFont(size=10, weight="bold"))
        self.acc_label.grid(row=0, column=2, sticky="w", pady=2, padx=4)
        self.acc_entry = ctk.CTkEntry(s3_grid, height=30, placeholder_text="APNA Center / HDFC", font=ctk.CTkFont(size=11))
        self.acc_entry.grid(row=0, column=3, sticky="ew", pady=2, padx=4)

        # Standard Fee
        ctk.CTkLabel(s3_grid, text="Standard Fee (₹):", font=ctk.CTkFont(size=10)).grid(row=1, column=0, sticky="w", pady=2, padx=4)
        self.orig_fee_entry = ctk.CTkEntry(s3_grid, height=30, placeholder_text="0", font=ctk.CTkFont(size=11))
        self.orig_fee_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=4)
        self.orig_fee_entry.bind("<KeyRelease>", self.on_fee_changed)

        # Concession / Discount
        ctk.CTkLabel(s3_grid, text="Concession (₹):", font=ctk.CTkFont(size=10)).grid(row=1, column=2, sticky="w", pady=2, padx=4)
        self.disc_entry = ctk.CTkEntry(s3_grid, height=30, placeholder_text="0", font=ctk.CTkFont(size=11))
        self.disc_entry.grid(row=1, column=3, sticky="ew", pady=2, padx=4)
        self.disc_entry.bind("<KeyRelease>", self.on_fee_changed)

        # Concession Reason
        ctk.CTkLabel(s3_grid, text="Discount Reason:", font=ctk.CTkFont(size=10)).grid(row=2, column=0, sticky="w", pady=2, padx=4)
        self.reason_entry = ctk.CTkEntry(s3_grid, height=30, placeholder_text="पुराना छात्र / ऑफर", font=ctk.CTkFont(size=11))
        self.reason_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=4)

        # Final Paid Amount (Mandatory)
        ctk.CTkLabel(s3_grid, text="Amount Paid (₹) *:", font=ctk.CTkFont(size=10, weight="bold"), text_color=COLOR_CYAN).grid(row=2, column=2, sticky="w", pady=2, padx=4)
        self.final_amt_entry = ctk.CTkEntry(
            s3_grid,
            height=30,
            placeholder_text="कुल जमा राशि ₹",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        self.final_amt_entry.grid(row=2, column=3, sticky="ew", pady=2, padx=4)
        self.final_amt_entry.bind("<KeyRelease>", lambda e: self.sanitize_numeric(self.final_amt_entry))

        # UTR
        ctk.CTkLabel(s3_grid, text="UTR / Ref No:", font=ctk.CTkFont(size=10)).grid(row=3, column=0, sticky="w", pady=2, padx=4)
        self.utr_entry = ctk.CTkEntry(s3_grid, height=30, placeholder_text="12-अंक UPI UTR (वैकल्पिक)", font=ctk.CTkFont(size=11))
        self.utr_entry.grid(row=3, column=1, sticky="ew", pady=2, padx=4)
        self.utr_entry.bind("<KeyRelease>", self.on_utr_changed)

        # Notes
        ctk.CTkLabel(s3_grid, text="Remarks / Notes:", font=ctk.CTkFont(size=10)).grid(row=3, column=2, sticky="w", pady=2, padx=4)
        self.notes_entry = ctk.CTkEntry(s3_grid, height=30, placeholder_text="विशेष नोट...", font=ctk.CTkFont(size=11))
        self.notes_entry.grid(row=3, column=3, sticky="ew", pady=2, padx=4)

        s3_grid.grid_columnconfigure((1, 3), weight=1)

        # --- Section 4: Screenshot Upload (Compact) ---
        sc_card = ctk.CTkFrame(col_right, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, corner_radius=8)
        sc_card.pack(fill="x", padx=10, pady=(2, 6))

        sc_row = ctk.CTkFrame(sc_card, fg_color="transparent")
        sc_row.pack(fill="x", padx=8, pady=6)

        self.sc_title_lbl = ctk.CTkLabel(
            sc_row,
            text=f"📷 {t('field_screenshot', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        )
        self.sc_title_lbl.pack(side="left")

        btn_browse_sc = ctk.CTkButton(
            sc_row,
            text="📷 Browse...",
            width=80,
            height=26,
            fg_color=COLOR_CYAN,
            text_color="#001633",
            font=ctk.CTkFont(size=10, weight="bold"),
            hover_color=COLOR_CYAN_HOVER,
            command=self.browse_screenshot
        )
        btn_browse_sc.pack(side="left", padx=8)

        self.sc_label = ctk.CTkLabel(
            sc_row,
            text="कोई स्क्रीनशॉट चुना नहीं गया",
            font=ctk.CTkFont(size=10),
            text_color="#94A3B8"
        )
        self.sc_label.pack(side="left", padx=4)

        self.sc_thumb_label = ctk.CTkLabel(sc_row, text="")
        self.sc_thumb_label.pack(side="right", padx=6)

        # --- Section 5: Action Buttons (Right at your fingertips) ---
        btn_row = ctk.CTkFrame(col_right, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        btn_save = ctk.CTkButton(
            btn_row,
            text="💾 " + t("btn_submit_admission", lang),
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.save_admission
        )
        btn_save.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_reset = ctk.CTkButton(
            btn_row,
            text="🔄 " + t("btn_clear_form", lang),
            height=36,
            width=90,
            fg_color="#64748B",
            hover_color="#475569",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.reset_form
        )
        btn_reset.pack(side="right")

        # Form Status / Error Label
        self.form_msg = ctk.CTkLabel(
            col_right,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#EF4444"
        )
        self.form_msg.pack(pady=(0, 4))

    def set_source(self, source):
        self.admission_source = source
        is_dark = self.config.get("theme", "dark") == "dark"
        if source == "Telecalling":
            self.btn_src_tele.configure(fg_color=COLOR_CYAN, text_color="#001633")
            self.btn_src_walk.configure(fg_color="transparent", text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK)
            self.mode_option.set("UPI QR")
            self.on_payment_mode_changed("UPI QR")
        else:
            self.btn_src_walk.configure(fg_color=COLOR_CYAN, text_color="#001633")
            self.btn_src_tele.configure(fg_color="transparent", text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK)
            self.mode_option.set("Cash / नकद")
            self.on_payment_mode_changed("Cash / नकद")

    def on_payment_mode_changed(self, mode):
        lang = self.config.get("language", "hi")
        if "Cash" in mode:
            self.acc_label.configure(text="Account (कैश में ऑटो):")
            if not self.acc_entry.get().strip() or self.acc_entry.get().strip() == "":
                self.acc_entry.delete(0, "end")
                self.acc_entry.insert(0, "Cash / नकद (काउंटर)")
            self.sc_title_lbl.configure(text="📷 Screenshot (Optional for Cash)")
            if not self.selected_screenshot_path:
                self.sc_label.configure(text="कैश में स्क्रीनशॉट वैकल्पिक है", text_color="#10B981")
        else:
            self.acc_label.configure(text="Account / नाम *:")
            if self.acc_entry.get().strip() == "Cash / नकद (काउंटर)":
                self.acc_entry.delete(0, "end")
            self.sc_title_lbl.configure(text=f"📷 {t('field_screenshot', lang)}")
            if not self.selected_screenshot_path:
                self.sc_label.configure(text="कोई स्क्रीनशॉट चुना नहीं गया", text_color="#94A3B8")

    def sanitize_phone(self, event=None):
        current = self.phone_entry.get()
        # Keep ONLY digits (0-9)
        digits = re.sub(r"[^\d]", "", current)
        # Limit strictly to 10 digits
        if len(digits) > 10:
            digits = digits[:10]
        if current != digits:
            self.phone_entry.delete(0, "end")
            self.phone_entry.insert(0, digits)

        # Real-time visual feedback for the user
        if digits:
            if digits[0] not in "6789":
                self.form_msg.configure(
                    text="⚠️ मोबाइल नंबर 6, 7, 8 या 9 से शुरू होना चाहिए (वैध भारतीय मोबाइल नंबर)!",
                    text_color="#F59E0B"
                )
            elif len(digits) < 10:
                self.form_msg.configure(
                    text=f"⚠️ 10 अंकों का मोबाइल नंबर दर्ज करें (वर्तमान: {len(digits)}/10 अंक)",
                    text_color="#F59E0B"
                )
            else:
                self.form_msg.configure(text="")
        else:
            self.form_msg.configure(text="")

        self.on_contact_changed()

    def sanitize_numeric(self, entry, event=None):
        current = entry.get()
        # Allow only digits and at most one decimal point
        cleaned = re.sub(r"[^\d.]", "", current)
        if cleaned.count(".") > 1:
            parts = cleaned.split(".")
            cleaned = parts[0] + "." + "".join(parts[1:])
        if current != cleaned:
            entry.delete(0, "end")
            entry.insert(0, cleaned)

    def validate_date_field(self, event=None):
        current = self.date_entry.get()
        # Allow only digits and hyphen
        cleaned = re.sub(r"[^\d-]", "", current)
        if len(cleaned) > 10:
            cleaned = cleaned[:10]
        if current != cleaned:
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, cleaned)

        val = self.date_entry.get().strip()
        if len(val) == 10:
            try:
                datetime.strptime(val, "%Y-%m-%d")
                self.form_msg.configure(text="")
            except ValueError:
                self.form_msg.configure(
                    text="⚠️ अमान्य तारीख! सही प्रारूप दर्ज करें (YYYY-MM-DD, उदा: 2026-11-10)",
                    text_color="#F59E0B"
                )
        elif len(val) > 0 and len(val) < 10:
            self.form_msg.configure(
                text="⚠️ तारीख का फॉर्मेट YYYY-MM-DD होना चाहिए (उदा: 2026-11-10)",
                text_color="#F59E0B"
            )
        else:
            self.form_msg.configure(text="")

    def on_contact_changed(self, event=None):
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        db = DatabaseManager.get_instance()
        duplicate = db.check_duplicate_student(phone, email)
        if duplicate:
            prev_course = duplicate.get("courses_taken", "")
            prev_name = duplicate.get("student_name", "")
            self.warning_banner.configure(
                text=f"⚠️ {t('warn_duplicate_student', self.config.get('language', 'hi'))} [पुराना: {prev_name} | {prev_course}]"
            )
            if not self.reason_entry.get().strip():
                self.reason_entry.insert(0, "पुराना छात्र रियायत (Loyalty Discount)")
        else:
            self.warning_banner.configure(text="")

    def on_utr_changed(self, event=None):
        utr = self.utr_entry.get().strip()
        db = DatabaseManager.get_instance()
        duplicate_utr = db.check_duplicate_utr(utr)
        if duplicate_utr:
            self.warning_banner.configure(
                text=f"⚠️ {t('warn_duplicate_utr', self.config.get('language', 'hi'))} [पहले दर्ज: {duplicate_utr['student_name']} - ₹{duplicate_utr['final_amount']}]"
            )
        else:
            self.on_contact_changed()

    def on_fee_changed(self, event=None):
        self.sanitize_numeric(self.orig_fee_entry)
        self.sanitize_numeric(self.disc_entry)
        try:
            orig_text = self.orig_fee_entry.get().strip()
            disc_text = self.disc_entry.get().strip()
            orig = float(orig_text) if orig_text else 0.0
            disc = float(disc_text) if disc_text else 0.0
            final_val = max(orig - disc, 0.0)
            if orig > 0 or disc > 0:
                self.final_amt_entry.delete(0, "end")
                self.final_amt_entry.insert(0, str(int(final_val) if final_val.is_integer() else round(final_val, 2)))
        except ValueError:
            pass

    def browse_screenshot(self):
        file_path = fd.askopenfilename(
            title="पेमेंट स्क्रीनशॉट चुनें",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp *.bmp")]
        )
        if file_path:
            self.selected_screenshot_path = file_path
            self.sc_label.configure(text=f"चयनित: {Path(file_path).name[:14]}... ({os.path.getsize(file_path)//1024} KB)", text_color=COLOR_SUCCESS)
            try:
                pil_thumb = ImageOptimizer.get_thumbnail(file_path, size=(36, 36))
                if pil_thumb:
                    self.thumb_ctk = ctk.CTkImage(light_image=pil_thumb, dark_image=pil_thumb, size=(36, 36))
                    self.sc_thumb_label.configure(image=self.thumb_ctk)
            except Exception:
                pass

    def save_admission(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip().replace(" ", "").replace("+91", "").replace("-", "")
        email = self.email_entry.get().strip()
        acc = self.acc_entry.get().strip()
        orig_fee_str = self.orig_fee_entry.get().strip()
        disc_str = self.disc_entry.get().strip()
        amt_str = self.final_amt_entry.get().strip()
        pay_date = self.date_entry.get().strip()
        utr = self.utr_entry.get().strip()
        pay_mode = self.mode_option.get()
        notes = self.notes_entry.get().strip()
        disc_reason = self.reason_entry.get().strip()

        # Selected courses
        chosen_courses = [c for c, var in self.course_checkboxes.items() if var.get()]

        is_cash = "Cash" in pay_mode
        if is_cash and not acc:
            acc = "Cash / नकद (काउंटर)"

        # -------------------------------------------------------------
        # 1. STRICT STUDENT NAME VALIDATION & AUTO-CAPITALIZATION
        # -------------------------------------------------------------
        if not name or len(name) < 2:
            self.form_msg.configure(text="कृपया छात्र का पूरा नाम दर्ज करें (कम से कम 2 अक्षर)!", text_color="#EF4444")
            self.name_entry.focus()
            return

        if name.isdigit() or not re.search(r"[a-zA-Z\u0900-\u097F]", name):
            self.form_msg.configure(text="कृपया छात्र का मान्य नाम दर्ज करें (केवल संख्या या चिन्ह नहीं)!", text_color="#EF4444")
            self.name_entry.focus()
            return

        # Auto-clean and title case (e.g., "rahul kumar" -> "Rahul Kumar")
        name = re.sub(r"\s+", " ", name).title()

        # -------------------------------------------------------------
        # 2. STRICT 10-DIGIT MOBILE NUMBER VALIDATION
        # -------------------------------------------------------------
        if not phone:
            self.form_msg.configure(text="कृपया 10 अंकों का मोबाइल नंबर दर्ज करें!", text_color="#EF4444")
            self.phone_entry.focus()
            return

        if not phone.isdigit():
            self.form_msg.configure(text="मोबाइल नंबर में केवल अंक (0-9) मान्य हैं!", text_color="#EF4444")
            self.phone_entry.focus()
            return

        if len(phone) != 10:
            self.form_msg.configure(text=f"मोबाइल नंबर ठीक 10 अंकों का होना चाहिए! (वर्तमान: {len(phone)} अंक)", text_color="#EF4444")
            self.phone_entry.focus()
            return

        if phone[0] not in "6789":
            self.form_msg.configure(text="कृपया वैध 10 अंकों का मोबाइल नंबर दर्ज करें (6, 7, 8 या 9 से शुरू होना चाहिए)!", text_color="#EF4444")
            self.phone_entry.focus()
            return

        # -------------------------------------------------------------
        # 3. STRICT PAYMENT DATE VALIDATION (YYYY-MM-DD)
        # -------------------------------------------------------------
        if not pay_date:
            self.form_msg.configure(text="कृपया पेमेंट तारीख (YYYY-MM-DD) दर्ज करें!", text_color="#EF4444")
            self.date_entry.focus()
            return

        try:
            valid_dt = datetime.strptime(pay_date, "%Y-%m-%d")
            if valid_dt.year < 2000 or valid_dt.year > 2050:
                raise ValueError("Year out of reasonable bounds")
        except ValueError:
            self.form_msg.configure(
                text="अमान्य तारीख! कृपया सही तारीख (YYYY-MM-DD) दर्ज करें (उदा: 2026-11-10)",
                text_color="#EF4444"
            )
            self.date_entry.focus()
            return

        # -------------------------------------------------------------
        # 4. STRICT EMAIL VALIDATION
        # -------------------------------------------------------------
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not email or not re.match(email_regex, email):
            self.form_msg.configure(text="कृपया सही ईमेल आईडी दर्ज करें (उदा: student@gmail.com)!", text_color="#EF4444")
            self.email_entry.focus()
            return

        # -------------------------------------------------------------
        # 5. COURSE SELECTION CHECK
        # -------------------------------------------------------------
        if not chosen_courses:
            self.form_msg.configure(text="कृपया कम से कम एक कोर्स चुनें (चेकबॉक्स टिक करें)!", text_color="#EF4444")
            return

        # -------------------------------------------------------------
        # 6. ACCOUNT / BENEFICIARY CHECK (FOR ONLINE MODES)
        # -------------------------------------------------------------
        if not is_cash and not acc:
            self.form_msg.configure(text="कृपया पेमेंट किस अकाउंट / बैंक में आया, वह दर्ज करें!", text_color="#EF4444")
            self.acc_entry.focus()
            return

        # -------------------------------------------------------------
        # 7. STANDARD FEE & CONCESSION NUMERIC VALIDATION
        # -------------------------------------------------------------
        try:
            orig_fee = float(orig_fee_str) if orig_fee_str else 0.0
            if orig_fee < 0:
                raise ValueError()
        except ValueError:
            self.form_msg.configure(text="Standard Fee में सिर्फ वैध संख्या दर्ज करें!", text_color="#EF4444")
            self.orig_fee_entry.focus()
            return

        try:
            disc_amt = float(disc_str) if disc_str else 0.0
            if disc_amt < 0:
                raise ValueError()
        except ValueError:
            self.form_msg.configure(text="Concession / Discount में सिर्फ वैध संख्या दर्ज करें!", text_color="#EF4444")
            self.disc_entry.focus()
            return

        # -------------------------------------------------------------
        # 8. FINAL PAID AMOUNT VALIDATION
        # -------------------------------------------------------------
        if not amt_str:
            self.form_msg.configure(text="कृपया कुल जमा राशि (Amount Paid) दर्ज करें!", text_color="#EF4444")
            self.final_amt_entry.focus()
            return

        try:
            final_amount = float(amt_str)
            if final_amount <= 0:
                self.form_msg.configure(text="जमा राशि 0 से अधिक होनी चाहिए!", text_color="#EF4444")
                self.final_amt_entry.focus()
                return
        except ValueError:
            self.form_msg.configure(text="जमा राशि (Amount Paid) में सिर्फ वैध संख्या दर्ज करें!", text_color="#EF4444")
            self.final_amt_entry.focus()
            return

        if orig_fee == 0.0:
            orig_fee = final_amount + disc_amt

        # -------------------------------------------------------------
        # 9. STRICT FRAUD CHECK: DUPLICATE UTR BLOCKER
        # -------------------------------------------------------------
        if utr:
            db_chk = DatabaseManager.get_instance()
            dup_utr = db_chk.check_duplicate_utr(utr)
            if dup_utr:
                self.form_msg.configure(
                    text=f"🚫 डुप्लीकेट UTR! यह UTR छात्र '{dup_utr['student_name']}' ({dup_utr['admission_no']}) में पहले से दर्ज है!",
                    text_color="#EF4444"
                )
                self.utr_entry.focus()
                return

        # -------------------------------------------------------------
        # 10. SCREENSHOT PROOF CHECK (Mandatory for UPI/Online, Optional for Cash)
        # -------------------------------------------------------------
        if not is_cash and not self.selected_screenshot_path:
            self.form_msg.configure(text="ऑनलाइन/UPI में पेमेंट स्क्रीनशॉट लगाना अनिवार्य है!", text_color="#EF4444")
            return

        db = DatabaseManager.get_instance()
        adm_no = db.generate_next_admission_no()

        # Optimize & save screenshot locally
        saved_screenshot_path = ""
        if self.selected_screenshot_path:
            saved_screenshot_path = ImageOptimizer.save_and_optimize_screenshot(self.selected_screenshot_path)

        admission_record = {
            "admission_no": adm_no,
            "student_name": name,
            "email": email,
            "phone": phone,
            "courses_taken": ", ".join(chosen_courses),
            "payment_mode": pay_mode,
            "account_holder": acc,
            "original_fee": orig_fee,
            "concession_amount": disc_amt,
            "concession_reason": disc_reason,
            "final_amount": final_amount,
            "utr_no": utr,
            "payment_date": pay_date,
            "screenshot_path": saved_screenshot_path,
            "admission_source": self.admission_source,
            "caller_staff_name": self.current_user.get("full_name", "Staff"),
            "caller_staff_id": self.current_user.get("id", 1),
            "notes": notes
        }

        try:
            db.add_admission(admission_record)
            db.log_activity(
                self.current_user.get("id", 1),
                self.current_user.get("username", "staff"),
                self.current_user.get("role", "caller"),
                "NEW_ADMISSION",
                f"Created {adm_no} for {name} (₹{final_amount})"
            )
            self.show_success_dialog(admission_record)
            self.reset_form()
            if self.on_record_saved:
                self.on_record_saved()
        except Exception as e:
            self.form_msg.configure(text=f"एरर: {str(e)}", text_color="#EF4444")

    def show_success_dialog(self, record):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Admission Successful")
        dialog.geometry("450x260")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="🎉 Admission Successfully Recorded!",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLOR_SUCCESS
        ).pack(pady=(16, 4))

        info_box = ctk.CTkFrame(dialog, fg_color=COLOR_NAVY_CARD, corner_radius=8)
        info_box.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(
            info_box,
            text=f"Admission No: {record['admission_no']}\nStudent: {record['student_name']}\nCourse: {record['courses_taken']}\nPaid: ₹{record['final_amount']:,.2f}",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#CBD5E1",
            justify="left"
        ).pack(padx=12, pady=8)

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(6, 12))

        def print_receipt():
            db = DatabaseManager.get_instance()
            out_pdf = db.receipts_dir / f"Receipt_{record['admission_no']}.pdf"
            if not out_pdf.exists() or out_pdf.stat().st_size < 1000:
                ReceiptGenerator.generate_fee_receipt(record, str(out_pdf))
            os.startfile(str(out_pdf))

        def send_whatsapp():
            inst_name = self.config.get("institute_name", "अपना कंप्यूटर सेंटर")
            msg_text = (
                f"नमस्ते {record['student_name']} जी! 🎓\n\n"
                f"{inst_name} में आपका हार्दिक स्वागत है। आपका एडमिशन सफलतापूर्वक दर्ज हो चुका है।\n\n"
                f"📌 एडमिशन विवरण:\n"
                f"• एडमिशन नं: {record['admission_no']}\n"
                f"• कोर्स: {record['courses_taken']}\n"
                f"• प्राप्त फीस: ₹{record['final_amount']:,.2f}\n"
                f"• तारीख: {record['payment_date']}\n\n"
                f"शुभकामनाएं!\n"
                f"{inst_name}"
            )
            phone = record["phone"].replace("+91", "").replace(" ", "").replace("-", "")
            encoded_text = urllib.parse.quote(msg_text)
            webbrowser.open(f"https://wa.me/91{phone}?text={encoded_text}")

        btn_wa = ctk.CTkButton(
            btn_row,
            text="💬 WhatsApp",
            height=34,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=send_whatsapp
        )
        btn_wa.pack(side="left", padx=(0, 6))

        btn_print = ctk.CTkButton(
            btn_row,
            text="🖨️ Print Fee Receipt (PDF)",
            height=34,
            fg_color=COLOR_CYAN,
            text_color="#001633",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            hover_color=COLOR_CYAN_HOVER,
            command=print_receipt
        )
        btn_print.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_close = ctk.CTkButton(
            btn_row,
            text="Done",
            height=34,
            width=80,
            fg_color="#64748B",
            text_color="#FFFFFF",
            command=dialog.destroy
        )
        btn_close.pack(side="right")

    def reset_form(self):
        self.name_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.acc_entry.delete(0, "end")
        self.orig_fee_entry.delete(0, "end")
        self.disc_entry.delete(0, "end")
        self.reason_entry.delete(0, "end")
        self.final_amt_entry.delete(0, "end")
        self.utr_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.selected_screenshot_path = ""
        self.sc_label.configure(text="कोई स्क्रीनशॉट चुना नहीं गया", text_color="#94A3B8")
        self.sc_thumb_label.configure(image="")
        self.warning_banner.configure(text="")
        self.form_msg.configure(text="")
        for var in self.course_checkboxes.values():
            var.set(False)
