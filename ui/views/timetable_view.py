import os
import urllib.parse
import webbrowser
from pathlib import Path
from datetime import datetime
import tkinter.filedialog as fd
import customtkinter as ctk
from core.config import (
    COLOR_CYAN, COLOR_CYAN_HOVER, COLOR_NAVY_SURFACE, COLOR_NAVY_CARD,
    COLOR_NAVY_BORDER, COLOR_LIGHT_SURFACE, COLOR_LIGHT_CARD,
    COLOR_TEXT_LIGHT, COLOR_TEXT_DARK, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    load_config
)
from core.translations import t
from core.database import DatabaseManager

DAYS = ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

class TimetableView(ctk.CTkFrame):
    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")
        self.current_user = current_user
        self.config = load_config()
        self.active_day = "All"

        self.setup_ui()

    def setup_ui(self):
        is_dark = self.config.get("theme", "dark") == "dark"
        lang = self.config.get("language", "hi")
        role = self.current_user.get("role", "caller").lower()
        can_manage = role in ("admin", "coordinator")

        # Header Bar
        banner = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        banner.pack(fill="x", padx=16, pady=(12, 12))

        b_left = ctk.CTkFrame(banner, fg_color="transparent")
        b_left.pack(side="left", padx=20, pady=14)

        ctk.CTkLabel(
            b_left,
            text=f"📅 {t('tt_title', lang)}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_CYAN if is_dark else "#0284C7"
        ).pack(anchor="w")

        ctk.CTkLabel(
            b_left,
            text="कक्षा समय-सारणी, शिक्षक अवकाश (Leave) व सब्स्टीट्यूट प्रबंधन",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#94A3B8" if is_dark else "#64748B"
        ).pack(anchor="w")

        b_right = ctk.CTkFrame(banner, fg_color="transparent")
        b_right.pack(side="right", padx=16, pady=14)

        if can_manage:
            btn_add = ctk.CTkButton(
                b_right,
                text=t("btn_add_schedule", lang),
                height=36,
                fg_color=COLOR_CYAN,
                hover_color=COLOR_CYAN_HOVER,
                text_color="#001633",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=self.show_add_dialog
            )
            btn_add.pack(side="left", padx=4)

        btn_exp = ctk.CTkButton(
            b_right,
            text=t("btn_export_timetable", lang),
            height=36,
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_schedule_text
        )
        btn_exp.pack(side="left", padx=4)

        btn_wa = ctk.CTkButton(
            b_right,
            text="💬 " + t("btn_whatsapp_timetable", lang),
            height=36,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.share_timetable_whatsapp
        )
        btn_wa.pack(side="left", padx=4)

        # Day Filter Bar
        day_bar = ctk.CTkFrame(self, fg_color="transparent")
        day_bar.pack(fill="x", padx=16, pady=(0, 10))

        self.day_buttons = {}
        for d in DAYS:
            btn = ctk.CTkButton(
                day_bar,
                text=d,
                width=80,
                height=30,
                corner_radius=15,
                fg_color=COLOR_CYAN if d == self.active_day else (COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD),
                text_color="#001633" if d == self.active_day else (COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK),
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda day=d: self.filter_day(day)
            )
            btn.pack(side="left", padx=3)
            self.day_buttons[d] = btn

        # Main Table Card
        card = ctk.CTkFrame(
            self,
            fg_color=COLOR_NAVY_SURFACE if is_dark else COLOR_LIGHT_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_NAVY_BORDER if is_dark else "#CBD5E1"
        )
        card.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Table Header
        th = ctk.CTkFrame(card, fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, height=36, corner_radius=6)
        th.pack(fill="x", padx=12, pady=(12, 6))

        cols = [
            ("Day", 85), ("Time Slot", 120), ("Subject / Topic", 160), ("Teacher Name", 140),
            ("Class / Batch", 120), ("Status / Substitute", 180), ("Actions", 120)
        ]
        for title, w in cols:
            ctk.CTkLabel(
                th,
                text=title,
                width=w,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="#CBD5E1" if is_dark else "#334155"
            ).pack(side="left", padx=4)

        self.scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.load_schedule()

    def filter_day(self, day):
        self.active_day = day
        is_dark = self.config.get("theme", "dark") == "dark"
        for d, b in self.day_buttons.items():
            if d == day:
                b.configure(fg_color=COLOR_CYAN, text_color="#001633")
            else:
                b.configure(fg_color=COLOR_NAVY_CARD if is_dark else COLOR_LIGHT_CARD, text_color=COLOR_TEXT_LIGHT if is_dark else COLOR_TEXT_DARK)
        self.load_schedule()

    def load_schedule(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        db = DatabaseManager.get_instance()
        items = db.get_timetable(day=self.active_day)

        if not items:
            ctk.CTkLabel(
                self.scroll,
                text="इस दिन के लिए कोई क्लास शेड्यूल नहीं है। ऊपर '+ नई क्लास जोड़ें' दबाएं।",
                font=ctk.CTkFont(size=12),
                text_color="#94A3B8"
            ).pack(pady=40)
            return

        can_manage = self.current_user.get("role", "caller").lower() in ("admin", "coordinator")

        for item in items:
            tr = ctk.CTkFrame(self.scroll, fg_color="transparent", height=38)
            tr.pack(fill="x", pady=2)

            is_leave = bool(item.get("is_leave", 0))
            sub = item.get("substitute_teacher", "")

            status_str = f"⚠️ On Leave ➡️ {sub}" if is_leave else "🟢 Active Class"
            status_clr = COLOR_WARNING if is_leave else COLOR_SUCCESS

            ctk.CTkLabel(tr, text=item["day_of_week"][:3], width=85, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=f"{item['start_time']} - {item['end_time']}", width=120, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=item["subject"][:22], width=160, anchor="w", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=item["teacher_name"][:18], width=140, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=item["room_batch"][:16], width=120, anchor="w", font=ctk.CTkFont(size=11)).pack(side="left", padx=4)
            ctk.CTkLabel(tr, text=status_str[:24], width=180, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), text_color=status_clr).pack(side="left", padx=4)

            # Actions
            act_box = ctk.CTkFrame(tr, fg_color="transparent", width=120)
            act_box.pack(side="left", padx=4)

            if can_manage:
                btn_sub = ctk.CTkButton(
                    act_box,
                    text="Leave/Sub",
                    width=65,
                    height=26,
                    fg_color="#0284C7",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    command=lambda s_id=item["id"], l=is_leave, sub_name=sub: self.show_leave_dialog(s_id, l, sub_name)
                )
                btn_sub.pack(side="left", padx=2)

                btn_del = ctk.CTkButton(
                    act_box,
                    text="🗑️",
                    width=28,
                    height=26,
                    fg_color="#EF4444",
                    hover_color="#DC2626",
                    font=ctk.CTkFont(size=10),
                    command=lambda s_id=item["id"]: self.delete_item(s_id)
                )
                btn_del.pack(side="left", padx=2)

    def show_add_dialog(self):
        d = ctk.CTkToplevel(self)
        d.title("Add Class Schedule")
        d.geometry("450x430")
        d.grab_set()

        ctk.CTkLabel(d, text="📅 नई क्लास जोड़ें (Add Class Schedule)", font=ctk.CTkFont(size=15, weight="bold"), text_color=COLOR_CYAN).pack(pady=(16, 12))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=24)

        ctk.CTkLabel(f, text="दिन (Day of Week):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        day_opt = ctk.CTkOptionMenu(f, values=DAYS[1:], height=34)
        day_opt.pack(fill="x", pady=(0, 6))

        db = DatabaseManager.get_instance()
        staff_teachers = [s["name"] for s in db.get_all_staff() if s.get("status") != "Inactive"]
        if not staff_teachers:
            staff_teachers = ["अमित सर", "प्रिया मैम", "सुनील जी"]

        ctk.CTkLabel(f, text="टीचर का नाम (चुनें या लिखें):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        t_entry = ctk.CTkComboBox(f, values=staff_teachers, height=34)
        if staff_teachers:
            t_entry.set(staff_teachers[0])
        t_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="सब्जेक्ट / कोर्स (Subject):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        s_entry = ctk.CTkEntry(f, height=34, placeholder_text="उदा: History / Computer Fundamentals")
        s_entry.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(f, text="समय (Time Slot):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        t_row = ctk.CTkFrame(f, fg_color="transparent")
        t_row.pack(fill="x", pady=(0, 6))
        st_entry = ctk.CTkEntry(t_row, height=34, placeholder_text="Start: 10:00 AM")
        st_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        et_entry = ctk.CTkEntry(t_row, height=34, placeholder_text="End: 11:30 AM")
        et_entry.pack(side="right", fill="x", expand=True, padx=(4, 0))

        ctk.CTkLabel(f, text="रूम / बैच (Room or Batch):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        r_entry = ctk.CTkEntry(f, height=34, placeholder_text="Room 1 / Morning Batch")
        r_entry.pack(fill="x", pady=(0, 10))

        def save():
            t_name = t_entry.get().strip()
            sub = s_entry.get().strip()
            st = st_entry.get().strip()
            et = et_entry.get().strip()
            rb = r_entry.get().strip()
            if not t_name or not sub or not st:
                return
            db = DatabaseManager.get_instance()
            db.add_schedule_item(t_name, sub, day_opt.get(), st, et, rb, self.current_user.get("full_name", "Admin"))
            d.destroy()
            self.load_schedule()

        ctk.CTkButton(d, text="सेव करें (Save Schedule)", height=38, fg_color=COLOR_CYAN, text_color="#001633", font=ctk.CTkFont(weight="bold"), command=save).pack(fill="x", padx=24, pady=10)

    def show_leave_dialog(self, schedule_id, is_leave, current_sub):
        d = ctk.CTkToplevel(self)
        d.title("Teacher Leave & Substitute")
        d.geometry("400x260")
        d.grab_set()

        ctk.CTkLabel(d, text="🏖️ शिक्षक अवकाश व सब्स्टीट्यूट", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_CYAN).pack(pady=(16, 8))

        f = ctk.CTkFrame(d, fg_color="transparent")
        f.pack(fill="x", padx=24)

        leave_var = ctk.BooleanVar(value=is_leave)
        chk = ctk.CTkCheckBox(f, text="टीचर आज छुट्टी (Leave) पर हैं", variable=leave_var, font=ctk.CTkFont(weight="bold"))
        chk.pack(anchor="w", pady=10)

        ctk.CTkLabel(f, text="सब्स्टीट्यूट टीचर (चुनें या लिखें):", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
        db = DatabaseManager.get_instance()
        staff_teachers = [s["name"] for s in db.get_all_staff() if s.get("status") != "Inactive"]
        if not staff_teachers:
            staff_teachers = ["विकास सर", "अमित सर", "प्रिया मैम"]
        sub_entry = ctk.CTkComboBox(f, values=staff_teachers, height=34)
        if current_sub:
            sub_entry.set(current_sub)
        elif staff_teachers:
            sub_entry.set(staff_teachers[0])
        sub_entry.pack(fill="x", pady=(0, 10))

        def save_leave():
            db = DatabaseManager.get_instance()
            db.update_teacher_leave(schedule_id, leave_var.get(), sub_entry.get().strip(), self.current_user.get("full_name", "Coordinator"))
            d.destroy()
            self.load_schedule()

        ctk.CTkButton(d, text="अपडेट करें (Save)", height=36, fg_color=COLOR_CYAN, text_color="#001633", font=ctk.CTkFont(weight="bold"), command=save_leave).pack(fill="x", padx=24, pady=10)

    def delete_item(self, schedule_id):
        db = DatabaseManager.get_instance()
        db.delete_schedule_item(schedule_id)
        self.load_schedule()

    def export_schedule_text(self):
        file_path = fd.asksaveasfilename(
            title="Export Timetable",
            defaultextension=".txt",
            initialfile=f"Timetable_{datetime.now().strftime('%Y-%m-%d')}.txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            db = DatabaseManager.get_instance()
            items = db.get_timetable()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"=== {self.config.get('institute_name', 'APNA COMPUTER')} - WEEKLY TIMETABLE ===\n")
                f.write(f"Generated On: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}\n\n")
                for d in DAYS[1:]:
                    f.write(f"--- {d.upper()} ---\n")
                    day_items = [i for i in items if i["day_of_week"] == d]
                    if not day_items:
                        f.write("  No classes scheduled.\n")
                    for i in day_items:
                        leave_note = f" [ON LEAVE -> Substitute: {i['substitute_teacher']}]" if i['is_leave'] else ""
                        f.write(f"  {i['start_time']} - {i['end_time']} | {i['subject']} | Teacher: {i['teacher_name']} | {i['room_batch']}{leave_note}\n")
                    f.write("\n")
            os.startfile(file_path)

    def share_timetable_whatsapp(self):
        """
        Formats today's or the active day's timetable into a clean, professional
        WhatsApp broadcast message and opens WhatsApp Web/Desktop.
        """
        db = DatabaseManager.get_instance()
        inst_name = self.config.get("institute_name", "APNA COMPUTER")
        today_day = datetime.now().strftime("%A")

        if self.active_day != "All":
            target_day = self.active_day
            items = db.get_timetable(day=target_day)
            day_label = f"🗓️ *दिन:* {target_day}"
        else:
            # First try today's timetable
            items = db.get_timetable(day=today_day)
            if items:
                target_day = today_day
                day_label = f"🗓️ *आज का दिन:* {today_day} (Daily Duty List)"
            else:
                # If no classes today, send full weekly schedule
                items = db.get_timetable()
                target_day = "All Days"
                day_label = "🗓️ *साप्ताहिक समय-सारणी (Full Weekly Schedule)*"

        if not items:
            # Show empty popup
            d = ctk.CTkToplevel(self)
            d.title("कोई क्लास नहीं मिली")
            d.geometry("380x150")
            d.grab_set()
            ctk.CTkLabel(d, text="⚠️ इस दिन के लिए कोई क्लास शेड्यूल नहीं है!", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_WARNING).pack(pady=(25, 10))
            ctk.CTkButton(d, text="ठीक है", command=d.destroy, fg_color="#334155").pack(pady=10)
            return

        date_str = datetime.now().strftime("%d-%b-%Y")
        lines = []
        lines.append(f"📢 *{inst_name.upper()} — शिक्षक समय-सारणी (Class Timetable)*")
        lines.append(f"{day_label} | *दिनांक:* {date_str}")
        lines.append("────────────────────────")
        lines.append("👨‍🏫 *कक्षा व ड्यूटी शेड्यूल:*")

        leaves = []
        for idx, it in enumerate(items, start=1):
            is_leave = bool(it.get("is_leave", 0))
            sub = it.get("substitute_teacher", "")
            time_slot = f"{it['start_time']} - {it['end_time']}"
            day_prefix = f"[{it['day_of_week'][:3]}] " if self.active_day == "All" and target_day == "All Days" else ""
            
            lines.append(f"\n*{idx}. {day_prefix}{it['subject']}* ({time_slot})")
            lines.append(f"   • फैकल्टी: *{it['teacher_name']}*")
            lines.append(f"   • क्लास / लैब: {it['room_batch']}")
            if is_leave:
                lines.append(f"   • ⚠️ *अवकाश (Leave)* ➡️ सब्स्टीट्यूट: *{sub}*")
                leaves.append(f"• {it['teacher_name']} (अवकाश) ➡️ {sub}")

        if leaves:
            lines.append("\n────────────────────────")
            lines.append("⚠️ *अवकाश व सब्स्टीट्यूट सूचना:*")
            for l in leaves:
                lines.append(f"  {l}")

        lines.append("\n────────────────────────")
        lines.append("📌 *नोट:* सभी शिक्षक क्लास समय से 10 मिनट पूर्व उपस्थित रहें।")
        lines.append(f"- प्रबंधन / डायरेक्टर, {inst_name}")

        full_msg = "\n".join(lines)
        encoded_msg = urllib.parse.quote(full_msg)
        wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
        webbrowser.open(wa_url)
