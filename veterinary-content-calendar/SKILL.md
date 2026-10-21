---
name: veterinary-content-calendar
description: Genera calendarios mensuales de contenido para marca personal de un veterinario/a enfocados en Instagram Reels, TikTok y Facebook Reels, con guiones de video corto (aparición en cámara), tono cercano y casual, y objetivo de crecer alcance/seguidores. Usa este skill siempre que el usuario pida "calendario de contenido", "ideas de video", "guiones para redes", "contenido para TikTok/Instagram/Facebook" relacionado con veterinaria, mascotas, salud animal, o su marca personal como veterinario. También úsalo si pide "más contenido", "el calendario del próximo mes", o variaciones del mismo pedido recurrente.
---

# Calendario de Contenido Viral — Veterinaria

Genera calendarios de contenido de video corto para un/a veterinario/a que construye marca personal, con el objetivo principal de crecer alcance y seguidores en Instagram, TikTok y Facebook.

## Perfil del creador (fijo, no preguntar de nuevo salvo que el usuario indique cambios)

- **Nicho**: veterinaria / salud y cuidado animal
- **Formato**: aparición en cámara hablando directo
- **Tono**: cercano y casual, como hablarle a un amigo dueño de mascota — nada de jerga técnica sin explicar, cero acartonado
- **Objetivo**: alcance y crecimiento de seguidores (no ventas directas ni conversión — el CTA es engagement/seguir, no "agenda tu cita")
- **Frecuencia por defecto**: calendario mensual (genera el mes completo salvo que pidan otra cosa)
- **Plataformas**: Instagram Reels, TikTok, Facebook Reels (mismo video base, se adapta el copy/hashtags por plataforma)

## Pilares de contenido (rotar entre ellos, no repetir el mismo pilar 2 días seguidos)

1. **Mitos vs. realidad** — desmentir creencias populares sobre mascotas ("los perros no ven en blanco y negro", "los gatos no necesitan vacunas si no salen", etc.)
2. **Señales de alerta** — síntomas que los dueños ignoran y no deberían ("por qué tu perro lame tanto sus patas", "esto en la caca de tu gato NO es normal")
3. **Casos reales / anécdotas de consulta** — historias breves y humanas de la clínica (sin romper confidencialidad, generalizadas)
4. **Cuidado preventivo práctico** — tips accionables ("cómo cepillar los dientes de tu perro en 30 segundos")
5. **Preguntas frecuentes de dueños** — responder lo que la gente pregunta en comentarios/DMs
6. **Reacciones/opinión veterinaria** — reaccionar a tendencias virales de mascotas, productos, o noticias, dando la perspectiva profesional

## Fórmulas de hook (primeros 3 segundos, elegir una distinta por video)

- Contradicción: "Esto que haces con tu perro le está haciendo daño"
- Número + curiosidad: "3 señales de que tu gato tiene dolor y no lo sabes"
- Pregunta directa a cámara: "¿Tu perro hace esto? Te explico qué significa"
- Historia gancho: "Hoy llegó un paciente que casi me hace llorar"
- Urgencia/alerta: "Si tu mascota hace esto, llévala YA al veterinario"

Evitar siempre: "Hola, hoy les voy a hablar de..." — mata el hook.

## Estructura de cada guion (30-60 segundos)

1. **Hook** (0-3s): una de las fórmulas de arriba
2. **Promesa** (3-8s): qué va a aprender el espectador
3. **Valor** (8-45s): 1 a 3 puntos claros, lenguaje simple, ejemplos concretos con mascotas
4. **Cierre + CTA** (últimos 5s): variar entre "sígueme para más tips como este", pregunta abierta para comentarios, o gancho al siguiente video de la serie

## Formato de salida

Genera una tabla con el calendario del mes (o el rango solicitado) con estas columnas:

| Día | Pilar | Hook | Guion breve (puntos clave) | CTA | Notas de plataforma |

Después de la tabla, desarrolla el **guion completo** de los 3-4 videos más fuertes del mes (los de mayor potencial viral) con el texto exacto a decir, listo para grabar.

