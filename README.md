# 📅 Calendario de Contenido Veterinario — Skill de IA + automatización con HeyGen

Una **skill para Claude** que genera calendarios mensuales de video corto (Instagram Reels, TikTok y Facebook Reels) para veterinarios que construyen marca personal, más un **script en Python** que convierte esos guiones en videos con avatar usando la API de HeyGen.

De la idea al video publicado, con IA en cada paso.

---

## ⚙️ Qué hace

**1. Planea el mes completo**
- 16–20 publicaciones con ritmo de 4–5 por semana.
- Rota 6 pilares de contenido sin repetir el mismo dos días seguidos.
- Usa fórmulas de hook distintas en cada video.
- Desarrolla el guion completo de los 3–4 videos con más potencial, listo para grabar.

**2. Adapta a cada plataforma**
Mismo video base, con copy y ajustes para TikTok, Instagram y Facebook.

**3. Genera los videos (opcional)**
`heygen_generate.py` manda los guiones a HeyGen y descarga videos con avatar hablando, en lote si quieres todo el mes.

## 🧱 Pilares de contenido

| # | Pilar | Ejemplo |
|---|---|---|
| 1 | Mitos vs. realidad | "Los perros no ven en blanco y negro" |
| 2 | Señales de alerta | "Esto en la caca de tu gato NO es normal" |
| 3 | Casos reales | Historias de consulta, sin datos de pacientes |
| 4 | Cuidado preventivo | "Cómo cepillar los dientes de tu perro en 30 segundos" |
| 5 | Preguntas frecuentes | Lo que la gente pregunta en comentarios y DMs |
| 6 | Opinión veterinaria | Reacciones a tendencias y productos virales |

## 🎬 Estructura de cada guion (30–60 s)

1. **Hook** (0–3 s)
2. **Promesa** (3–8 s)
3. **Valor** (8–45 s): 1 a 3 puntos claros
4. **Cierre + CTA** (últimos 5 s)

## 🤖 Automatización con HeyGen

Controla vía API la velocidad y el tono de voz (con hook más rápido usando el marcador `||`), fondo, subtítulos y formato vertical. La música de fondo se agrega con `ffmpeg` en post-proceso.

```bash
pip install requests

export HEYGEN_API_KEY="tu_api_key"

# Ver avatares y voces disponibles
python veterinary-content-calendar/scripts/heygen_generate.py list-avatars
python veterinary-content-calendar/scripts/heygen_generate.py list-voices

# Generar todos los videos del mes
python veterinary-content-calendar/scripts/heygen_generate.py generate-batch \
    --avatar-id "<avatar_id>" \
    --voice-id "<voice_id>" \
    --scripts-file guiones_del_mes.txt \
    --aspect-ratio 9:16 \
    --captions \
    --output-dir ./videos_mes
```

Tu API key nunca va en el código: se lee de la variable de entorno `HEYGEN_API_KEY` o del parámetro `--api-key`.

## 🚀 Cómo usar la skill

1. Descarga la carpeta [`veterinary-content-calendar/`](./veterinary-content-calendar).
2. Súbela como skill en Claude o colócala en tu carpeta de skills de Claude Code.
3. Pídele: *"Hazme el calendario de contenido de noviembre"*.

Puedes adaptar la sección **Perfil del creador** en `SKILL.md` a tu especialidad y tono.

## 📁 Estructura

```
calendario-contenido-veterinario/
├── README.md
└── veterinary-content-calendar/
    ├── SKILL.md
    └── scripts/
        └── heygen_generate.py
```

## 🔗 Relacionado

[escalera-de-dopamina](https://github.com/aegagrus97/escalera-de-dopamina): framework de 6 niveles para que cada video del calendario retenga y construya audiencia fiel.

---

### 🌎 English summary

A Claude skill that plans a full month of short-form video content (Reels, TikTok) for veterinary personal brands, rotating 6 content pillars with ready-to-record scripts, plus a Python script that turns those scripts into avatar videos via the HeyGen API, in batch.

---

Hecho por [Kat Moctezuma](https://github.com/aegagrus97) · Médica veterinaria · IA aplicada a salud animal
