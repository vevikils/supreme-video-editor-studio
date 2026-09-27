import os
import sys
import math
import json
import random
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Set global appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

TRANSITIONS = [
    "fade", "dissolve", "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown",
    "smoothleft", "smoothright", "circlecrop", "rectcrop",
    "distance", "fadeblack", "fadewhite", "radial", "zoomin"
]

VARIATION_MODES = [
    "Dinámico automático (Espejo, Reversa, Viñeta, Color)",
    "Solo Bucles Limpios (Loop Crossfade)",
    "Ida y Vuelta (Ping-Pong / Boomerang)",
    "Espejo Alternado (Normal -> Espejo -> Normal)"
]

RESOLUTIONS = {
    "1080p Full HD (1920x1080)": (1920, 1080),
    "4K Ultra HD (3840x2160)": (3840, 2160),
    "720p HD (1280x720)": (1280, 720),
    "TikTok / Reels 9:16 (1080x1920)": (1080, 1920),
    "Cuadrado 1:1 (1080x1080)": (1080, 1080)
}

def probe_file(file_path):
    """Obtiene la duración y datos del medio usando ffprobe"""
    if not os.path.exists(file_path):
        return None
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
        # If duration is 0, check streams
        if duration <= 0:
            for s in data.get("streams", []):
                if "duration" in s:
                    duration = float(s["duration"])
                    break
        has_video = any(s.get("codec_type") == "video" for s in data.get("streams", []))
        has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
        return {
            "duration": duration,
            "has_video": has_video,
            "has_audio": has_audio
        }
    except Exception as e:
        return None

class SupremeVideoEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Supreme Video Editor Studio")
        self.geometry("980x780")
        self.minsize(850, 680)

        # State
        self.video_path = tk.StringVar(value="")
        self.audio_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="")
        
        self.video_dur = 0.0
        self.audio_dur = 0.0
        self.is_exporting = False
        self.process = None

        self._build_ui()
        self._check_default_files()

    def _check_default_files(self):
        # Auto-detect files in current working dir if available
        cwd = os.getcwd()
        sample_v = os.path.join(cwd, "gemini_generated_video_d77be6b1.mp4")
        sample_a = os.path.join(cwd, "kdr ft vevi drill - 1 - UNA DIABLA.wav")
        if os.path.exists(sample_v):
            self.set_video_file(sample_v)
        if os.path.exists(sample_a):
            self.set_audio_file(sample_a)

    def _build_ui(self):
        # Layout: Header + Scrollable Content + Footer / Progress
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Header Bar
        header = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color=("#181926", "#11121d"))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title_badge = ctk.CTkLabel(
            header,
            text="★ SUPREME",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#e11d48",
            corner_radius=6,
            text_color="#ffffff",
            padx=10, pady=4
        )
        title_badge.grid(row=0, column=0, padx=(20, 10), pady=16)

        title_label = ctk.CTkLabel(
            header,
            text="VIDEO EDITOR STUDIO",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=("#ffffff", "#f8fafc")
        )
        title_label.grid(row=0, column=1, sticky="w", pady=16)

        sub_label = ctk.CTkLabel(
            header,
            text="Loop & Transitions Audio-Video Sync Engine",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94a3b8"
        )
        sub_label.grid(row=0, column=2, padx=20, pady=16)

        # 2. Main Scrollable Container
        scroll_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(15, 10))
        scroll_frame.grid_columnconfigure(0, weight=1)

        # SECTION A: Archivos Multimedia (Entradas)
        files_card = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color=("#212435", "#181a27"))
        files_card.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
        files_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            files_card,
            text="📂 ARCHIVOS MULTIMEDIA",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=18, pady=(14, 8))

        # Video Row
        ctk.CTkLabel(files_card, text="Vídeo Base:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=18, pady=5)
        self.entry_video = ctk.CTkEntry(files_card, textvariable=self.video_path, placeholder_text="Selecciona el archivo de vídeo a loopear...")
        self.entry_video.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkButton(files_card, text="Examinar", width=95, command=self.browse_video).grid(row=1, column=2, padx=(0, 18), pady=5)

        self.lbl_video_info = ctk.CTkLabel(files_card, text="Duración: No cargado", text_color="#94a3b8", font=ctk.CTkFont(size=11))
        self.lbl_video_info.grid(row=2, column=1, sticky="w", padx=2, pady=(0, 8))

        # Audio Row
        ctk.CTkLabel(files_card, text="Audio / Canción:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=18, pady=5)
        self.entry_audio = ctk.CTkEntry(files_card, textvariable=self.audio_path, placeholder_text="Selecciona la pista de audio / canción completa...")
        self.entry_audio.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkButton(files_card, text="Examinar", width=95, command=self.browse_audio).grid(row=3, column=2, padx=(0, 18), pady=5)

        self.lbl_audio_info = ctk.CTkLabel(files_card, text="Duración: No cargado", text_color="#94a3b8", font=ctk.CTkFont(size=11))
        self.lbl_audio_info.grid(row=4, column=1, sticky="w", padx=2, pady=(0, 8))

        # Output Row
        ctk.CTkLabel(files_card, text="Guardar en:", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, sticky="w", padx=18, pady=5)
        self.entry_output = ctk.CTkEntry(files_card, textvariable=self.output_path, placeholder_text="Ruta del vídeo final resultante...")
        self.entry_output.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=5)
        ctk.CTkButton(files_card, text="Destino", width=95, command=self.browse_output).grid(row=5, column=2, padx=(0, 18), pady=5)

        # Spacing
        ctk.CTkLabel(files_card, text="", height=4).grid(row=6, column=0)

        # SECTION B: Parámetros del Loop y Transiciones
        loop_card = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color=("#212435", "#181a27"))
        loop_card.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=5)
        loop_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            loop_card,
            text="✨ CONFIGURACIÓN DE LOOP Y TRANSICIONES",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#c084fc"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(14, 12))

        # Left Column: Modo de variación y Tipo de Transición
        f_left = ctk.CTkFrame(loop_card, fg_color="transparent")
        f_left.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 15))
        f_left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f_left, text="Estilo de Variaciones entre Bucles:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.combo_mode = ctk.CTkComboBox(f_left, values=VARIATION_MODES, height=34, state="readonly", command=self.update_summary)
        self.combo_mode.set(VARIATION_MODES[0])
        self.combo_mode.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(f_left, text="Efectos de Transición entre Bucles:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.combo_trans = ctk.CTkComboBox(f_left, values=["Aleatorias Dinámicas"] + TRANSITIONS, height=34, state="readonly")
        self.combo_trans.set("Aleatorias Dinámicas")
        self.combo_trans.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        # Right Column: Duración de transición, Fades
        f_right = ctk.CTkFrame(loop_card, fg_color="transparent")
        f_right.grid(row=1, column=1, sticky="nsew", padx=18, pady=(0, 15))
        f_right.grid_columnconfigure(1, weight=1)

        # Trans duration slider
        ctk.CTkLabel(f_right, text="Duración Transición (s):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.lbl_trans_dur = ctk.CTkLabel(f_right, text="1.0s", text_color="#38bdf8", font=ctk.CTkFont(weight="bold"))
        self.lbl_trans_dur.grid(row=0, column=1, sticky="e", pady=(0, 4))

        self.slider_trans_dur = ctk.CTkSlider(f_right, from_=0.3, to=3.0, number_of_steps=27, command=self._on_trans_dur_change)
        self.slider_trans_dur.set(1.0)
        self.slider_trans_dur.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # Fade out final slider
        ctk.CTkLabel(f_right, text="Fade Out Final (Vídeo & Audio):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.lbl_fade_out = ctk.CTkLabel(f_right, text="2.0s", text_color="#38bdf8", font=ctk.CTkFont(weight="bold"))
        self.lbl_fade_out.grid(row=2, column=1, sticky="e", pady=(0, 4))

        self.slider_fade_out = ctk.CTkSlider(f_right, from_=0.5, to=5.0, number_of_steps=45, command=self._on_fade_out_change)
        self.slider_fade_out.set(2.0)
        self.slider_fade_out.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # SECTION C: Ajustes de Vídeo, Color y Calidad
        video_card = ctk.CTkFrame(scroll_frame, corner_radius=12, fg_color=("#212435", "#181a27"))
        video_card.grid(row=2, column=0, sticky="ew", pady=(0, 15), padx=5)
        video_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            video_card,
            text="🎬 AJUSTES DE CALIDAD Y EXPORTACIÓN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ade80"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(14, 12))

        # Settings Col 1
        f_v1 = ctk.CTkFrame(video_card, fg_color="transparent")
        f_v1.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 15))
        f_v1.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f_v1, text="Resolución y Formato:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.combo_res = ctk.CTkComboBox(f_v1, values=list(RESOLUTIONS.keys()), height=34, state="readonly")
        self.combo_res.set("1080p Full HD (1920x1080)")
        self.combo_res.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(f_v1, text="FPS (Fotogramas por Segundo):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.combo_fps = ctk.CTkComboBox(f_v1, values=["30 fps", "60 fps", "24 fps"], height=34, state="readonly")
        self.combo_fps.set("30 fps")
        self.combo_fps.grid(row=3, column=0, sticky="ew", pady=(0, 12))

        # Settings Col 2
        f_v2 = ctk.CTkFrame(video_card, fg_color="transparent")
        f_v2.grid(row=1, column=1, sticky="nsew", padx=18, pady=(0, 15))
        f_v2.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f_v2, text="Calidad / Bitrate (CRF):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.combo_crf = ctk.CTkComboBox(f_v2, values=["Excelente / Master (CRF 16)", "Alta Calidad (CRF 18 - Recomendado)", "Estándar (CRF 21)", "Rápido / Ligero (CRF 24)"], height=34, state="readonly")
        self.combo_crf.set("Alta Calidad (CRF 18 - Recomendado)")
        self.combo_crf.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Checkboxes for extra spice
        self.chk_color_boost = ctk.CTkCheckBox(f_v2, text="Mejora sutil de contraste y saturación de color", onvalue=True, offvalue=False)
        self.chk_color_boost.select()
        self.chk_color_boost.grid(row=2, column=0, sticky="w", pady=(4, 6))

        self.chk_faststart = ctk.CTkCheckBox(f_v2, text="Optimizar para streaming web / YouTube (+faststart)", onvalue=True, offvalue=False)
        self.chk_faststart.select()
        self.chk_faststart.grid(row=3, column=0, sticky="w", pady=(2, 6))

        # SECTION D: Live Summary Box
        self.summary_box = ctk.CTkLabel(
            scroll_frame,
            text="Esperando archivos de vídeo y audio para calcular sincronización...",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("#181926", "#0f1017"),
            corner_radius=8,
            padx=14, pady=10,
            justify="left",
            anchor="w"
        )
        self.summary_box.grid(row=3, column=0, sticky="ew", pady=(0, 10), padx=5)

        # 3. Action & Progress Footer
        footer = ctk.CTkFrame(self, height=130, corner_radius=0, fg_color=("#181926", "#11121d"))
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        # Progress bar & status
        p_frame = ctk.CTkFrame(footer, fg_color="transparent")
        p_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(12, 6))
        p_frame.grid_columnconfigure(0, weight=1)

        self.lbl_status = ctk.CTkLabel(
            p_frame,
            text="Listo para procesar",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(p_frame, height=10, corner_radius=5)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # Buttons
        b_frame = ctk.CTkFrame(footer, fg_color="transparent")
        b_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(4, 14))
        b_frame.grid_columnconfigure(1, weight=1)

        self.btn_cancel = ctk.CTkButton(
            b_frame,
            text="Cancelar Proceso",
            fg_color="#475569",
            hover_color="#334155",
            width=140,
            height=38,
            command=self.cancel_render,
            state="disabled"
        )
        self.btn_cancel.grid(row=0, column=0, padx=(0, 10))

        self.btn_render = ctk.CTkButton(
            b_frame,
            text="⚡ RENDERIZAR VÍDEO COMPLETO",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e11d48",
            hover_color="#be123c",
            height=38,
            command=self.start_render
        )
        self.btn_render.grid(row=0, column=1, sticky="ew")

    def _on_trans_dur_change(self, val):
        self.lbl_trans_dur.configure(text=f"{val:.1f}s")
        self.update_summary()

    def _on_fade_out_change(self, val):
        self.lbl_fade_out.configure(text=f"{val:.1f}s")
        self.update_summary()

    def browse_video(self):
        file = filedialog.askopenfilename(
            title="Seleccionar Vídeo Base",
            filetypes=[("Vídeos MP4/MKV/MOV/WebM", "*.mp4 *.mkv *.mov *.webm *.avi"), ("Todos los archivos", "*.*")]
        )
        if file:
            self.set_video_file(file)

    def set_video_file(self, path):
        self.video_path.set(path)
        info = probe_file(path)
        if info and info["duration"] > 0:
            self.video_dur = info["duration"]
            self.lbl_video_info.configure(text=f"Duración: {self.video_dur:.2f}s ({self.format_time(self.video_dur)}) | Con vídeo detectado", text_color="#4ade80")
        else:
            self.video_dur = 0.0
            self.lbl_video_info.configure(text="No se pudo determinar duración (Revisa que FFmpeg esté disponible)", text_color="#f87171")
        self._auto_output_name()
        self.update_summary()

    def browse_audio(self):
        file = filedialog.askopenfilename(
            title="Seleccionar Audio / Canción",
            filetypes=[("Archivos de Audio", "*.wav *.mp3 *.aac *.flac *.m4a *.ogg"), ("Todos los archivos", "*.*")]
        )
        if file:
            self.set_audio_file(file)

    def set_audio_file(self, path):
        self.audio_path.set(path)
        info = probe_file(path)
        if info and info["duration"] > 0:
            self.audio_dur = info["duration"]
            self.lbl_audio_info.configure(text=f"Duración: {self.audio_dur:.2f}s ({self.format_time(self.audio_dur)}) | Audio estéreo OK", text_color="#4ade80")
        else:
            self.audio_dur = 0.0
            self.lbl_audio_info.configure(text="No se pudo determinar duración", text_color="#f87171")
        self._auto_output_name()
        self.update_summary()

    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Guardar Vídeo Final Como",
            defaultextension=".mp4",
            filetypes=[("Vídeo MP4", "*.mp4")]
        )
        if file:
            self.output_path.set(file)

    def _auto_output_name(self):
        if not self.output_path.get() and self.video_path.get():
            base_dir = os.path.dirname(self.video_path.get()) or os.getcwd()
            if self.audio_path.get():
                song_base = os.path.splitext(os.path.basename(self.audio_path.get()))[0]
                # Clean up song name
                safe_name = "".join(c for c in song_base if c.isalnum() or c in (' ', '_', '-')).strip()
                out_name = f"{safe_name}_SupremeMaster_1080p.mp4"
            else:
                out_name = "Supreme_Video_Output.mp4"
            self.output_path.set(os.path.join(base_dir, out_name))

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 10)
        return f"{m:02d}:{s:02d}.{ms}"

    def update_summary(self, *args):
        if self.video_dur <= 0 or self.audio_dur <= 0:
            self.summary_box.configure(text="ℹ️ Selecciona un vídeo base y una canción para calcular los loops requeridos.")
            return

        trans_dur = self.slider_trans_dur.get()
        effective_clip_dur = max(0.5, self.video_dur - trans_dur)
        
        # Calculate how many loops are needed
        # Formula: L = (Audio_dur - trans_dur) / effective_clip_dur + 1
        needed_loops = math.ceil((self.audio_dur - trans_dur) / effective_clip_dur) + 1
        if needed_loops < 2:
            needed_loops = 2

        total_video_generated = self.video_dur * needed_loops - (needed_loops - 1) * trans_dur

        summary_text = (
            f"📊 ESTIMACIÓN DE MONTAJE:\n"
            f"• Duración Audio: {self.audio_dur:.2f}s | Duración Vídeo Base: {self.video_dur:.2f}s\n"
            f"• Se generarán {needed_loops} bucles continuos con {needed_loops - 1} transiciones de {trans_dur:.1f}s\n"
            f"• Longitud total sincronizada: {self.audio_dur:.2f}s con fundido de salida de {self.slider_fade_out.get():.1f}s"
        )
        self.summary_box.configure(text=summary_text)

    def start_render(self):
        if self.is_exporting:
            return

        v_in = self.video_path.get()
        a_in = self.audio_path.get()
        out_f = self.output_path.get()

        if not os.path.exists(v_in):
            messagebox.showerror("Error", "El archivo de vídeo no existe o no es válido.")
            return
        if not os.path.exists(a_in):
            messagebox.showerror("Error", "El archivo de audio no existe o no es válido.")
            return
        if not out_f:
            messagebox.showerror("Error", "Por favor especifica la ruta de guardado.")
            return

        # Disable render button and enable cancel
        self.is_exporting = True
        self.btn_render.configure(state="disabled", text="⏳ RENDERIZANDO...")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        self.lbl_status.configure(text="Iniciando motor FFmpeg...", text_color="#38bdf8")

        # Run export in background thread
        thread = threading.Thread(target=self._render_worker, daemon=True)
        thread.start()

    def cancel_render(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.lbl_status.configure(text="Cancelando proceso...", text_color="#f87171")
            except Exception:
                pass

    def _render_worker(self):
        v_in = self.video_path.get()
        a_in = self.audio_path.get()
        out_f = self.output_path.get()

        v_info = probe_file(v_in)
        a_info = probe_file(a_in)

        v_dur = v_info["duration"] if v_info else self.video_dur
        a_dur = a_info["duration"] if a_info else self.audio_dur

        trans_dur = round(self.slider_trans_dur.get(), 2)
        fade_out = round(self.slider_fade_out.get(), 2)

        # Resolution
        res_text = self.combo_res.get()
        width, height = RESOLUTIONS.get(res_text, (1920, 1080))
        
        # FPS
        fps_text = self.combo_fps.get().split()[0]
        try:
            target_fps = int(fps_text)
        except ValueError:
            target_fps = 30

        # CRF
        crf_str = self.combo_crf.get()
        crf_val = "18"
        if "16" in crf_str:
            crf_val = "16"
        elif "18" in crf_str:
            crf_val = "18"
        elif "21" in crf_str:
            crf_val = "21"
        elif "24" in crf_str:
            crf_val = "24"

        # Mode
        mode = self.combo_mode.get()
        color_boost = self.chk_color_boost.get()
        faststart = self.chk_faststart.get()

        # Calculate number of clips needed
        effective_clip_dur = max(0.5, v_dur - trans_dur)
        needed_loops = math.ceil((a_dur - trans_dur) / effective_clip_dur) + 1
        if needed_loops < 2:
            needed_loops = 2

        # Build filter complex
        # Scale/crop filter to enforce selected resolution
        base_scale = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={target_fps}"

        clip_labels = []
        filter_lines = []

        chosen_transition = self.combo_trans.get()

        for i in range(needed_loops):
            lbl = f"c{i}"
            clip_labels.append(lbl)

            filters = [f"trim=0:{v_dur:.3f}"]

            # Mode variations
            if "Solo Bucles Limpios" in mode:
                # Keep plain
                filters.append("setpts=PTS-STARTPTS")
                filters.append(base_scale)
                if color_boost:
                    filters.append("eq=contrast=1.04:saturation=1.08")
            elif "Ping-Pong" in mode:
                # Even: forward, Odd: reverse
                if i % 2 == 1:
                    filters.append("reverse")
                filters.append("setpts=PTS-STARTPTS")
                filters.append(base_scale)
                if color_boost:
                    filters.append("eq=contrast=1.05:saturation=1.1")
            elif "Espejo Alternado" in mode:
                # Even: normal, Odd: hflip
                if i % 2 == 1:
                    filters.append("hflip")
                filters.append("setpts=PTS-STARTPTS")
                filters.append(base_scale)
                if color_boost:
                    filters.append("eq=contrast=1.05:saturation=1.1")
            else:
                # Dinámico automático (variedad creativa similar a UNA DIABLA)
                variant = i % 6
                if variant == 0:
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.05:saturation=1.1" if color_boost else "null")
                elif variant == 1:
                    filters.append("hflip")
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.08:saturation=1.15" if color_boost else "null")
                elif variant == 2:
                    filters.append("reverse")
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.05:saturation=1.12" if color_boost else "null")
                elif variant == 3:
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("vignette=PI/5")
                    filters.append("eq=contrast=1.1:saturation=1.2" if color_boost else "null")
                elif variant == 4:
                    filters.append("hflip")
                    filters.append("reverse")
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.06:saturation=1.1" if color_boost else "null")
                else:
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("vignette=PI/6")
                    filters.append("eq=contrast=1.07:saturation=1.15" if color_boost else "null")

            filters.append("format=yuv420p")
            clean_chain = ",".join(f for f in filters if f != "null")
            filter_lines.append(f"[0:v]{clean_chain}[{lbl}];")

        # Now build crossfade chain
        current_input = clip_labels[0]
        cur_offset = v_dur - trans_dur

        for i in range(1, needed_loops):
            next_input = clip_labels[i]
            out_lbl = f"v{i}" if i < needed_loops - 1 else "vpreout"

            if chosen_transition == "Aleatorias Dinámicas":
                # pick a rotating or randomized transition
                t_type = TRANSITIONS[(i - 1) % len(TRANSITIONS)]
            else:
                t_type = chosen_transition

            filter_lines.append(
                f"[{current_input}][{next_input}]xfade=transition={t_type}:duration={trans_dur:.2f}:offset={cur_offset:.2f}[{out_lbl}];"
            )
            current_input = out_lbl
            cur_offset += (v_dur - trans_dur)

        # Video fade out at the end
        fade_start = max(0.0, a_dur - fade_out)
        filter_lines.append(f"[{current_input}]fade=t=out:st={fade_start:.2f}:d={fade_out:.2f}[vout];")

        # Audio fades
        filter_lines.append(f"[1:a]afade=t=in:st=0:d=0.4,afade=t=out:st={fade_start:.2f}:d={fade_out:.2f}[aout]")

        filter_complex = "".join(filter_lines)

        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-y",
            "-i", v_in,
            "-i", a_in,
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", crf_val,
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "48000",
            "-t", f"{a_dur:.3f}"
        ]

        if faststart:
            cmd.extend(["-movflags", "+faststart"])

        cmd.append(out_f)

        # Start execution
        self.lbl_status.configure(text=f"Procesando {needed_loops} bucles sincronizados ({a_dur:.1f}s)...", text_color="#f59e0b")

        try:
            # We use startupinfo on windows to hide console popups
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                startupinfo=startupinfo,
                bufsize=1,
                universal_newlines=True
            )

            # Monitor progress line by line
            import re
            time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

            for line in self.process.stdout:
                match = time_regex.search(line)
                if match:
                    hours, mins, secs = match.groups()
                    curr_time = float(hours) * 3600 + float(mins) * 60 + float(secs)
                    progress = min(0.99, max(0.01, curr_time / a_dur))
                    
                    self.after(0, self._update_progress, progress, curr_time, a_dur)

            self.process.wait()
            ret = self.process.returncode

            if ret == 0:
                self.after(0, self._on_render_success, out_f)
            else:
                self.after(0, self._on_render_failed, "FFmpeg terminó con código de error. Revisa el archivo de log o prueba con otros clips.")

        except Exception as e:
            self.after(0, self._on_render_failed, str(e))

    def _update_progress(self, progress, curr_time, a_dur):
        self.progress_bar.set(progress)
        pct = int(progress * 100)
        self.lbl_status.configure(
            text=f"Renderizando: {pct}% ({self.format_time(curr_time)} / {self.format_time(a_dur)})",
            text_color="#38bdf8"
        )

    def _on_render_success(self, out_file):
        self.is_exporting = False
        self.progress_bar.set(1.0)
        self.lbl_status.configure(text="¡Vídeo completado con éxito! 🎉", text_color="#4ade80")
        self.btn_render.configure(state="normal", text="⚡ RENDERIZAR VÍDEO COMPLETO")
        self.btn_cancel.configure(state="disabled")

        res = messagebox.askyesno(
            "¡Renderizado Completado!",
            f"El vídeo ha sido creado correctamente en:\n\n{out_file}\n\n¿Deseas abrir la carpeta contenedora ahora?"
        )
        if res:
            try:
                os.startfile(os.path.dirname(out_file))
            except Exception:
                pass

    def _on_render_failed(self, err_msg):
        self.is_exporting = False
        self.lbl_status.configure(text="El proceso fue cancelado o tuvo un error.", text_color="#f87171")
        self.btn_render.configure(state="normal", text="⚡ RENDERIZAR VÍDEO COMPLETO")
        self.btn_cancel.configure(state="disabled")
        messagebox.showerror("Aviso de Exportación", f"Detalle: {err_msg}")

if __name__ == "__main__":
    app = SupremeVideoEditor()
    app.mainloop()