## Notas de adaptación por plataforma

| Plataforma | Ajuste |
|---|---|
| TikTok | Copy corto, tendencias de sonido si aplica, texto en pantalla resumiendo el punto clave |
| Instagram Reels | Mismo video, cuidar el primer frame como miniatura, subtítulos siempre |
| Facebook Reels | Copy un poco más descriptivo, el público es más adulto — evitar jerga de internet |

## Integración con HeyGen (generar los videos automáticamente)

El skill incluye `scripts/heygen_generate.py`, que toma los guiones ya escritos
y los manda a la API de HeyGen para generar videos con avatar hablando (ideal
si el usuario no quiere grabarse él mismo, o quiere versiones adicionales).

Usar este script cuando el usuario pida explícitamente "mándalo a HeyGen",
"genera el video", "crea el avatar", o similar — no ejecutarlo automáticamente
solo por generar un calendario.

Requisitos antes de correrlo:
- El usuario necesita su propia API key de HeyGen (Settings → API en heygen.com)
- Necesita `avatar_id` y `voice_id` — se obtienen con:
  `python scripts/heygen_generate.py list-avatars`
  `python scripts/heygen_generate.py list-voices`
- Instalar dependencia: `pip install requests --break-system-packages`
- Opcional (solo para música de fondo): tener `ffmpeg` instalado

### Qué controla la API de HeyGen (y qué no)
SÍ vía API: velocidad y tono de voz (incluyendo hook más rápido que el
resto usando el marcador `||` en el guion), fondo (color/imagen/video),
subtítulos quemados, aspect ratio.
NO vía API — se agrega aparte: música de fondo / efectos de sonido (el
script lo resuelve con `ffmpeg` en post-proceso si se pasa `--music-file`)
y elementos interactivos (encuestas, stickers, links), que se agregan
manualmente al publicar en Instagram/TikTok, no son parte del archivo de video.

Al escribir guiones para este script, separar el hook (primera frase) del
resto con `||` si se quiere que suene más rápido/con más energía, ej:
`"Esto que le das a tu perro le está haciendo daño.||Sé que se ve tierno..."`

Uso típico (un solo video, con todas las opciones):
```
python scripts/heygen_generate.py generate \
    --avatar-id "<avatar_id>" \
    --voice-id "<voice_id>" \
    --script "Hook aquí.||Resto del guion..." \
    --aspect-ratio 9:16 \
    --background-color "#FAFAFA" \
    --captions \
    --hook-speed 1.15 \
    --voice-speed 1.0 \
    --music-file ./musica_suave.mp3 \
    --output video_lunes.mp4
```

Para generar varios videos del calendario de una sola vez, guardar los
guiones completos (solo el texto hablado, no la tabla) en un .txt separados
por una línea `---`, cada uno con su marcador `||` si aplica, y usar:
```
python scripts/heygen_generate.py generate-batch \
    --avatar-id "<avatar_id>" \
    --voice-id "<voice_id>" \
    --scripts-file guiones_del_mes.txt \
    --aspect-ratio 9:16 \
    --captions \
    --output-dir ./videos_mes
```

Nota: el entorno de Claude.ai no tiene salida a internet, así que el script
no se puede ejecutar dentro de la conversación — es para que el usuario lo
corra en su propia máquina con su API key.

## Al generar el calendario

- No repetir el mismo pilar en días consecutivos
- Variar las fórmulas de hook — no usar la misma dos veces en el mes
- Si el usuario menciona una fecha o temporada específica (ej. campaña de vacunación, verano, adopciones), incorporar contenido relevante a esa fecha
- Si el usuario no especifica cuántos días/semanas, asumir calendario mensual completo (entre 16-20 publicaciones, ritmo de 4-5 por semana)
- Preguntar solo si falta información crítica (ej. el usuario nunca mencionó su especialidad dentro de veterinaria — perros/gatos, exóticos, grandes animales, etc.) — si no la sabes, asume perros y gatos como default y acláralo
