# Supreme Video Editor Studio 🎬

Un potente editor y motor de sincronización de bucles de vídeo con pistas de audio completas, con transiciones cinematográficas automáticas (`xfade`), efectos dinámicos de movimiento (espejo, reversa, viñetas, corrección de color) y exportación acelerada mediante FFmpeg.

Desarrollado para automatizar la creación de videoclips musicales cuando solo dispones de un clip de vídeo corto y una canción completa.

---

## ✨ Características Principales

- **Sincronización Inteligente de Loops**: Calcula con precisión milimétrica la duración de la pista de audio y del vídeo fuente usando `ffprobe`, determinando el número exacto de bucles y transiciones requeridas.
- **Transiciones Cinematográficas Suaves**: Motor de fundidos cruzados (`xfade`) con transiciones dinámicas como `fade`, `dissolve`, `wipeleft`, `wiperight`, `slide`, `zoomin`, etc.
- **Estilos de Variación Creativa**:
  - *Dinámico automático*: Combina espejos (`hflip`), reversa (`reverse`), viñetas cinematográficas y contraste/saturación.
  - *Solo Bucles Limpios*: Transiciones limpias sin alterar el clip original.
  - *Ping-Pong / Boomerang*: Alternancia rítmica hacia adelante y en reversa.
  - *Espejo Alternado*: Alternancia horizontal simétrica.
- **Fade Out Final Sincronizado**: Cierre suave simultáneo para imagen y audio configurable.
- **Resoluciones & Calidad**: Perfiles 1080p Full HD, 4K UHD, 720p, vertical 9:16 (TikTok / Reels / Shorts) y 1:1, control CRF y optimización web streaming (`+faststart`).
- **Interfaz Moderna**: GUI de diseño oscuro construida con `CustomTkinter`, con barra de progreso en vivo y retroalimentación en tiempo real.

---

## 🛠️ Requisitos Previos

- **Python 3.10+**
- **FFmpeg y ffprobe** instalados y añadidos al PATH del sistema.

### Instalación de dependencias:
```bash
pip install customtkinter pillow
```

---

## 🚀 Uso

### Ejecutar desde código:
```bash
python supreme_video_editor.py
```

### Ejecutar en Windows con lanzador:
Hacer doble clic en `Iniciar_Supreme_Editor.bat`.

### Compilar a ejecutable independiente (.exe):
```bash
python -m PyInstaller --noconsole --onefile --name "Supreme_Video_Editor_Studio" --icon="app_icon.ico" --collect-all customtkinter supreme_video_editor.py
```

---

## 👤 Autor

Creado por **vevikils**.
