import os
import sys
import subprocess
import threading
import queue
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog

from ..config import (
    BASE_DIR, CONVERTED_DIR, DEBUG,
    BG, SURFACE, CARD, BORDER, TEXT, MUTED, ACCENT,
    GREEN, GREEN_DIM, RED, YELLOW,
)
from ..i18n import T
from ..physics import find_naraka_paths, scan_all_drives, apply_physics
from ..proxy import _set_win_proxy
from ..qr_converter import process_image
from .widgets import section_header


class NarakaApp(ctk.CTk):

    _PLAT_KEYS = ["steam", "epic", "vng", "custom"]

    def __init__(self):
        super().__init__()
        self.title("Naraka Tool")
        self.geometry("540x700")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self._lang         = "en"
        self._current_plat = "steam"
        self._custom_path  = ""
        self._content      = None

        self._mitm_master   = None
        self._mitm_loop     = None
        self._mitm_thread   = None
        self._proxy_lock    = threading.Lock()
        self._proxy_on      = False
        self._updating_ui   = False
        self._log_queue     = queue.Queue()
        self._log_box_shown = False

        self._build_topbar()
        self._body = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0,
            scrollbar_fg_color=BG,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=MUTED)
        self._body.pack(fill="both", expand=True)
        self._rebuild_content()
        self.after(3000, self._poll_proxy)
        self.after(500,  self._poll_log_queue)

    # ── helpers ──────────────────────────────────────────────────────────────────
    def t(self, key, **kw):
        s = T[self._lang].get(key, key)
        return s.format(**kw) if kw else s

    # ── topbar ───────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=50)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="Naraka Tool",
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color=TEXT).pack(side="left", padx=20)

        lf = ctk.CTkFrame(bar, fg_color=CARD, corner_radius=8)
        lf.pack(side="right", padx=16, pady=10)

        self._btn_en = ctk.CTkButton(
            lf, text="EN", width=38, height=28, corner_radius=6,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            fg_color=ACCENT, hover_color="#3a72d4", text_color="#ffffff",
            command=lambda: self._switch_lang("en"))
        self._btn_en.pack(side="left", padx=(2, 0), pady=2)

        self._btn_vi = ctk.CTkButton(
            lf, text="VI", width=38, height=28, corner_radius=6,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            fg_color="transparent", hover_color=BORDER, text_color=MUTED,
            command=lambda: self._switch_lang("vi"))
        self._btn_vi.pack(side="left", padx=(0, 2), pady=2)

    def _switch_lang(self, lang):
        if lang == self._lang:
            return
        self._lang = lang
        for btn, code in [(self._btn_en, "en"), (self._btn_vi, "vi")]:
            active = code == lang
            btn.configure(
                fg_color=ACCENT if active else "transparent",
                hover_color="#3a72d4" if active else BORDER,
                text_color="#ffffff" if active else MUTED)
        self._log_box_shown = False
        self._rebuild_content()

    # ── body ─────────────────────────────────────────────────────────────────────
    def _rebuild_content(self):
        if self._content is not None:
            try:
                self._content.destroy()
            except Exception:
                pass
        self._content = ctk.CTkFrame(self._body, fg_color="transparent", corner_radius=0)
        self._content.pack(fill="x")
        self._build_physics(self._content)
        self._build_qr(self._content)
        self._build_proxy(self._content)

    # ════════════════════════════════════════════════════════════════════════════
    #  Character Physics
    # ════════════════════════════════════════════════════════════════════════════
    def _build_physics(self, parent):
        section_header(parent, self.t("sec_physics"))

        outer = ctk.CTkFrame(parent, fg_color="transparent")
        outer.pack(fill="x", padx=24)
        outer.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(outer, text=self.t("phys_hint"),
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=MUTED, anchor="w", justify="left",
                     wraplength=460).grid(row=0, column=0, sticky="w", pady=(0, 10))

        chip_frame = ctk.CTkFrame(outer, fg_color=CARD, corner_radius=8)
        chip_frame.grid(row=1, column=0, sticky="w")

        self._plat_btns = {}
        for i, key in enumerate(self._PLAT_KEYS):
            lbl    = self.t(f"plat_{key}")
            active = key == self._current_plat
            btn = ctk.CTkButton(
                chip_frame, text=lbl,
                width=0, height=30, corner_radius=6,
                font=ctk.CTkFont("Segoe UI", 11),
                fg_color=ACCENT if active else "transparent",
                hover_color="#3a72d4" if active else BORDER,
                text_color="#ffffff" if active else MUTED,
                command=lambda k=key: self._select_platform(k))
            btn.pack(
                side="left",
                padx=(2 if i == 0 else 0, 2 if i == len(self._PLAT_KEYS) - 1 else 0),
                pady=2)
            self._plat_btns[key] = btn

        crow = ctk.CTkFrame(outer, fg_color="transparent")
        crow.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self._custom_row = crow

        self._custom_entry = ctk.CTkEntry(
            crow, placeholder_text=self.t("custom_ph"),
            fg_color=CARD, border_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont("Segoe UI", 11), height=32)
        self._custom_entry.pack(side="left", fill="x", expand=True)
        if self._custom_path:
            self._custom_entry.insert(0, self._custom_path)

        ctk.CTkButton(
            crow, text=self.t("browse"),
            width=70, height=32, corner_radius=8,
            fg_color=CARD, hover_color=BORDER, text_color=TEXT,
            border_width=1, border_color=BORDER,
            font=ctk.CTkFont("Segoe UI", 11),
            command=self._browse_custom).pack(side="left", padx=(6, 0))

        if self._current_plat != "custom":
            crow.grid_remove()

        brow = ctk.CTkFrame(outer, fg_color="transparent")
        brow.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        self._phys_btn = ctk.CTkButton(
            brow, text=self.t("btn_enable"),
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            fg_color=GREEN, hover_color="#28a85a", text_color="#0f1f17",
            corner_radius=8, height=34, width=148,
            command=self._enable_physics)
        self._phys_btn.pack(side="left")

        self._scan_btn = ctk.CTkButton(
            brow, text=self.t("btn_scan"),
            font=ctk.CTkFont("Segoe UI", 11),
            fg_color=CARD, hover_color=BORDER, text_color=TEXT,
            corner_radius=8, height=34, width=120,
            border_width=1, border_color=BORDER,
            command=self._scan_machine)
        self._scan_btn.pack(side="left", padx=(8, 0))

        self._phys_status = ctk.CTkLabel(
            outer, text="",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=MUTED, anchor="w", wraplength=460)
        self._phys_status.grid(row=4, column=0, sticky="w", pady=(6, 0))

    def _select_platform(self, key: str):
        prev = self._current_plat
        self._current_plat = key
        for k, btn in self._plat_btns.items():
            active = k == key
            btn.configure(
                fg_color=ACCENT if active else "transparent",
                hover_color="#3a72d4" if active else BORDER,
                text_color="#ffffff" if active else MUTED)
        if key == "custom":
            self._custom_row.grid()
        elif prev == "custom":
            self._custom_row.grid_remove()

    def _browse_custom(self):
        path = filedialog.askdirectory(title="Select Naraka Bladepoint folder")
        if path:
            self._custom_path = os.path.normpath(path)
            self._custom_entry.delete(0, "end")
            self._custom_entry.insert(0, self._custom_path)

    def _enable_physics(self):
        if self._current_plat == "custom":
            self._custom_path = self._custom_entry.get().strip()
        self._phys_btn.configure(state="disabled")
        self._scan_btn.configure(state="disabled")
        self._phys_status.configure(text="", text_color=MUTED)
        paths = find_naraka_paths(self._current_plat, self._custom_path)
        if not paths:
            self._phys_status.configure(text=self.t("no_game"), text_color=YELLOW)
            self._phys_btn.configure(state="normal")
            self._scan_btn.configure(state="normal")
            return
        errors = []
        for p in paths:
            try:
                apply_physics(p)
            except Exception as e:
                errors.append(str(e))
        self._phys_btn.configure(state="normal")
        self._scan_btn.configure(state="normal")
        if errors:
            self._phys_status.configure(
                text=self.t("phys_err", e="; ".join(errors)), text_color=RED)
        else:
            self._phys_status.configure(
                text=self.t("found_n", n=len(paths)), text_color=GREEN)

    def _scan_machine(self):
        self._phys_btn.configure(state="disabled")
        self._scan_btn.configure(state="disabled")
        self._phys_status.configure(text=self.t("scanning"), text_color=MUTED)
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        paths  = scan_all_drives()
        errors = []
        for p in paths:
            try:
                apply_physics(p)
            except Exception as e:
                errors.append(str(e))
        self.after(0, lambda: self._scan_done(paths, errors))

    def _scan_done(self, paths, errors):
        try:
            self._phys_btn.configure(state="normal")
            self._scan_btn.configure(state="normal")
        except Exception:
            return
        if not paths:
            self._phys_status.configure(text=self.t("no_game"), text_color=YELLOW)
        elif errors:
            self._phys_status.configure(
                text=self.t("phys_err", e="; ".join(errors)), text_color=RED)
        else:
            self._phys_status.configure(
                text=self.t("found_n", n=len(paths)), text_color=GREEN)

    # ════════════════════════════════════════════════════════════════════════════
    #  QR Converter
    # ════════════════════════════════════════════════════════════════════════════
    def _build_qr(self, parent):
        section_header(parent, self.t("sec_qr"))

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", padx=24)

        ctk.CTkLabel(wrap, text=self.t("qr_desc"),
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=MUTED, anchor="w", justify="left",
                     wraplength=480).pack(anchor="w")

        note = ctk.CTkFrame(wrap, fg_color=CARD, corner_radius=8,
                            border_width=1, border_color=BORDER)
        note.pack(fill="x", pady=(8, 0))
        ni = ctk.CTkFrame(note, fg_color="transparent")
        ni.pack(fill="x", padx=12, pady=7)
        ctk.CTkLabel(ni, text="ℹ",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=ACCENT).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(ni, text=self.t("qr_proxy_note"),
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=MUTED, justify="left", wraplength=380,
                     anchor="w").pack(side="left", fill="x", expand=True)

        brow = ctk.CTkFrame(wrap, fg_color="transparent")
        brow.pack(fill="x", pady=(10, 0))

        self._qr_btn = ctk.CTkButton(
            brow, text=self.t("qr_pick"),
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            fg_color=ACCENT, hover_color="#3a72d4", text_color="#ffffff",
            corner_radius=8, height=34, width=150,
            command=self._pick_and_convert)
        self._qr_btn.pack(side="left")

        ctk.CTkButton(
            brow, text=self.t("qr_open"),
            font=ctk.CTkFont("Segoe UI", 11),
            fg_color=CARD, hover_color=BORDER, text_color=MUTED,
            corner_radius=8, height=34, width=110,
            border_width=1, border_color=BORDER,
            command=lambda: os.startfile(str(CONVERTED_DIR))
        ).pack(side="left", padx=(8, 0))

        self._qr_status = ctk.CTkLabel(
            wrap, text="",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=MUTED, anchor="w", wraplength=480)
        self._qr_status.pack(anchor="w", pady=(8, 0))

        self._result_frame = ctk.CTkScrollableFrame(
            wrap, fg_color=CARD, corner_radius=8,
            border_width=1, border_color=BORDER, height=96,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=MUTED)

    def _pick_and_convert(self):
        paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp"), ("All", "*.*")])
        if not paths:
            return
        self._qr_btn.configure(state="disabled", text=self.t("converting"))
        self._qr_status.configure(text=self.t("qr_proc", n=len(paths)), text_color=MUTED)
        for w in self._result_frame.winfo_children():
            w.destroy()
        self._result_frame.pack_forget()
        threading.Thread(target=self._qr_worker, args=(paths,), daemon=True).start()

    def _qr_worker(self, paths):
        results = []
        for p in paths:
            path = Path(p)
            try:
                result = process_image(path.read_bytes(), path.name)
            except Exception as e:
                result = {"file": path.name, "error": str(e)}
            results.append(result)
        self.after(0, lambda: self._show_results(results))

    def _show_results(self, results):
        ok  = [r for r in results if r.get("success")]
        bad = [r for r in results if not r.get("success")]
        try:
            self._qr_btn.configure(state="normal", text=self.t("qr_pick"))
        except Exception:
            return
        if ok and not bad:
            self._qr_status.configure(text=self.t("qr_ok", n=len(ok)), text_color=GREEN)
        elif bad and not ok:
            self._qr_status.configure(text=self.t("qr_fail", n=len(bad)), text_color=RED)
        else:
            self._qr_status.configure(
                text=self.t("qr_mixed", ok=len(ok), bad=len(bad)), text_color=YELLOW)
        for w in self._result_frame.winfo_children():
            w.destroy()
        for r in results:
            row = ctk.CTkFrame(self._result_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            if r.get("success"):
                icon, color, detail = "✓", GREEN, r.get("out_name", "")
            else:
                icon, color, detail = "✕", RED, r.get("error", "")
            ctk.CTkLabel(row, text=icon,
                         font=ctk.CTkFont("Segoe UI", 11, "bold"),
                         text_color=color, width=20).pack(side="left")
            ctk.CTkLabel(row, text=r["file"],
                         font=ctk.CTkFont("Segoe UI", 11),
                         text_color=TEXT, anchor="w").pack(side="left", padx=(4, 8))
            ctk.CTkLabel(row, text=detail,
                         font=ctk.CTkFont("Segoe UI", 10),
                         text_color=MUTED, anchor="w").pack(side="left", fill="x", expand=True)
        if results:
            self._result_frame.pack(fill="x", pady=(8, 0))

    # ════════════════════════════════════════════════════════════════════════════
    #  CN Proxy
    # ════════════════════════════════════════════════════════════════════════════
    def _build_proxy(self, parent):
        section_header(parent, self.t("sec_proxy"))

        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", padx=24)

        ctrl = ctk.CTkFrame(wrap, fg_color=CARD, corner_radius=10,
                            border_width=1, border_color=BORDER, height=48)
        ctrl.pack(fill="x")
        ctrl.pack_propagate(False)

        inner = ctk.CTkFrame(ctrl, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=0)

        self._pill = ctk.CTkFrame(inner, fg_color=BORDER, corner_radius=6, height=26)
        self._pill.pack(side="left", pady=10)
        self._pill.pack_propagate(False)
        self._pill_lbl = ctk.CTkLabel(
            self._pill,
            text=f"  ●  {self.t('proxy_on') if self._proxy_on else self.t('proxy_off')}  ",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color=GREEN if self._proxy_on else MUTED)
        self._pill_lbl.pack(expand=True)
        if self._proxy_on:
            self._pill.configure(fg_color=GREEN_DIM, border_width=1, border_color="#2ecc71")

        self._toggle = ctk.CTkSwitch(
            inner, text="", width=44, height=22,
            onvalue=True, offvalue=False,
            progress_color=GREEN, button_color="#ffffff",
            command=self._toggle_proxy)
        self._toggle.pack(side="right", pady=12)
        if self._proxy_on:
            self._toggle.select()

        note = ctk.CTkFrame(wrap, fg_color=CARD, corner_radius=10,
                            border_width=1, border_color=BORDER)
        note.pack(fill="x", pady=(8, 0))
        inner_note = ctk.CTkFrame(note, fg_color="transparent")
        inner_note.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(inner_note, text="⚠",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=YELLOW).pack(side="left", anchor="n", padx=(0, 10))
        ctk.CTkLabel(inner_note, text=self.t("proxy_warn"),
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=MUTED, justify="left", wraplength=400,
                     anchor="w").pack(side="left", fill="x", expand=True)

        self._log_box = ctk.CTkTextbox(
            wrap, fg_color=CARD, text_color="#55cc88",
            font=ctk.CTkFont("Courier New", 10),
            corner_radius=8, border_width=1, border_color=BORDER,
            height=78, state="disabled", wrap="word",
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=MUTED)

        ctk.CTkFrame(wrap, fg_color="transparent", height=16).pack()

    def _set_proxy_ui(self, on: bool):
        self._proxy_on    = on
        self._updating_ui = True
        try:
            if on:
                self._pill.configure(fg_color=GREEN_DIM, border_width=1, border_color="#2ecc71")
                self._pill_lbl.configure(
                    text=f"  ●  {self.t('proxy_on')}  ", text_color=GREEN)
                self._toggle.select()
            else:
                self._pill.configure(fg_color=BORDER, border_width=0)
                self._pill_lbl.configure(
                    text=f"  ●  {self.t('proxy_off')}  ", text_color=MUTED)
                self._toggle.deselect()
        except Exception:
            pass
        self._updating_ui = False

    def _toggle_proxy(self):
        if self._updating_ui:
            return
        if self._toggle.get():
            self._start_proxy()
        else:
            self._stop_proxy()

    def _start_proxy(self):
        with self._proxy_lock:
            if self._mitm_thread and self._mitm_thread.is_alive():
                return
            t = threading.Thread(target=self._start_proxy_thread, daemon=True)
            self._mitm_thread = t
        t.start()

    def _start_proxy_thread(self):
        import asyncio
        import logging

        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))


        _root_log = logging.getLogger()
        for _h in list(_root_log.handlers):
            if type(_h).__module__.startswith("mitmproxy"):
                try:
                    _root_log.removeHandler(_h)
                    _h.close()
                except Exception:
                    pass

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _run():
            from mitmproxy import options
            from mitmproxy.tools.dump import DumpMaster
            from naraka.addon import NarakaAddon

            opts   = options.Options(
                listen_host="0.0.0.0", listen_port=8080,
                mode=["regular"], ssl_insecure=True)
            master = DumpMaster(opts, with_termlog=False, with_dumper=False)
            master.addons.add(NarakaAddon(self._log_queue, debug=DEBUG))

            with self._proxy_lock:
                self._mitm_master = master
                self._mitm_loop   = loop

            self.after(0, lambda: self._set_proxy_ui(True))
            _set_win_proxy(True)

            async def _cert_import():
                import ctypes
                await asyncio.sleep(4)
                cert = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.cer"
                if cert.exists():
                    try:
                        chk = subprocess.run(
                            ["certutil", "-store", "Root"],
                            capture_output=True, text=True,
                            encoding="utf-8", errors="replace",
                            creationflags=flags)
                        if "mitmproxy" not in chk.stdout.lower():
                            ctypes.windll.shell32.ShellExecuteW(
                                None, "runas", "certutil",
                                f'-addstore -f Root "{str(cert)}"',
                                None, 0)
                    except Exception:
                        pass

            loop.create_task(_cert_import())
            await master.run()

        try:
            loop.run_until_complete(_run())
        except Exception:
            pass
        finally:
            _root_log = logging.getLogger()
            for _h in list(_root_log.handlers):
                if type(_h).__module__.startswith("mitmproxy"):
                    try:
                        _root_log.removeHandler(_h)
                        _h.close()
                    except Exception:
                        pass

            try:
                _pending = asyncio.all_tasks(loop)
                if _pending:
                    for _t in _pending:
                        _t.cancel()
                    loop.run_until_complete(
                        asyncio.gather(*_pending, return_exceptions=True))
            except Exception:
                pass
            _set_win_proxy(False)
            with self._proxy_lock:
                self._mitm_master = None
                self._mitm_loop   = None
            self.after(0, lambda: self._set_proxy_ui(False))
            try:
                loop.close()
            except Exception:
                pass

    def _poll_log_queue(self):
        try:
            while True:
                msg = self._log_queue.get_nowait()
                try:
                    if not self._log_box_shown:
                        self._log_box.pack(fill="x", pady=(8, 0))
                        self._log_box_shown = True
                    self._log_box.configure(state="normal")
                    self._log_box.insert("end", msg + "\n")
                    self._log_box.see("end")
                    self._log_box.configure(state="disabled")
                except Exception:
                    pass
        except queue.Empty:
            pass
        self.after(500, self._poll_log_queue)

    def _stop_proxy(self):
        with self._proxy_lock:
            master = self._mitm_master
            loop   = self._mitm_loop
        if master and loop:
            loop.call_soon_threadsafe(master.shutdown)
        else:
            self._set_proxy_ui(False)

    def _poll_proxy(self):
        with self._proxy_lock:
            running = (self._mitm_master is not None and
                       self._mitm_thread is not None and
                       self._mitm_thread.is_alive())
        if not self._updating_ui and running != self._proxy_on:
            self._set_proxy_ui(running)
        self.after(3000, self._poll_proxy)

    def on_close(self):
        _set_win_proxy(False)
        with self._proxy_lock:
            master = self._mitm_master
            loop   = self._mitm_loop
        if master and loop:
            loop.call_soon_threadsafe(master.shutdown)
        self.destroy()
