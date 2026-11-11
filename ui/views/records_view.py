import os
import urllib.parse
import webbrowser
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
from core.receipt_generator import ReceiptGenerator
from core.id_card_generator import IDCardGenerator
from core.excel_service import ExcelService
from core.auth import AuthManager
from ui.components.tooltip import CTkTooltip

class RecordsView(ctk.CTkFrame):
    def __init__(self, parent, current_user, on_refresh_callback=None):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.on_refresh_callback = on_refresh_callback
        self.config = load_config()

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")

        # Top Control / Filter Bar
        ctrl_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        ctrl_card.pack(fill="x", padx=16, pady=(12, 12))

        filter_box = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        filter_box.pack(fill="x", padx=16, pady=12)

        # Search Entry
        ctk.CTkLabel(filter_box, text="🔍 Search:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 6))
        self.search_entry = ctk.CTkEntry(
            filter_box,
            placeholder_text="नाम, फोन, ईमेल, UTR या एडमिशन नंबर खोजें...",
            width=280,
            height=36
        )
        self.search_entry.pack(side="left", padx=(0, 14))
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_records())

        # Status Filter
        ctk.CTkLabel(filter_box, text="Status:", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=(0, 6))
        self.status_option = ctk.CTkOptionMenu(
            filter_box,
            values=["All", "Pending", "Activated", "Due Fees (बकाया फीस)"],
            width=130,
            height=36,
            fg_color=COLOR_NAVY_CARD if is_dark else "#FFFFFF",
            button_color=COLOR_CYAN,
            button_hover_color=COLOR_CYAN_HOVER,
            text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK,
            command=lambda v: self.load_records()
        )
        self.status_option.pack(side="left", padx=(0, 8))

        # Quick Due Fees Filter Button
        self.btn_due_filter = ctk.CTkButton(
            filter_box,
            text="💳 बकाया फीस (Due)",
            height=36,
            fg_color="#D97706",
            hover_color="#B45309",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.filter_due_fees
        )
        self.btn_due_filter.pack(side="left", padx=(0, 10))
        CTkTooltip(self.btn_due_filter, "जिन छात्रों की फीस किस्त बाकी है केवल उन्हें 1-क्लिक में देखें")

        # Quick Refresh Button
        btn_refresh = ctk.CTkButton(
            filter_box,
            text="🔄 Refresh",
            width=90,
            height=36,
            fg_color="#0284C7",
            hover_color="#0369A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.load_records
        )
        btn_refresh.pack(side="left", padx=(0, 8))
        CTkTooltip(btn_refresh, "तालिका रिफ्रेश करें (Refresh Records)")

        # Export Excel Button
        btn_export = ctk.CTkButton(
            filter_box,
            text="📊 Export Excel",
            width=120,
            height=36,
            fg_color=COLOR_CYAN,
            hover_color=COLOR_CYAN_HOVER,
            text_color="#001633",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_records_excel
        )
        btn_export.pack(side="right")
        CTkTooltip(btn_export, "छात्रों की एक्सेल शीट डाउनलोड करें (Export to Excel)")

        # Table Container Card
        table_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        table_card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Table Header
        self.th_frame = ctk.CTkFrame(table_card, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, height=36, corner_radius=6)
        self.th_frame.pack(fill="x", padx=12, pady=(12, 6))

        headers = [
            ("Adm No", 85), ("Date", 75), ("Student Name", 120), ("Phone", 85),
            ("Courses Enrolled", 130), ("Paid (₹)", 85), ("Mode", 60), ("Status", 75), ("Actions", 230)
        ]
        for title, w in headers:
            ctk.CTkLabel(
                self.th_frame,
                text=title,
                width=w,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#CBD5E1" if is_dark else "#334155"
            ).pack(side="left", padx=3)

        # Scrollable Rows Frame
        self.rows_frame = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.load_records()

    def filter_due_fees(self):
        self.status_option.set("Due Fees (बकाया फीस)")
        self.load_records()

    def load_records(self):
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        is_dark = self.config.get("theme", "dark") == "dark"
        search = self.search_entry.get().strip()
        status = self.status_option.get()

        db = DatabaseManager.get_instance()
        if status == "Due Fees (बकाया फीस)":
            raw_admissions = db.get_admissions(status=None, search_query=search)
            admissions = [
                a for a in raw_admissions
                if max(0.0, float(a.get("original_fee") or a.get("final_amount") or 0.0) - float(a.get("concession_amount") or 0.0) - float(a.get("final_amount") or 0.0)) > 0
            ]
        else:
            admissions = db.get_admissions(status=status, search_query=search)

        if not admissions:
            ctk.CTkLabel(
                self.rows_frame,
                text="कोई रिकॉर्ड नहीं मिला (No records found matching criteria).",
                font=ctk.CTkFont(size=12),
                text_color="#94A3B8"
            ).pack(pady=40)
            return

        for a in admissions:
            tr = ctk.CTkFrame(self.rows_frame, fg_color="transparent", height=38)
            tr.pack(fill="x", pady=2)

            is_act = a["activation_status"] == "Activated"
            status_color = COLOR_SUCCESS if is_act else COLOR_DANGER
            status_badge = "✅ Active" if is_act else "🚩 Pending"

            orig_fee = float(a.get("original_fee") or a.get("final_amount") or 0.0)
            disc_fee = float(a.get("concession_amount") or 0.0)
            paid_fee = float(a.get("final_amount") or 0.0)
            net_fee = max(0.0, orig_fee - disc_fee)
            balance_due = max(0.0, net_fee - paid_fee)

            paid_str = f"₹{paid_fee:,.0f}"
            paid_col = COLOR_SUCCESS if balance_due == 0 else "#F59E0B"
            if balance_due > 0:
                paid_str = f"₹{paid_fee:,.0f} (बाकी ₹{balance_due:,.0f})"

            ctk.CTkLabel(tr, text=a["admission_no"], width=85, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["payment_date"], width=75, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["student_name"][:16], width=120, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["phone"], width=85, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["courses_taken"][:18], width=130, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=paid_str, width=85, anchor="w", font=ctk.CTkFont(size=10, weight="bold"), text_color=paid_col).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=a["payment_mode"][:7], width=60, anchor="w", font=ctk.CTkFont(size=10)).pack(side="left", padx=3)
            ctk.CTkLabel(tr, text=status_badge, width=75, anchor="w", font=ctk.CTkFont(size=10, weight="bold"), text_color=status_color).pack(side="left", padx=3)

            # Actions Box
            act_box = ctk.CTkFrame(tr, fg_color="transparent", width=230)
            act_box.pack(side="left", padx=3)

            # View Screenshot Button
            if a.get("screenshot_path") and os.path.exists(a["screenshot_path"]):
                btn_sc = ctk.CTkButton(
                    act_box,
                    text="👁️",
                    width=28,
                    height=26,
                    fg_color="#0284C7",
                    hover_color="#0369A1",
                    font=ctk.CTkFont(size=10),
                    command=lambda p=a["screenshot_path"]: self.view_screenshot_modal(p)
                )
                btn_sc.pack(side="left", padx=1)
                CTkTooltip(btn_sc, "👁️ पेमेंट स्क्रीनशॉट देखें (View Screenshot)")

            # Print Receipt Button
            btn_rcpt = ctk.CTkButton(
                act_box,
                text="🖨️",
                width=28,
                height=26,
                fg_color="#334155",
                hover_color="#475569",
                font=ctk.CTkFont(size=10),
                command=lambda rec=a: self.print_receipt(rec)
            )
            btn_rcpt.pack(side="left", padx=1)
            CTkTooltip(btn_rcpt, "🖨️ A4 फीस रसीद प्रिंट करें (Print Fee Receipt)")

            # Print Student ID Card Button
            btn_id = ctk.CTkButton(
                act_box,
                text="🪪",
                width=28,
                height=26,
                fg_color="#4F46E5",
                hover_color="#4338CA",
                font=ctk.CTkFont(size=10),
                command=lambda rec=a: self.print_id_card(rec)
            )
            btn_id.pack(side="left", padx=1)
            CTkTooltip(btn_id, "🪪 पॉकेट आई-कार्ड बनाएं (Print Student ID Card)")

            # Pay Installment Button (Active if balance due > 0)
            if balance_due > 0:
                btn_inst = ctk.CTkButton(
                    act_box,
                    text="💳",
                    width=28,
                    height=26,
                    fg_color="#D97706",
                    hover_color="#B45309",
                    font=ctk.CTkFont(size=10),
                    command=lambda rec=a: self.open_installment_dialog(rec)
                )
                btn_inst.pack(side="left", padx=1)
                CTkTooltip(btn_inst, f"💳 बकाया किस्त जमा करें (Due: ₹{balance_due:,.0f})")

            # WhatsApp Direct Message / Reminder Button
            btn_wa = ctk.CTkButton(
                act_box,
                text="💬",
                width=28,
                height=26,
                fg_color="#10B981",
                hover_color="#059669",
                font=ctk.CTkFont(size=10),
                command=lambda rec=a: self.open_whatsapp_dialog(rec)
            )
            btn_wa.pack(side="left", padx=1)
            wa_tip = "💬 व्हाट्सएप फीस रिमाइंडर भेजें" if balance_due > 0 else "💬 व्हाट्सएप स्वागत व रसीद संदेश भेजें"
            CTkTooltip(btn_wa, wa_tip)

            # Quick Activate Button (if pending)
            if not is_act:
                btn_act = ctk.CTkButton(
                    act_box,
                    text="✅",
                    width=28,
                    height=26,
                    fg_color=COLOR_SUCCESS,
                    hover_color="#059669",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    command=lambda rec_id=a["id"]: self.quick_activate(rec_id)
                )
                btn_act.pack(side="left", padx=1)
                CTkTooltip(btn_act, "✅ कोर्स एक्टिवेट करें (Quick Activate Course)")

            # Delete Button (Only visible to Admin for security)
            if self.current_user.get("role") == "admin":
                btn_del = ctk.CTkButton(
                    act_box,
                    text="🗑️",
                    width=26,
                    height=26,
                    fg_color="#EF4444",
                    hover_color="#DC2626",
                    font=ctk.CTkFont(size=9),
                    command=lambda rec_id=a["id"], adm_no=a["admission_no"]: self.confirm_delete_record(rec_id, adm_no)
                )
                btn_del.pack(side="left", padx=1)
                CTkTooltip(btn_del, "🗑️ रिकॉर्ड डिलीट करें (Admin Password Required)")

    def confirm_delete_record(self, admission_id, admission_no):
        d = ctk.CTkToplevel(self)
        d.title("Delete Record")
        d.geometry("400x240")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text=f"🔒 एडमिन सुरक्षा: रिकॉर्ड '{admission_no}' हटाएं?",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#EF4444"
        ).pack(pady=(16, 6))

        ctk.CTkLabel(
            d,
            text="रिकॉर्ड मिटाने के लिए अपना Admin पासवर्ड दर्ज करें:",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8"
        ).pack(pady=(0, 8))

        pwd_entry = ctk.CTkEntry(d, width=240, height=34, show="•", placeholder_text="Admin Password")
        pwd_entry.pack(pady=4)
        pwd_entry.focus()

        err_lbl = ctk.CTkLabel(d, text="", font=ctk.CTkFont(size=11, weight="bold"), text_color="#EF4444")
        err_lbl.pack(pady=2)

        btn_box = ctk.CTkFrame(d, fg_color="transparent")
        btn_box.pack(pady=10)

        def do_delete():
            pwd = pwd_entry.get()
            if not pwd:
                err_lbl.configure(text="कृपया एडमिन पासवर्ड दर्ज करें!")
                return

            is_valid = AuthManager.authenticate(self.current_user.get("username", "admin"), pwd)
            if not is_valid:
                err_lbl.configure(text="❌ गलत पासवर्ड! डिलीट करने की अनुमति नहीं है।")
                return

            db = DatabaseManager.get_instance()
            db.delete_admission(admission_id)
            db.log_activity(
                self.current_user.get("id", 1),
                self.current_user.get("username", "admin"),
                "admin",
                "DELETE_ADMISSION",
                f"Deleted admission {admission_no}"
            )
            d.destroy()
            self.load_records()
            if self.on_refresh_callback:
                self.on_refresh_callback()

        ctk.CTkButton(btn_box, text="हाँ, हटाएं (Confirm Delete)", fg_color="#EF4444", hover_color="#DC2626", font=ctk.CTkFont(weight="bold"), command=do_delete).pack(side="left", padx=6)
        ctk.CTkButton(btn_box, text="रद्द करें (Cancel)", fg_color="#64748B", command=d.destroy).pack(side="left", padx=6)

    def quick_activate(self, admission_id):
        db = DatabaseManager.get_instance()
        user_name = self.current_user.get("full_name", "Staff")
        db.update_activation_status(admission_id, "Activated", user_name)
        self.load_records()
        if self.on_refresh_callback:
            self.on_refresh_callback()

    def view_screenshot_modal(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return

        modal = ctk.CTkToplevel(self)
        modal.title("Payment Screenshot Viewer")
        modal.geometry("640x700")
        modal.grab_set()

        ctk.CTkLabel(
            modal,
            text=f"📷 Payment Screenshot: {Path(image_path).name}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLOR_CYAN
        ).pack(pady=8)

        scroll_img = ctk.CTkScrollableFrame(modal, fg_color="transparent")
        scroll_img.pack(fill="both", expand=True, padx=12, pady=8)

        try:
            with Image.open(image_path) as pil_img:
                w, h = pil_img.size
                max_w = 580
                if w > max_w:
                    h = int(h * (max_w / w))
                    w = max_w
                resized = pil_img.resize((w, h), Image.Resampling.LANCZOS)
                self.modal_ctk_img = ctk.CTkImage(light_image=resized, dark_image=resized, size=(w, h))
                img_lbl = ctk.CTkLabel(scroll_img, image=self.modal_ctk_img, text="")
                img_lbl.pack(pady=4)
        except Exception as e:
            ctk.CTkLabel(scroll_img, text=f"Error displaying image: {e}").pack(pady=20)

        ctk.CTkButton(
            modal,
            text="बंद करें (Close)",
            height=34,
            fg_color="#64748B",
            text_color="#FFFFFF",
            command=modal.destroy
        ).pack(pady=8)

    def print_receipt(self, record):
        db = DatabaseManager.get_instance()
        out_pdf = db.receipts_dir / f"Receipt_{record['admission_no']}.pdf"
        ReceiptGenerator.generate_fee_receipt(record, str(out_pdf))
        os.startfile(str(out_pdf))

    def print_id_card(self, record):
        db = DatabaseManager.get_instance()
        out_pdf = db.receipts_dir / f"ID_Card_{record['admission_no']}.pdf"
        IDCardGenerator.generate_id_card(record, str(out_pdf))
        os.startfile(str(out_pdf))

    def open_installment_dialog(self, record):
        orig = float(record.get("original_fee") or record.get("final_amount") or 0.0)
        disc = float(record.get("concession_amount") or 0.0)
        paid = float(record.get("final_amount") or 0.0)
        net = max(0.0, orig - disc)
        due = max(0.0, net - paid)

        d = ctk.CTkToplevel(self)
        d.title(f"Pay Installment - {record['student_name']}")
        d.geometry("460x420")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text=f"💳 फीस किस्त जमा करें: {record['student_name']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_CYAN
        ).pack(pady=(16, 4))

        card = ctk.CTkFrame(d, fg_color=COLOR_NAVY_CARD, corner_radius=8)
        card.pack(fill="x", padx=20, pady=8)

        txt = (
            f"कोर्स: {record['courses_taken']}\n"
            f"कुल देय फीस: ₹{net:,.2f} | पूर्व जमा राशि: ₹{paid:,.2f}\n"
            f"👉 वर्तमान शेष बकाया (Balance Due): ₹{due:,.2f}"
        )
        ctk.CTkLabel(card, text=txt, font=ctk.CTkFont(size=11), text_color="#E0E1DD", justify="left").pack(padx=12, pady=10)

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=4)

        ctk.CTkLabel(f, text="किस्त राशि (Installment Amount ₹) *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        amt_entry = ctk.CTkEntry(f, height=34, font=ctk.CTkFont(size=12, weight="bold"))
        amt_entry.insert(0, str(int(due) if due.is_integer() else due))
        amt_entry.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="भुगतान मोड (Payment Mode) *:", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        mode_opt = ctk.CTkOptionMenu(f, values=["Cash / नकद", "UPI QR", "Card Swipe", "Net Banking"], height=34)
        mode_opt.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(f, text="रिमार्क / नोट (Optional):", font=ctk.CTkFont(size=10)).pack(anchor="w")
        note_entry = ctk.CTkEntry(f, height=30, placeholder_text="उदा: दूसरी किस्त")
        note_entry.pack(fill="x", pady=(2, 8))

        err_lbl = ctk.CTkLabel(d, text="", font=ctk.CTkFont(size=11), text_color="#EF4444")
        err_lbl.pack(pady=2)

        def save_installment():
            amt_val = amt_entry.get().strip()
            if not amt_val:
                err_lbl.configure(text="कृपया किस्त राशि दर्ज करें!")
                return
            try:
                inst_amt = float(amt_val)
                if inst_amt <= 0:
                    err_lbl.configure(text="राशि 0 से अधिक होनी चाहिए!")
                    return
            except ValueError:
                err_lbl.configure(text="वैध संख्या दर्ज करें!")
                return

            db = DatabaseManager.get_instance()
            today_str = datetime.now().strftime("%Y-%m-%d")
            staff = self.current_user.get("full_name", "Staff")
            success, rec_no = db.add_installment(
                record["id"],
                inst_amt,
                mode_opt.get(),
                today_str,
                note_entry.get().strip(),
                staff
            )
            if success:
                db.log_activity(
                    self.current_user.get("id", 1),
                    self.current_user.get("username", "staff"),
                    self.current_user.get("role", "staff"),
                    "INSTALLMENT_PAID",
                    f"Paid ₹{inst_amt} for {record['admission_no']} ({rec_no})"
                )
                d.destroy()
                self.load_records()
                if self.on_refresh_callback:
                    self.on_refresh_callback()

        ctk.CTkButton(
            d,
            text="💾 किस्त सेव करें व रसीद अपडेट करें",
            height=38,
            fg_color=COLOR_CYAN,
            text_color="#001633",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=save_installment
        ).pack(fill="x", padx=20, pady=(6, 12))

    def open_whatsapp_dialog(self, record):
        d = ctk.CTkToplevel(self)
        d.title(f"WhatsApp - {record['student_name']}")
        d.geometry("480x440")
        d.grab_set()

        ctk.CTkLabel(
            d,
            text=f"💬 WhatsApp मैसेज भेजें: {record['student_name']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#10B981"
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            d,
            text=f"मोबाइल: +91 {record['phone']} | कोर्स: {record['courses_taken'][:30]}",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8"
        ).pack(pady=(0, 10))

        tpl_frame = ctk.CTkFrame(d, fg_color="transparent")
        tpl_frame.pack(fill="x", padx=20, pady=(0, 8))

        inst_name = self.config.get("institute_name", "अपना कंप्यूटर सेंटर")
        orig = float(record.get("original_fee") or record.get("final_amount") or 0.0)
        disc = float(record.get("concession_amount") or 0.0)
        paid = float(record.get("final_amount") or 0.0)
        net = max(0.0, orig - disc)
        due = max(0.0, net - paid)

        def set_receipt_msg():
            msg_box.delete("1.0", "end")
            msg_text = (
                f"नमस्ते {record['student_name']} जी! 🎓\n\n"
                f"{inst_name} में आपका हार्दिक स्वागत है। आपका एडमिशन सफलतापूर्वक दर्ज हो चुका है।\n\n"
                f"📌 एडमिशन विवरण:\n"
                f"• एडमिशन नं: {record['admission_no']}\n"
                f"• कोर्स: {record['courses_taken']}\n"
                f"• प्राप्त फीस: ₹{record['final_amount']:,.2f}\n"
                f"• भुगतान मोड: {record['payment_mode']}\n"
                f"• तारीख: {record['payment_date']}\n\n"
                f"शुभकामनाएं!\n"
                f"{inst_name}"
            )
            msg_box.insert("1.0", msg_text)

        def set_reminder_msg():
            msg_box.delete("1.0", "end")
            msg_text = (
                f"नमस्ते {record['student_name']} जी! 🎓\n\n"
                f"{inst_name} से सादर नमस्ते!\n\n"
                f"आपके कोर्स *{record['courses_taken']}* की फीस किस्त का विवरण:\n"
                f"• कुल तय फीस: ₹{net:,.0f}\n"
                f"• अब तक जमा राशि: ₹{paid:,.0f}\n"
                f"• 👉 *शेष बकाया किस्त (Balance Due): ₹{due:,.0f}*\n\n"
                f"कृपया असुविधा से बचने के लिए बकाया किस्त समय पर संस्थान काउंटर या UPI द्वारा जमा कराने का कष्ट करें।\n\n"
                f"धन्यवाद!\n"
                f"प्रबंधन, {inst_name}\n"
                f"हेल्पलाइन: {self.config.get('institute_phone', '')}"
            )
            msg_box.insert("1.0", msg_text)

        btn_t1 = ctk.CTkButton(tpl_frame, text="🎉 एडमिशन रसीद मैसेज", height=28, font=ctk.CTkFont(size=10, weight="bold"), fg_color="#0284C7", command=set_receipt_msg)
        btn_t1.pack(side="left", padx=(0, 8))

        btn_t2 = ctk.CTkButton(tpl_frame, text="⏰ फीस किस्त रिमाइंडर", height=28, font=ctk.CTkFont(size=10, weight="bold"), fg_color="#EAB308", text_color="#001633", hover_color="#CA8A04", command=set_reminder_msg)
        btn_t2.pack(side="left")

        msg_box = ctk.CTkTextbox(d, height=170, font=ctk.CTkFont(size=11))
        msg_box.pack(fill="x", padx=20, pady=8)

        if due > 0:
            set_reminder_msg()
        else:
            set_receipt_msg()

        def do_send():
            raw_text = msg_box.get("1.0", "end").strip()
            encoded_text = urllib.parse.quote(raw_text)
            phone = record["phone"].replace("+91", "").replace(" ", "").replace("-", "")
            wa_url = f"https://wa.me/91{phone}?text={encoded_text}"
            webbrowser.open(wa_url)
            d.destroy()

        btn_send = ctk.CTkButton(
            d,
            text="🚀 WhatsApp पर भेजें (Send via WhatsApp)",
            height=38,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=do_send
        )
        btn_send.pack(fill="x", padx=20, pady=(6, 12))

    def export_records_excel(self):
        file_path = fd.asksaveasfilename(
            title="Excel फ़ाइल सेव करें",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            status = self.status_option.get()
            search = self.search_entry.get().strip()
            ExcelService.export_admissions_to_excel(file_path, status=status, search_query=search)
            os.startfile(file_path)
