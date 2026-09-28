# Supreme Video Editor Studio v3.0 🎬

Un potente editor y motor de sincronización de bucles de vídeo con pistas de audio completas, con transiciones cinematográficas automáticas (`xfade`), efectos dinámicos de movimiento (espejo, reversa, viñetas, corrección de color), generador de ondas de audio automáticas y exportación acelerada mediante FFmpeg.

Desarrollado para automatizar la creación de videoclips musicales cuando solo dispones de un clip de vídeo corto y una canción completa, o directamente solo de la pista de audio.

---

## ✨ Novedades de la Versión 3.0 (v3.0)

- **Soporte de Renderizado Sólo Audio / Visualizer Automático**: Ahora permite generar vídeos directamente con una pista de audio (MP3/WAV) aunque no se aporte vídeo, generando un fondo dinámico con onda de audio animada en tiempo real (`showwaves`).
- **Selector de Inicio de Canción en Tiempo Exacto**: Escoge el punto de inicio en formato `MM:SS` (ej. `01:15`) o segundos para extraer la mejor parte para Reels o TikToks.
- **Control de Zoom y Reencuadre (50% a 250%)**: Acercamiento o alejamiento suave para adaptar tomas horizontales a formatos verticales (9:16) y cuadrados (1:1).
- **Compatibilidad Universal YUV420p**: Todos los perfiles exportan en formato píxel `yuv420p` y flag `+faststart` para asegurar reproducción perfecta en cualquier reproductor (QuickTime, Windows Media, navegadores, iOS y Android).
- **Suite de Metadatos y SEO para YouTube**: Generador de títulos atractivos con emojis, descripciones completas, créditos y hashtags/etiquetas automáticas listas para copiar con 1 clic.
- **Registro Detallado de Errores FFmpeg**: Diagnóstico visible de la salida de FFmpeg ante cualquier imprevisto en el proceso.

---

## 🚀 Características Principales

- **Sincronización Inteligente de Loops**: Calcula con precisión milimétrica la duración de la pista de audio y del vídeo fuente usando `ffprobe`, determinando el número exacto de bucles y transiciones requeridas.
- **36+ Transiciones Cinematográficas Suaves**: Motor de fundidos cruzados (`xfade`) con transiciones dinámicas como `fade`, `dissolve`, `wipeleft`, `wiperight`, `slide`, `zoomin`, `circleopen`, `radial`, etc.
- **Estilos de Variación Creativa**:
  - *Dinámico automático*: Combina espejos (`hflip`), reversa (`reverse`), viñetas cinematográficas y contraste/saturación.
  - *Solo Bucles Limpios*: Transiciones limpias sin alterar el clip original.
  - *Ping-Pong / Boomerang*: Alternancia rítmica hacia adelante y en reversa.
  - *Espejo Alternado*: Alternancia horizontal simétrica.
- **Presets de Plataformas**:
  - *YouTube Visualizer*: 1080p / 4K 16:9 con duración completa de canción y fundido suave.
  - *Spotify Canvas*: 9:16 vertical de 7.5 segundos sin audio, optimizado en loop.
  - *TikTok & Instagram Reels*: 9:16 vertical de 15s o 30s punchy.
  - *Instagram Post / Cuadrado (1:1)*: 1080x1080.
- **Superposición de Texto Estilizado**: Incorpora título de la canción y nombre de artistas con sombras, diferentes posiciones (inferior, superior, centro) y temporización automática (8s, 15s o todo el vídeo).
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

## 💻 Uso

### Ejecutar desde código:
```bash
python supreme_video_editor.py
```

### Ejecutar en Windows con lanzador:
Hacer doble clic en `Iniciar_Supreme_Editor.bat`.

### Compilar a ejecutable independiente (.exe):
```bash
python -m PyInstaller --noconsole --onefile --clean --name "Supreme_Video_Editor_Studio_v3.0" --icon="app_icon.ico" --collect-all customtkinter supreme_video_editor.py
```

---

## 👤 Autor

Creado por **vevikils**.
