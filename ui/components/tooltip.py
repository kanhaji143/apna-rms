import tkinter as tk

class CTkTooltip:
    """
    Lightweight, elegant floating tooltip on hover for Tkinter/CustomTkinter widgets.
    Displays in dark navy with electric cyan text and subtle border.
    """
    def __init__(self, widget, text, delay_ms=200):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.tip_window = None
        self.schedule_id = None
        
        self.widget.bind("<Enter>", self.on_enter, add="+")
        self.widget.bind("<Leave>", self.on_leave, add="+")
        self.widget.bind("<ButtonPress>", self.on_leave, add="+")

    def on_enter(self, event=None):
        self.schedule()

    def on_leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.schedule_id = self.widget.after(self.delay_ms, self.show_tip)

    def unschedule(self):
        s_id = self.schedule_id
        self.schedule_id = None
        if s_id:
            try:
                self.widget.after_cancel(s_id)
            except Exception:
                pass

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 5
            y = self.widget.winfo_rooty() - 32
            
            # If too close to top of screen, show below widget
            if y < 30:
                y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes("-topmost", True)

            label = tk.Label(
                tw,
                text=self.text,
                justify="left",
                background="#00183A",
                foreground="#00F0FF",
                relief="solid",
                borderwidth=1,
                font=("Segoe UI", 9, "bold"),
                padx=8,
                pady=4
            )
            label.pack()
        except Exception:
            pass

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            try:
                tw.destroy()
            except Exception:
                pass
