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

# Extended transitions list for cinematic variety
TRANSITIONS = [
    "fade", "dissolve", "fadeblack", "fadewhite", "distance",
    "wipeleft", "wiperight", "wipeup", "wipedown", "wipetl", "wipetr", "wipebl", "wipebr",
    "slideleft", "slideright", "slideup", "slidedown",
    "smoothleft", "smoothright", "smoothup", "smoothdown",
    "circlecrop", "rectcrop", "circleopen", "circleclose",
    "radial", "zoomin", "hlslice", "hrslice", "vu_slice", "vd_slice",
    "squeezeh", "squeezev", "horzopen", "horzclose", "vertopen", "vertclose"
]

VARIATION_MODES = [
    "Dinámico automático (Espejo, Reversa, Viñeta, Color)",
    "Solo Bucles Limpios (Loop Crossfade)",
    "Ida y Vuelta (Ping-Pong / Boomerang)",
    "Espejo Alternado (Normal -> Espejo -> Normal)"
]

PLATFORM_PRESETS = {
    "YouTube Visualizer (1080p 16:9 - Duración Completa Canción)": {
        "res": "1920x1080",
        "aspect": "16:9",
        "duration_mode": "full_audio",
        "custom_dur": 0.0,
        "fade_out": 2.0,
        "suffix": "_YouTube_1080p.mp4",
        "desc": "Vídeo horizontal 16:9 sincronizado con toda la canción y fundido suave final."
    },
    "Spotify Canvas (9:16 Vertical - Loop Corto 7.5s - Sin Audio)": {
        "res": "1080x1920",
        "aspect": "9:16",
        "duration_mode": "fixed_short",
        "custom_dur": 7.5,
        "fade_out": 0.0,
        "no_audio": True,
        "suffix": "_Spotify_Canvas_9x16.mp4",
        "desc": "Loop perfecto vertical (9:16) de 7.5 segundos sin audio para Canvas de Spotify."
    },
    "TikTok & Instagram Reels (9:16 Vertical - 30 Segundos Punchy)": {
        "res": "1080x1920",
        "aspect": "9:16",
        "duration_mode": "fixed_short",
        "custom_dur": 30.0,
        "fade_out": 1.5,
        "suffix": "_TikTok_Reels_30s.mp4",
        "desc": "Formato vertical 9:16 de 30 segundos ideal para previas virales en TikTok / Instagram."
    },
    "TikTok & Instagram Reels (9:16 Vertical - Duración Completa)": {
        "res": "1080x1920",
        "aspect": "9:16",
        "duration_mode": "full_audio",
        "custom_dur": 0.0,
        "fade_out": 2.0,
        "suffix": "_TikTok_Reels_Full.mp4",
        "desc": "Vídeo vertical 9:16 completo para Reels de larga duración o YouTube Shorts."
    },
    "YouTube 4K Ultra HD (3840x2160 - Máxima Calidad)": {
        "res": "3840x2160",
        "aspect": "16:9",
        "duration_mode": "full_audio",
        "custom_dur": 0.0,
        "fade_out": 2.0,
        "suffix": "_YouTube_4K.mp4",
        "desc": "Visualizer en ultra alta definición 4K a bitrate premium."
    },
    "Cuadrado Instagram Feed (1:1 - 1080x1080 - 60s)": {
        "res": "1080x1080",
        "aspect": "1:1",
        "duration_mode": "fixed_short",
        "custom_dur": 60.0,
        "fade_out": 1.5,
        "suffix": "_Insta_Post_1x1.mp4",
        "desc": "Formato cuadrado 1:1 de 60 segundos perfecto para feed de Instagram."
    }
}

GENRE_STYLES = [
    "Drill / Spanish Drill / Trap",
    "Urbano / Reggaeton / Trap Latino",
    "Hyperpop / Glitchcore / Electrónica",
    "Hip Hop / Boombap / Lo-Fi",
    "Pop / Rock / Indie",
    "Personalizado / Libre"
]

TEXT_POSITIONS = [
    "Centro (Estilo Portada Cinematográfica)",
    "Inferior Centrado (Subtítulo / Tercio Inferior)",
    "Superior Centrado (Top Banner)",
    "Esquina Inferior Izquierda (Minimalista)"
]

def probe_file(file_path):
    """Obtiene la duración y datos del medio usando ffprobe"""
    if not os.path.exists(file_path):
        return None
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_path
    ]
    try:
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        res = subprocess.run(cmd, capture_output=True, text=True, check=True, startupinfo=startupinfo)
        data = json.loads(res.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
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
    except Exception:
        return None

def get_system_font_path():
    """Busca una fuente de alta legibilidad instalada en Windows"""
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguiemj.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\tahoma.ttf"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c.replace("\\", "/")
    return "C:/Windows/Fonts/arial.ttf"

class SupremeVideoEditor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Supreme Video Editor Studio v3.0 - Professional Visualizer & Metadata Suite")
        self.geometry("1100x890")
        self.minsize(940, 740)

        # State Variables
        self.video_path = tk.StringVar(value="")
        self.audio_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="")
        
        self.track_title = tk.StringVar(value="UNA DIABLA")
        self.artist_name = tk.StringVar(value="KDR ft. VEVI")
        self.producer_name = tk.StringVar(value="VEVI")
        self.instagram_user = tk.StringVar(value="@vevikils")
        self.contact_email = tk.StringVar(value="diego@gmail.com")

        self.video_dur = 0.0
        self.audio_dur = 0.0
        self.is_exporting = False
        self.process = None

        # User Customizable Parameters (Duration, Zoom & Song Start Time)
        self.custom_duration_var = tk.StringVar(value="30.0")
        self.audio_start_var = tk.StringVar(value="00:00")
        self.zoom_var = tk.StringVar(value="100")

        self._build_ui()
        self._check_default_files()
        self.generate_seo_metadata()

    def _check_default_files(self):
        cwd = os.getcwd()
        sample_v = os.path.join(cwd, "gemini_generated_video_d77be6b1.mp4")
        sample_a = os.path.join(cwd, "kdr ft vevi drill - 1 - UNA DIABLA.wav")
        if os.path.exists(sample_v):
            self.set_video_file(sample_v)
        if os.path.exists(sample_a):
            self.set_audio_file(sample_a)

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Header Bar
        header = ctk.CTkFrame(self, height=65, corner_radius=0, fg_color=("#181926", "#11121d"))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title_badge = ctk.CTkLabel(
            header,
            text="★ SUPREME 2.7",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color="#e11d48",
            corner_radius=6,
            text_color="#ffffff",
            padx=10, pady=4
        )
        title_badge.grid(row=0, column=0, padx=(20, 10), pady=16)

        title_label = ctk.CTkLabel(
            header,
            text="VIDEO EDITOR & METADATA STUDIO",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=("#ffffff", "#f8fafc")
        )
        title_label.grid(row=0, column=1, sticky="w", pady=16)

        sub_label = ctk.CTkLabel(
            header,
            text="Universal Compatibility (YUV420p) • Typography Overlays • Multi-Platform",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94a3b8"
        )
        sub_label.grid(row=0, column=2, padx=20, pady=16)

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(self, corner_radius=10, fg_color=("#181a27", "#13141f"))
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=18, pady=(10, 10))
        
        self.tab_editor = self.tabview.add("🎬 Editor de Vídeo Multi-Plataforma")
        self.tab_seo = self.tabview.add("🏷️ Generador SEO YouTube / Spotify")

        self._build_editor_tab()
        self._build_seo_tab()

        # 3. Action & Progress Footer
        footer = ctk.CTkFrame(self, height=125, corner_radius=0, fg_color=("#181926", "#11121d"))
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        p_frame = ctk.CTkFrame(footer, fg_color="transparent")
        p_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(10, 4))
        p_frame.grid_columnconfigure(0, weight=1)

        self.lbl_status = ctk.CTkLabel(
            p_frame,
            text="Listo para renderizar y exportar con máxima compatibilidad universal",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.lbl_status.grid(row=0, column=0, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(p_frame, height=10, corner_radius=5)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        b_frame = ctk.CTkFrame(footer, fg_color="transparent")
        b_frame.grid(row=1, column=0, sticky="ew", padx=25, pady=(4, 12))
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
            text="⚡ EXPORTAR VÍDEO CON FORMATO SELECCIONADO",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#e11d48",
            hover_color="#be123c",
            height=38,
            command=self.start_render
        )
        self.btn_render.grid(row=0, column=1, sticky="ew")

    def _build_editor_tab(self):
        container = self.tab_editor
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure(0, weight=1)

        # CARD 1: Presets Multi-Plataforma
        preset_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        preset_card.grid(row=0, column=0, sticky="ew", pady=(0, 12), padx=5)
        preset_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            preset_card,
            text="📱 PRESETS RÁPIDOS POR PLATAFORMA",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f43f5e"
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 6))

        p_inner = ctk.CTkFrame(preset_card, fg_color="transparent")
        p_inner.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
        p_inner.grid_columnconfigure(0, weight=1)

        self.combo_preset = ctk.CTkComboBox(
            p_inner,
            values=list(PLATFORM_PRESETS.keys()),
            height=36,
            state="readonly",
            command=self._on_preset_change
        )
        self.combo_preset.set(list(PLATFORM_PRESETS.keys())[0])
        self.combo_preset.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.lbl_preset_desc = ctk.CTkLabel(
            p_inner,
            text=PLATFORM_PRESETS[list(PLATFORM_PRESETS.keys())[0]]["desc"],
            font=ctk.CTkFont(size=11),
            text_color="#38bdf8",
            justify="left"
        )
        self.lbl_preset_desc.grid(row=1, column=0, sticky="w")

        # CARD 2: Archivos Multimedia & Control de Tiempo
        files_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        files_card.grid(row=1, column=0, sticky="ew", pady=(0, 12), padx=5)
        files_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            files_card,
            text="📂 ARCHIVOS MULTIMEDIA & SINCRONIZACIÓN",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(12, 6))

        # Video Row
        ctk.CTkLabel(files_card, text="Vídeo Base:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=16, pady=4)
        self.entry_video = ctk.CTkEntry(files_card, textvariable=self.video_path, placeholder_text="Selecciona el vídeo original o generado con IA...")
        self.entry_video.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=4)
        ctk.CTkButton(files_card, text="Examinar", width=90, command=self.browse_video).grid(row=1, column=2, padx=(0, 16), pady=4)

        self.lbl_video_info = ctk.CTkLabel(files_card, text="Duración: No cargado", text_color="#94a3b8", font=ctk.CTkFont(size=11))
        self.lbl_video_info.grid(row=2, column=1, sticky="w", padx=2, pady=(0, 6))

        # Audio Row
        ctk.CTkLabel(files_card, text="Audio / Pista:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=16, pady=4)
        self.entry_audio = ctk.CTkEntry(files_card, textvariable=self.audio_path, placeholder_text="Selecciona la canción completa o beat...")
        self.entry_audio.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=4)
        ctk.CTkButton(files_card, text="Examinar", width=90, command=self.browse_audio).grid(row=3, column=2, padx=(0, 16), pady=4)

        self.lbl_audio_info = ctk.CTkLabel(files_card, text="Duración: No cargado", text_color="#94a3b8", font=ctk.CTkFont(size=11))
        self.lbl_audio_info.grid(row=4, column=1, sticky="w", padx=2, pady=(0, 6))

        # Prominent Audio Timing & Clip Duration Panel inside CARD 2
        timing_panel = ctk.CTkFrame(files_card, fg_color=("#181926", "#11121d"), corner_radius=8)
        timing_panel.grid(row=5, column=0, columnspan=3, sticky="ew", padx=16, pady=(4, 10))
        timing_panel.grid_columnconfigure((1, 3), weight=1)

        # 1. Custom Duration Control
        ctk.CTkLabel(
            timing_panel,
            text="⏱️ Duración del Vídeo (s):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#fbbf24"
        ).grid(row=0, column=0, sticky="w", padx=(14, 8), pady=10)
        self.entry_custom_dur = ctk.CTkEntry(
            timing_panel,
            textvariable=self.custom_duration_var,
            width=80,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            justify="center"
        )
        self.entry_custom_dur.grid(row=0, column=1, sticky="w", padx=(0, 16), pady=10)
        self.entry_custom_dur.bind("<KeyRelease>", lambda e: self.update_summary())

        # 2. Audio Start Time Control (SUPER VISIBLE)
        ctk.CTkLabel(
            timing_panel,
            text="🎵 Iniciar Audio en Segundo / Minuto:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4ade80"
        ).grid(row=0, column=2, sticky="w", padx=(10, 8), pady=10)
        self.entry_audio_start = ctk.CTkEntry(
            timing_panel,
            textvariable=self.audio_start_var,
            width=90,
            height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            placeholder_text="00:00 o seg",
            justify="center"
        )
        self.entry_audio_start.grid(row=0, column=3, sticky="w", padx=(0, 14), pady=10)
        self.entry_audio_start.bind("<KeyRelease>", lambda e: self.update_summary())

        # Output Row
        ctk.CTkLabel(files_card, text="Guardar en:", font=ctk.CTkFont(weight="bold")).grid(row=6, column=0, sticky="w", padx=16, pady=4)
        self.entry_output = ctk.CTkEntry(files_card, textvariable=self.output_path, placeholder_text="Destino del archivo de vídeo...")
        self.entry_output.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=4)
        ctk.CTkButton(files_card, text="Destino", width=90, command=self.browse_output).grid(row=6, column=2, padx=(0, 16), pady=4)

        ctk.CTkLabel(files_card, text="", height=2).grid(row=7, column=0)

        # CARD 3: Transiciones, Zoom & Efectos
        loop_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        loop_card.grid(row=2, column=0, sticky="ew", pady=(0, 12), padx=5)
        loop_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            loop_card,
            text="✨ CONFIGURACIÓN DE LOOP Y EFECTOS",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#c084fc"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 8))

        f_left = ctk.CTkFrame(loop_card, fg_color="transparent")
        f_left.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 12))
        f_left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(f_left, text="Estilo de Variaciones:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.combo_mode = ctk.CTkComboBox(f_left, values=VARIATION_MODES, height=32, state="readonly", command=self.update_summary)
        self.combo_mode.set(VARIATION_MODES[0])
        self.combo_mode.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(f_left, text="Transición Entre Loops (36+ Efectos):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 3))
        self.combo_trans = ctk.CTkComboBox(f_left, values=["Aleatorias Dinámicas"] + TRANSITIONS, height=32, state="readonly")
        self.combo_trans.set("Aleatorias Dinámicas")
        self.combo_trans.grid(row=3, column=0, sticky="ew", pady=(0, 6))

        f_right = ctk.CTkFrame(loop_card, fg_color="transparent")
        f_right.grid(row=1, column=1, sticky="nsew", padx=16, pady=(0, 12))
        f_right.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(f_right, text="Duración Transición (s):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.lbl_trans_dur = ctk.CTkLabel(f_right, text="1.0s", text_color="#38bdf8", font=ctk.CTkFont(weight="bold"))
        self.lbl_trans_dur.grid(row=0, column=1, sticky="e", pady=(0, 3))

        self.slider_trans_dur = ctk.CTkSlider(f_right, from_=0.3, to=2.5, number_of_steps=22, command=self._on_trans_dur_change)
        self.slider_trans_dur.set(1.0)
        self.slider_trans_dur.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(f_right, text="Fade Out Final (Vídeo & Audio):", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 3))
        self.lbl_fade_out = ctk.CTkLabel(f_right, text="2.0s", text_color="#38bdf8", font=ctk.CTkFont(weight="bold"))
        self.lbl_fade_out.grid(row=2, column=1, sticky="e", pady=(0, 3))

        self.slider_fade_out = ctk.CTkSlider(f_right, from_=0.0, to=4.0, number_of_steps=40, command=self._on_fade_out_change)
        self.slider_fade_out.set(2.0)
        self.slider_fade_out.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 6))

        # Bottom row in loop_card: Zoom del Vídeo
        f_custom = ctk.CTkFrame(loop_card, fg_color=("#181926", "#11121d"), corner_radius=8)
        f_custom.grid(row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 14))
        f_custom.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(f_custom, text="🔍 Zoom Vídeo (Encuadre / Escala):", font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8").grid(row=0, column=0, sticky="w", padx=(14, 8), pady=8)
        z_frame = ctk.CTkFrame(f_custom, fg_color="transparent")
        z_frame.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=8)
        z_frame.grid_columnconfigure(0, weight=1)
        self.slider_zoom = ctk.CTkSlider(z_frame, from_=50, to=250, number_of_steps=40, command=self._on_zoom_change)
        self.slider_zoom.set(100)
        self.slider_zoom.grid(row=0, column=0, sticky="ew")
        self.lbl_zoom = ctk.CTkLabel(z_frame, text="100%", width=50, font=ctk.CTkFont(size=12, weight="bold"), text_color="#38bdf8")
        self.lbl_zoom.grid(row=0, column=1, padx=(8, 0))

        # CARD 4: Tipografía y Texto Personalizado en Vídeo
        text_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        text_card.grid(row=3, column=0, sticky="ew", pady=(0, 12), padx=5)
        text_card.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            text_card,
            text="✍️ TEXTO Y TÍTULOS SOBRE EL VÍDEO (PLANTILLA)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#34d399"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 8))

        self.chk_enable_overlay = ctk.CTkCheckBox(
            text_card,
            text="Incrustar Título y Artista en el vídeo",
            font=ctk.CTkFont(weight="bold"),
            onvalue=True,
            offvalue=False
        )
        self.chk_enable_overlay.select()
        self.chk_enable_overlay.grid(row=1, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 10))

        # Text input fields
        ctk.CTkLabel(text_card, text="Título en Pantalla:").grid(row=2, column=0, sticky="w", padx=(16, 8), pady=3)
        self.entry_overlay_title = ctk.CTkEntry(text_card, textvariable=self.track_title, placeholder_text="Ej: UNA DIABLA")
        self.entry_overlay_title.grid(row=2, column=1, sticky="ew", padx=(0, 16), pady=3)

        ctk.CTkLabel(text_card, text="Artista / Subtítulo:").grid(row=2, column=2, sticky="w", padx=(16, 8), pady=3)
        self.entry_overlay_artist = ctk.CTkEntry(text_card, textvariable=self.artist_name, placeholder_text="Ej: KDR ft. VEVI")
        self.entry_overlay_artist.grid(row=2, column=3, sticky="ew", padx=(0, 16), pady=3)

        ctk.CTkLabel(text_card, text="Posición del Texto:").grid(row=3, column=0, sticky="w", padx=(16, 8), pady=6)
        self.combo_text_pos = ctk.CTkComboBox(text_card, values=TEXT_POSITIONS, state="readonly", height=30)
        self.combo_text_pos.set(TEXT_POSITIONS[0])
        self.combo_text_pos.grid(row=3, column=1, sticky="ew", padx=(0, 16), pady=6)

        ctk.CTkLabel(text_card, text="Duración Aparición:").grid(row=3, column=2, sticky="w", padx=(16, 8), pady=6)
        self.combo_text_timing = ctk.CTkComboBox(text_card, values=["Durante Todo el Vídeo", "Primeros 15 segundos", "Primeros 8 segundos"], state="readonly", height=30)
        self.combo_text_timing.set("Durante Todo el Vídeo")
        self.combo_text_timing.grid(row=3, column=3, sticky="ew", padx=(0, 16), pady=6)

        ctk.CTkLabel(text_card, text="", height=4).grid(row=4, column=0)

        # CARD 5: Live Summary
        self.summary_box = ctk.CTkLabel(
            scroll,
            text="Esperando archivos de vídeo y audio para calcular sincronización...",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=("#181926", "#0f1017"),
            corner_radius=8,
            padx=14, pady=10,
            justify="left",
            anchor="w"
        )
        self.summary_box.grid(row=4, column=0, sticky="ew", pady=(0, 10), padx=5)

    def _build_seo_tab(self):
        container = self.tab_seo
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scroll.grid_columnconfigure(0, weight=1)

        # Data Inputs Card
        data_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        data_card.grid(row=0, column=0, sticky="ew", pady=(0, 12), padx=5)
        data_card.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            data_card,
            text="🎵 DATOS DEL LANZAMIENTO / TRACK",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#fbbf24"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 10))

        # Row 1: Título & Artistas
        ctk.CTkLabel(data_card, text="Título Canción:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=(16, 8), pady=4)
        entry_t = ctk.CTkEntry(data_card, textvariable=self.track_title, placeholder_text="Ej: UNA DIABLA")
        entry_t.grid(row=1, column=1, sticky="ew", padx=(0, 16), pady=4)

        ctk.CTkLabel(data_card, text="Artistas:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=2, sticky="w", padx=(16, 8), pady=4)
        entry_a = ctk.CTkEntry(data_card, textvariable=self.artist_name, placeholder_text="Ej: KDR ft. VEVI")
        entry_a.grid(row=1, column=3, sticky="ew", padx=(0, 16), pady=4)

        # Row 2: Productor & Género
        ctk.CTkLabel(data_card, text="Productor / Beat:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=(16, 8), pady=4)
        entry_p = ctk.CTkEntry(data_card, textvariable=self.producer_name, placeholder_text="Ej: VEVI")
        entry_p.grid(row=2, column=1, sticky="ew", padx=(0, 16), pady=4)

        ctk.CTkLabel(data_card, text="Género / Estilo:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=2, sticky="w", padx=(16, 8), pady=4)
        self.combo_genre = ctk.CTkComboBox(data_card, values=GENRE_STYLES, state="readonly")
        self.combo_genre.set(GENRE_STYLES[0])
        self.combo_genre.grid(row=2, column=3, sticky="ew", padx=(0, 16), pady=4)

        # Row 3: Instagram & Email
        ctk.CTkLabel(data_card, text="Instagram:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=(16, 8), pady=4)
        entry_i = ctk.CTkEntry(data_card, textvariable=self.instagram_user, placeholder_text="@tu_usuario")
        entry_i.grid(row=3, column=1, sticky="ew", padx=(0, 16), pady=4)

        ctk.CTkLabel(data_card, text="Contacto / Email:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=2, sticky="w", padx=(16, 8), pady=4)
        entry_e = ctk.CTkEntry(data_card, textvariable=self.contact_email, placeholder_text="email@contacto.com")
        entry_e.grid(row=3, column=3, sticky="ew", padx=(0, 16), pady=4)

        btn_gen_seo = ctk.CTkButton(
            data_card,
            text="✨ REGENERAR METADATOS Y SEO AUTOMÁTICO",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=34,
            command=self.generate_seo_metadata
        )
        btn_gen_seo.grid(row=4, column=0, columnspan=4, sticky="ew", padx=16, pady=(12, 14))

        # Title suggestion
        t_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        t_card.grid(row=1, column=0, sticky="ew", pady=(0, 12), padx=5)
        t_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            t_card,
            text="📌 TÍTULO VIRAL SUGERIDO PARA YOUTUBE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(10, 4))

        self.txt_suggested_title = ctk.CTkEntry(t_card, font=ctk.CTkFont(weight="bold", size=13))
        self.txt_suggested_title.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkButton(
            t_card,
            text="Copiar Título",
            width=110,
            height=28,
            command=lambda: self.copy_to_clipboard(self.txt_suggested_title.get(), "Título copiado!")
        ).grid(row=1, column=1, padx=(0, 16), pady=(0, 8))

        # Description suggestion
        d_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        d_card.grid(row=2, column=0, sticky="ew", pady=(0, 12), padx=5)
        d_card.grid_columnconfigure(0, weight=1)

        d_head = ctk.CTkFrame(d_card, fg_color="transparent")
        d_head.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 4))
        d_head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            d_head,
            text="📝 DESCRIPCIÓN COMPLETA OPTIMIZADA (YOUTUBE / SPOTIFY)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4ade80"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            d_head,
            text="Copiar Descripción",
            width=140,
            height=28,
            command=lambda: self.copy_to_clipboard(self.txt_desc.get("1.0", "end-1c"), "Descripción copiada!")
        ).grid(row=0, column=1, sticky="e")

        self.txt_desc = ctk.CTkTextbox(d_card, height=180, font=ctk.CTkFont(size=12))
        self.txt_desc.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Tags suggestion
        tags_card = ctk.CTkFrame(scroll, corner_radius=12, fg_color=("#212435", "#181a27"))
        tags_card.grid(row=3, column=0, sticky="ew", pady=(0, 12), padx=5)
        tags_card.grid_columnconfigure(0, weight=1)

        tag_head = ctk.CTkFrame(tags_card, fg_color="transparent")
        tag_head.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 4))
        tag_head.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tag_head,
            text="🏷️ TAGS Y HASHTAGS DE ALTO ALCANCE (Separados por coma para YouTube)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#c084fc"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            tag_head,
            text="Copiar Tags",
            width=110,
            height=28,
            command=lambda: self.copy_to_clipboard(self.txt_tags.get("1.0", "end-1c"), "Tags copiados!")
        ).grid(row=0, column=1, sticky="e")

        self.txt_tags = ctk.CTkTextbox(tags_card, height=75, font=ctk.CTkFont(size=12))
        self.txt_tags.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.txt_hashtags = ctk.CTkEntry(tags_card, font=ctk.CTkFont(size=12))
        self.txt_hashtags.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

    def _on_zoom_change(self, val):
        self.lbl_zoom.configure(text=f"{int(val)}%")
        self.update_summary()

    def parse_timestamp(self, ts_str):
        """Convierte texto de tiempo (ej. '01:30', '90', '1:25.5') a segundos float"""
        if not ts_str:
            return 0.0
        s = ts_str.strip().replace(",", ".")
        try:
            if ":" in s:
                parts = s.split(":")
                if len(parts) == 2:
                    return max(0.0, float(parts[0]) * 60 + float(parts[1]))
                elif len(parts) == 3:
                    return max(0.0, float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]))
            return max(0.0, float(s))
        except Exception:
            return 0.0

    def _on_preset_change(self, choice):
        preset = PLATFORM_PRESETS.get(choice)
        if not preset:
            return
        self.lbl_preset_desc.configure(text=preset["desc"])
        self.slider_fade_out.set(preset["fade_out"])
        self.lbl_fade_out.configure(text=f"{preset['fade_out']:.1f}s")
        if preset["duration_mode"] == "fixed_short":
            self.custom_duration_var.set(str(preset["custom_dur"]))
        elif self.audio_dur > 0:
            self.custom_duration_var.set(f"{self.audio_dur:.1f}")
        self._auto_output_name()
        self.update_summary()

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
            self.lbl_video_info.configure(text=f"Duración: {self.video_dur:.2f}s ({self.format_time(self.video_dur)}) | Vídeo OK", text_color="#4ade80")
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
            preset = PLATFORM_PRESETS.get(self.combo_preset.get(), PLATFORM_PRESETS[list(PLATFORM_PRESETS.keys())[0]])
            if preset.get("duration_mode") != "fixed_short":
                self.custom_duration_var.set(f"{self.audio_dur:.1f}")
        else:
            self.audio_dur = 0.0
            self.lbl_audio_info.configure(text="No se pudo determinar duración", text_color="#f87171")
        
        base_name = os.path.splitext(os.path.basename(path))[0]
        if "-" in base_name:
            parts = base_name.split("-")
            self.track_title.set(parts[-1].strip())
            if len(parts) > 1 and not self.artist_name.get():
                self.artist_name.set(parts[0].strip())
        else:
            self.track_title.set(base_name.strip())

        self._auto_output_name()
        self.update_summary()
        self.generate_seo_metadata()

    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Guardar Vídeo Final Como",
            defaultextension=".mp4",
            filetypes=[("Vídeo MP4 Universal", "*.mp4")]
        )
        if file:
            self.output_path.set(file)

    def _auto_output_name(self):
        v_path = self.video_path.get()
        a_path = self.audio_path.get()
        source_path = v_path if (v_path and os.path.exists(v_path)) else a_path
        if not source_path:
            return
        base_dir = os.path.dirname(source_path) or os.getcwd()
        
        preset_choice = self.combo_preset.get()
        preset = PLATFORM_PRESETS.get(preset_choice, PLATFORM_PRESETS[list(PLATFORM_PRESETS.keys())[0]])
        suffix = preset["suffix"]

        title_str = self.track_title.get() or "Video_Output"
        safe_name = "".join(c for c in title_str if c.isalnum() or c in (' ', '_', '-')).strip().replace(" ", "_")

        self.output_path.set(os.path.join(base_dir, f"{safe_name}{suffix}"))

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 10)
        return f"{m:02d}:{s:02d}.{ms}"

    def update_summary(self, *args):
        preset = PLATFORM_PRESETS.get(self.combo_preset.get(), PLATFORM_PRESETS[list(PLATFORM_PRESETS.keys())[0]])
        has_video = self.video_dur > 0 and os.path.exists(self.video_path.get())
        has_audio = self.audio_dur > 0 and os.path.exists(self.audio_path.get())

        if not has_video and not has_audio:
            self.summary_box.configure(text="ℹ️ Selecciona un vídeo base o pista de audio para comenzar.")
            return

        trans_dur = self.slider_trans_dur.get()
        effective_clip_dur = max(0.5, self.video_dur - trans_dur) if has_video else 30.0

        # Target duration resolution (custom input or preset/audio)
        try:
            user_dur_val = float(self.custom_duration_var.get())
            if user_dur_val > 0:
                target_dur = user_dur_val
            else:
                target_dur = self.audio_dur if self.audio_dur > 0 else 30.0
        except ValueError:
            target_dur = self.audio_dur if self.audio_dur > 0 else 30.0

        if has_video:
            needed_loops = math.ceil((target_dur - trans_dur) / effective_clip_dur) + 1
            if needed_loops < 2:
                needed_loops = 2
            video_summary = f"Vídeo fuente: {self.video_dur:.2f}s | {needed_loops} bucles continuos (xfade {trans_dur:.1f}s)"
        else:
            video_summary = "Fondo visual animado de espectro (Generación automática)"

        # Zoom level info
        zoom_val = int(self.slider_zoom.get())
        zoom_info = f"100% (Normal)" if zoom_val == 100 else f"{zoom_val}% ({'Acercar' if zoom_val > 100 else 'Alejar'})"

        # Audio start point info
        audio_start_sec = self.parse_timestamp(self.audio_start_var.get())
        if preset.get("no_audio"):
            audio_note = "Sin audio (Loop visual Spotify Canvas)"
        else:
            start_str = self.format_time(audio_start_sec)
            audio_note = f"Desde {start_str} hasta {self.format_time(audio_start_sec + target_dur)} ({target_dur:.1f}s)"

        summary_text = (
            f"📊 ESTIMACIÓN ({preset['res']} • {preset['aspect']}):\n"
            f"• Duración final: {target_dur:.2f}s | {video_summary} | Zoom: {zoom_info}\n"
            f"• Audio: {audio_note} | Perfil YUV420p (Compatibilidad universal 100%)"
        )
        self.summary_box.configure(text=summary_text)

    def generate_seo_metadata(self):
        title = self.track_title.get().strip() or "UNA DIABLA"
        artist = self.artist_name.get().strip() or "VEVI"
        producer = self.producer_name.get().strip() or "VEVI"
        genre = self.combo_genre.get()
        ig = self.instagram_user.get().strip() or "@vevikils"
        mail = self.contact_email.get().strip() or "contacto@vevi.com"

        youtube_title = f"{title.upper()} - {artist} (Visualizer Oficial) [Prod. by {producer}]"
        self.txt_suggested_title.delete(0, "end")
        self.txt_suggested_title.insert(0, youtube_title)

        clean_title_tag = "".join(c for c in title if c.isalnum())
        artist_clean = "".join(c for c in artist.split()[0] if c.isalnum())

        desc_content = f"""🔥 "{title.upper()}" - {artist} (Official Visualizer)
Disfruta del videoclip / visualizer oficial de "{title.upper()}". {genre} con barras pesadas, flow oscuro y la producción más fresca.

🎵 Créditos del Tema:
• Artistas: {artist}
• Producción, Mezcla y Master: {producer}
• Edición de Vídeo & Visualizer: {producer}

📲 Redes Sociales y Streaming:
• Instagram: https://instagram.com/{ig.replace('@', '')}
• YouTube: @vevikils (¡Suscríbete y activa la campanita 🔔!)
• Spotify / Apple Music: Escucha "{title}" en todas las plataformas
• Contacto / Business / Beats: {mail}

🎧 Déjanos en los comentarios tu parte favorita y qué opinas de este visualizer.
"""
        self.txt_desc.delete("1.0", "end")
        self.txt_desc.insert("1.0", desc_content)

        genre_tags = []
        if "Drill" in genre:
            genre_tags = ["drill espanol", "spanish drill", "drill beat", "drill 2026", "drill espana", "drill argentino"]
        elif "Urbano" in genre or "Reggaeton" in genre:
            genre_tags = ["reggaeton 2026", "trap latino", "urbano latino", "latin trap", "perreo"]
        elif "Hyperpop" in genre:
            genre_tags = ["hyperpop espanol", "glitchcore", "rage beat", "electronic trap"]
        else:
            genre_tags = ["musica urbana", "trap espanol", "nuevo tema", "visualizer oficial"]

        specific_tags = [
            title.lower(),
            artist.lower(),
            f"{artist.lower()} {title.lower()}",
            f"{title.lower()} visualizer",
            f"prod by {producer.lower()}",
            "visualizer",
            "musica urbana"
        ] + genre_tags

        tags_string = ", ".join(list(dict.fromkeys(specific_tags)))
        self.txt_tags.delete("1.0", "end")
        self.txt_tags.insert("1.0", tags_string)

        hashtags = f"#{clean_title_tag} #{artist_clean} #Visualizer #MusicVideo #UrbanMusic #{genre.split('/')[0].replace(' ', '')}"
        self.txt_hashtags.delete(0, "end")
        self.txt_hashtags.insert(0, hashtags)

    def copy_to_clipboard(self, text, message="Copiado al portapapeles"):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", message)

    def start_render(self):
        if self.is_exporting:
            return

        v_in = self.video_path.get()
        a_in = self.audio_path.get()
        out_f = self.output_path.get()

        preset = PLATFORM_PRESETS.get(self.combo_preset.get(), PLATFORM_PRESETS[list(PLATFORM_PRESETS.keys())[0]])
        requires_audio = not preset.get("no_audio", False)

        has_v = bool(v_in and os.path.exists(v_in))
        has_a = bool(a_in and os.path.exists(a_in))

        if not has_v and not has_a:
            messagebox.showerror("Faltan Archivos", "Debes seleccionar al menos un vídeo base o una pista de audio.")
            return

        if not has_v:
            confirm = messagebox.askyesno(
                "Vídeo Base No Seleccionado",
                "No has seleccionado un archivo en 'Vídeo Base'.\n\n¿Deseas exportar generando un fondo visual oscuro animado con espectro sonoro para la pista de audio?"
            )
            if not confirm:
                return

        if requires_audio and not has_a:
            messagebox.showerror("Audio Requerido", "Para este formato necesitas seleccionar una pista de audio.")
            return

        if not out_f:
            self._auto_output_name()
            out_f = self.output_path.get()
            if not out_f:
                messagebox.showerror("Ruta de Guardado", "Por favor especifica la ruta de guardado para el vídeo.")
                return

        self.is_exporting = True
        self.btn_render.configure(state="disabled", text="⏳ RENDERIZANDO...")
        self.btn_cancel.configure(state="normal")
        self.progress_bar.set(0)
        self.lbl_status.configure(text="Iniciando render con codificación universal...", text_color="#38bdf8")

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

        has_v = bool(v_in and os.path.exists(v_in))
        has_a = bool(a_in and os.path.exists(a_in))

        v_info = probe_file(v_in) if has_v else None
        a_info = probe_file(a_in) if has_a else None

        v_dur = v_info["duration"] if v_info else self.video_dur
        a_dur = a_info["duration"] if a_info else self.audio_dur

        preset = PLATFORM_PRESETS.get(self.combo_preset.get(), PLATFORM_PRESETS[list(PLATFORM_PRESETS.keys())[0]])
        is_no_audio = preset.get("no_audio", False)

        trans_dur = round(self.slider_trans_dur.get(), 2)
        fade_out = round(self.slider_fade_out.get(), 2)

        # Resolution width & height
        w_str, h_str = preset["res"].split("x")
        width, height = int(w_str), int(h_str)

        # Target duration: use custom duration if specified and > 0
        try:
            user_dur_val = float(self.custom_duration_var.get())
            if user_dur_val > 0:
                target_dur = user_dur_val
            elif preset["duration_mode"] == "fixed_short":
                target_dur = preset["custom_dur"]
            else:
                target_dur = a_dur if a_dur > 0 else 60.0
        except ValueError:
            target_dur = preset["custom_dur"] if preset["duration_mode"] == "fixed_short" else (a_dur if a_dur > 0 else 60.0)

        # Video Zoom Scaling & Cropping (Zoom Factor: 50% - 250%)
        zoom_pct = self.slider_zoom.get()
        zoom_factor = max(0.5, min(3.0, zoom_pct / 100.0))

        audio_start_sec = self.parse_timestamp(self.audio_start_var.get())
        filter_lines = []
        cmd = ["ffmpeg", "-y"]

        if has_v and v_dur > 0.5:
            effective_clip_dur = max(0.5, v_dur - trans_dur)
            needed_loops = math.ceil((target_dur - trans_dur) / effective_clip_dur) + 1
            if needed_loops < 2:
                needed_loops = 2

            if abs(zoom_factor - 1.0) < 0.02:
                base_scale = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps=30"
            elif zoom_factor > 1.0:
                z_w = int(width * zoom_factor)
                z_h = int(height * zoom_factor)
                if z_w % 2 != 0: z_w += 1
                if z_h % 2 != 0: z_h += 1
                base_scale = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},scale={z_w}:{z_h},crop={width}:{height},fps=30"
            else:
                z_w = int(width * zoom_factor)
                z_h = int(height * zoom_factor)
                if z_w % 2 != 0: z_w += 1
                if z_h % 2 != 0: z_h += 1
                base_scale = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},scale={z_w}:{z_h},pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps=30"

            clip_labels = []
            mode = self.combo_mode.get()
            chosen_transition = self.combo_trans.get()

            for i in range(needed_loops):
                lbl = f"c{i}"
                clip_labels.append(lbl)

                filters = [f"trim=0:{v_dur:.3f}"]

                if "Solo Bucles Limpios" in mode:
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.04:saturation=1.08")
                elif "Ping-Pong" in mode:
                    if i % 2 == 1:
                        filters.append("reverse")
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.05:saturation=1.1")
                elif "Espejo Alternado" in mode:
                    if i % 2 == 1:
                        filters.append("hflip")
                    filters.append("setpts=PTS-STARTPTS")
                    filters.append(base_scale)
                    filters.append("eq=contrast=1.05:saturation=1.1")
                else:
                    variant = i % 6
                    if variant == 0:
                        filters.append("setpts=PTS-STARTPTS")
                        filters.append(base_scale)
                        filters.append("eq=contrast=1.05:saturation=1.1")
                    elif variant == 1:
                        filters.append("hflip")
                        filters.append("setpts=PTS-STARTPTS")
                        filters.append(base_scale)
                        filters.append("eq=contrast=1.08:saturation=1.15")
                    elif variant == 2:
                        filters.append("reverse")
                        filters.append("setpts=PTS-STARTPTS")
                        filters.append(base_scale)
                        filters.append("eq=contrast=1.05:saturation=1.12")
                    elif variant == 3:
                        filters.append("setpts=PTS-STARTPTS")
                        filters.append(base_scale)
                        filters.append("vignette=PI/5")
                        filters.append("eq=contrast=1.1:saturation=1.2")
                    elif variant == 4:
                        filters.append("hflip")
                        filters.append("reverse")
                        filters.append("setpts=PTS-STARTPTS")
                        filters.append(base_scale)
                        filters.append("eq=contrast=1.06:saturation=1.1")
                    else:
                        filters.append("setpts=PTS-STARTPTS")
                        filters.append(base_scale)
                        filters.append("vignette=PI/6")
                        filters.append("eq=contrast=1.07:saturation=1.15")

                filters.append("format=yuv420p")
                clean_chain = ",".join(filters)
                filter_lines.append(f"[0:v]{clean_chain}[{lbl}];")

            current_input = clip_labels[0]
            cur_offset = v_dur - trans_dur

            for i in range(1, needed_loops):
                next_input = clip_labels[i]
                out_lbl = f"v{i}" if i < needed_loops - 1 else "vpreout"

                if chosen_transition == "Aleatorias Dinámicas":
                    t_type = TRANSITIONS[(i - 1) % len(TRANSITIONS)]
                else:
                    t_type = chosen_transition

                filter_lines.append(
                    f"[{current_input}][{next_input}]xfade=transition={t_type}:duration={trans_dur:.2f}:offset={cur_offset:.2f}[{out_lbl}];"
                )
                current_input = out_lbl
                cur_offset += (v_dur - trans_dur)

            # Video fade out
            if fade_out > 0.1:
                fade_start = max(0.0, target_dur - fade_out)
                filter_lines.append(f"[{current_input}]fade=t=out:st={fade_start:.2f}:d={fade_out:.2f}[v_faded];")
                last_v = "v_faded"
            else:
                last_v = current_input

            cmd.extend(["-i", v_in])
            audio_input_idx = 1
        else:
            # Fallback: Create dynamic dark visualizer background
            filter_lines.append(
                f"color=c=#0f111a:s={width}x{height}:d={target_dur:.2f}:r=30,format=yuv420p[v_bg];"
            )
            if has_a and not is_no_audio:
                wave_h = max(180, int(height / 5))
                filter_lines.append(
                    f"[0:a]showwaves=s={width}x{wave_h}:mode=cline:colors=#e11d48|#38bdf8:rate=30[waves];"
                )
                y_wave = f"(h-{wave_h})/2+100"
                filter_lines.append(
                    f"[v_bg][waves]overlay=x=0:y={y_wave}:format=auto[v_motion];"
                )
                last_v = "v_motion"
            else:
                last_v = "v_bg"

            if fade_out > 0.1:
                fade_start = max(0.0, target_dur - fade_out)
                filter_lines.append(f"[{last_v}]fade=t=out:st={fade_start:.2f}:d={fade_out:.2f}[v_faded];")
                last_v = "v_faded"

            audio_input_idx = 0

        # Text Overlay Processing
        enable_text = self.chk_enable_overlay.get()
        title_text = self.entry_overlay_title.get().strip()
        artist_text = self.entry_overlay_artist.get().strip()

        if enable_text and (title_text or artist_text):
            font_path = get_system_font_path()
            safe_title = title_text.replace(":", "\\:").replace("'", "\\'").upper()
            safe_artist = artist_text.replace(":", "\\:").replace("'", "\\'")

            title_fsize = max(28, int(width / 32))
            artist_fsize = max(18, int(width / 48))

            pos_choice = self.combo_text_pos.get()
            if "Inferior Centrado" in pos_choice:
                y_title = "h-th-130"
                y_artist = "h-th-80"
                x_title = "(w-text_w)/2"
                x_artist = "(w-text_w)/2"
            elif "Superior Centrado" in pos_choice:
                y_title = "80"
                y_artist = "140"
                x_title = "(w-text_w)/2"
                x_artist = "(w-text_w)/2"
            elif "Esquina Inferior Izquierda" in pos_choice:
                x_title = "70"
                x_artist = "70"
                y_title = "h-th-130"
                y_artist = "h-th-80"
            else: # Centro (Estilo Portada Cinematográfica)
                y_title = "(h-text_h)/2-35"
                y_artist = "(h-text_h)/2+35"
                x_title = "(w-text_w)/2"
                x_artist = "(w-text_w)/2"

            timing_choice = self.combo_text_timing.get()
            timing_filter = ""
            if "15 segundos" in timing_choice:
                timing_filter = ":enable='between(t,0,15)'"
            elif "8 segundos" in timing_choice:
                timing_filter = ":enable='between(t,0,8)'"

            filter_lines.append(
                f"[{last_v}]drawtext=fontfile='{font_path}':text='{safe_title}':fontsize={title_fsize}:fontcolor=white:x={x_title}:y={y_title}:shadowcolor=black@0.8:shadowx=3:shadowy=3{timing_filter}[v_txt1];"
            )
            filter_lines.append(
                f"[v_txt1]drawtext=fontfile='{font_path}':text='{safe_artist}':fontsize={artist_fsize}:fontcolor=white@0.85:x={x_artist}:y={y_artist}:shadowcolor=black@0.8:shadowx=2:shadowy=2{timing_filter}[vout];"
            )
        else:
            filter_lines.append(f"[{last_v}]null[vout];")

        # Audio handling (with customizable start time / offset)
        if not is_no_audio and has_a:
            if audio_start_sec > 0.05:
                cmd.extend(["-ss", f"{audio_start_sec:.3f}"])
            cmd.extend(["-i", a_in])

            if fade_out > 0.1:
                fade_start = max(0.0, target_dur - fade_out)
                filter_lines.append(f"[{audio_input_idx}:a]afade=t=in:st=0:d=0.4,afade=t=out:st={fade_start:.2f}:d={fade_out:.2f}[aout]")
            else:
                filter_lines.append(f"[{audio_input_idx}:a]anull[aout]")

        filter_complex = "".join(filter_lines)

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vout]"
        ])

        if not is_no_audio and os.path.exists(a_in):
            cmd.extend([
                "-map", "[aout]",
                "-c:a", "aac",
                "-b:a", "320k",
                "-ar", "48000"
            ])
        else:
            cmd.append("-an")

        # CRITICAL FIX: Explicit -pix_fmt yuv420p for 100% universal player compatibility (Windows Media Player, QuickTime, iOS, Android, Browsers)
        cmd.extend([
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            "-crf", "18",
            "-t", f"{target_dur:.3f}",
            "-movflags", "+faststart",
            out_f
        ])

        self.lbl_status.configure(
            text=f"Exportando {preset['aspect']} ({target_dur:.1f}s) con YUV420p universal...",
            text_color="#f59e0b"
        )

        try:
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

            import re
            time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            captured_log = []

            for line in self.process.stdout:
                captured_log.append(line)
                if len(captured_log) > 30:
                    captured_log.pop(0)
                match = time_regex.search(line)
                if match:
                    hours, mins, secs = match.groups()
                    curr_time = float(hours) * 3600 + float(mins) * 60 + float(secs)
                    progress = min(0.99, max(0.01, curr_time / target_dur))
                    self.after(0, self._update_progress, progress, curr_time, target_dur)

            self.process.wait()
            ret = self.process.returncode

            if ret == 0:
                self.after(0, self._on_render_success, out_f)
            else:
                tail_err = "".join(captured_log[-10:]).strip()
                err_detail = f"FFmpeg terminó con código de error.\n\nDetalles:\n{tail_err}" if tail_err else "FFmpeg terminó con código de error."
                self.after(0, self._on_render_failed, err_detail)

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
        self.lbl_status.configure(text="¡Vídeo exportado con éxito en formato universal! 🎉", text_color="#4ade80")
        self.btn_render.configure(state="normal", text="⚡ EXPORTAR VÍDEO CON FORMATO SELECCIONADO")
        self.btn_cancel.configure(state="disabled")

        res = messagebox.askyesno(
            "¡Exportación Finalizada!",
            f"El vídeo ha sido creado correctamente en formato universal compatible (YUV420p):\n\n{out_file}\n\n¿Deseas abrir la carpeta de destino ahora?"
        )
        if res:
            try:
                os.startfile(os.path.dirname(out_file))
            except Exception:
                pass

    def _on_render_failed(self, err_msg):
        self.is_exporting = False
        self.lbl_status.configure(text="El proceso fue cancelado o tuvo un error.", text_color="#f87171")
        self.btn_render.configure(state="normal", text="⚡ EXPORTAR VÍDEO CON FORMATO SELECCIONADO")
        self.btn_cancel.configure(state="disabled")
        messagebox.showerror("Aviso de Exportación", f"Detalle: {err_msg}")

if __name__ == "__main__":
    app = SupremeVideoEditor()
    app.mainloop()
