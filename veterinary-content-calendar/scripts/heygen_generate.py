#!/usr/bin/env python3
"""
heygen_generate.py

Envía guiones de video (generados por el skill veterinary-content-calendar)
a la API de HeyGen para crear videos con avatar hablando.

Requiere: pip install requests --break-system-packages
Requiere una API key de HeyGen (Settings -> API en heygen.com), pasada por
--api-key o variable de entorno HEYGEN_API_KEY.

QUÉ SE PUEDE CONTROLAR VÍA LA API DE HEYGEN (y qué no)
-------------------------------------------------------
SÍ, directamente en la generación del video:
  - Velocidad y tono (pitch) de la voz — incluso puedes hacer el hook (las
    primeras frases) más rápido que el resto del guion, para más energía.
  - Fondo: color sólido, imagen o video (vía URL pública).
  - Subtítulos/captions quemados en el video.
  - Relación de aspecto (9:16 vertical, 16:9, 1:1, etc).

NO lo hace HeyGen — se agrega después, por eso este script incluye un paso
opcional con ffmpeg:
  - Música de fondo / efectos de sonido: no existen en la API de HeyGen.
    Si tienes ffmpeg instalado y le pasas --music-file, este script mezcla
    una pista de audio local por debajo de la narración del avatar.
  - Elementos interactivos (encuestas, stickers, links): eso lo agrega
    Instagram/TikTok cuando subes el video manualmente, no es parte del
    archivo de video en sí — no hay API para eso.

CÓMO FUNCIONA EL HOOK MÁS RÁPIDO
---------------------------------
Si en tu guion separas la primera frase (el hook) del resto usando el
marcador "||", el script genera esa parte con una velocidad de voz más alta
(--hook-speed, default 1.15) y el resto a velocidad normal (--voice-speed,
default 1.0), todo dentro del mismo video (HeyGen soporta múltiples clips
encadenados en un solo request). Si no usas el marcador, todo el guion se
genera a la misma velocidad.

Ejemplo de guion con marcador:
    Esto que le das a tu perro le está haciendo daño.||Sé que se ve tierno...

USO
---

1) Ver tus avatares y voces disponibles (no consume créditos):

    python heygen_generate.py list-avatars
    python heygen_generate.py list-voices

2) Generar UN video a partir de un guion:

    python heygen_generate.py generate \
        --avatar-id "Angela-inblackskirt-20220820" \
        --voice-id "1bd001e7e50f421d891986aad5158bc8" \
        --script "Esto que le das a tu perro le está haciendo daño.||Sé que se ve tierno..." \
        --aspect-ratio 9:16 \
        --background-color "#FAFAFA" \
        --captions \
        --hook-speed 1.15 \
        --voice-speed 1.0 \
        --music-file ./musica_suave.mp3 \
        --output video_lunes.mp4

3) Generar TODOS los guiones de un archivo (separados por una línea "---"),
   útil para procesar el calendario completo del mes:

    python heygen_generate.py generate-batch \
        --avatar-id "Angela-inblackskirt-20220820" \
        --voice-id "1bd001e7e50f421d891986aad5158bc8" \
        --scripts-file guiones_del_mes.txt \
        --aspect-ratio 9:16 \
        --captions \
        --output-dir ./videos_mes

Los guiones deben ser SOLO lo que el avatar va a decir en voz alta (el texto
final del guion completo que genera el skill), no la tabla de calendario.

NOTA: este entorno de Claude no tiene acceso a red saliente, así que no puedo
ejecutar este script por ti aquí mismo — pero es funcional para correrlo en
tu computadora o servidor con conexión a internet.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit(
        "Falta la librería 'requests'. Instálala con:\n"
        "  pip install requests --break-system-packages"
    )

BASE_URL = "https://api.heygen.com"


def get_api_key(cli_key: str | None) -> str:
    key = cli_key or os.environ.get("HEYGEN_API_KEY")
    if not key:
        sys.exit(
            "No encontré una API key. Pásala con --api-key o exporta "
            "HEYGEN_API_KEY antes de correr el script."
        )
    return key


def headers(api_key: str) -> dict:
    return {"X-Api-Key": api_key, "Content-Type": "application/json"}


def list_avatars(api_key: str):
    r = requests.get(f"{BASE_URL}/v2/avatars", headers=headers(api_key))
    r.raise_for_status()
    avatars = r.json()["data"]["avatars"]
    for a in avatars:
        print(f"{a['avatar_id']:<40} {a.get('avatar_name', '')} ({a.get('gender', '')})")
    print(f"\nTotal: {len(avatars)} avatares")


def list_voices(api_key: str):
    r = requests.get(f"{BASE_URL}/v2/voices", headers=headers(api_key))
    r.raise_for_status()
    voices = r.json()["data"]["voices"]
    for v in voices:
        print(f"{v['voice_id']:<36} {v.get('name', '')} ({v.get('language', '')})")
    print(f"\nTotal: {len(voices)} voces")


ASPECT_TO_DIMENSION = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}


def build_background(background_color: str | None, background_url: str | None,
                      background_type: str) -> dict:
    """background_type: 'image' o 'video' si se pasa background_url;
    si no, fondo de color sólido."""
    if background_url:
        bg = {"type": background_type, "url": background_url}
        if background_type == "video":
            bg["play_style"] = "loop"
        return bg
    return {"type": "color", "value": background_color or "#FAFAFA"}


def split_hook_and_body(script_text: str) -> tuple[str, str | None]:
    """Si el guion trae el marcador '||', separa hook (antes) de cuerpo
    (después). Si no, devuelve todo como un solo bloque sin cuerpo separado."""
    if "||" in script_text:
        hook, body = script_text.split("||", 1)
        return hook.strip(), body.strip()
    return script_text.strip(), None


def create_video(api_key: str, avatar_id: str, voice_id: str, script_text: str,
                  aspect_ratio: str = "9:16", background_color: str | None = None,
                  background_url: str | None = None, background_type: str = "image",
                  captions: bool = False, hook_speed: float = 1.15,
                  voice_speed: float = 1.0, pitch: int = 0) -> str:
    """Dispara la generación de un video y devuelve el video_id.

    Si el guion trae el marcador '||', el hook se genera a hook_speed y el
    resto a voice_speed, como dos clips encadenados dentro del mismo video.
    """
    width, height = ASPECT_TO_DIMENSION.get(aspect_ratio, (1080, 1920))
    background = build_background(background_color, background_url, background_type)

    hook, body = split_hook_and_body(script_text)

    def make_clip(text: str, speed: float) -> dict:
        return {
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal",
            },
            "voice": {
                "type": "text",
                "input_text": text,
                "voice_id": voice_id,
                "speed": speed,
                "pitch": pitch,
            },
            "background": background,
        }

    video_inputs = [make_clip(hook, hook_speed)]
    if body:
        video_inputs.append(make_clip(body, voice_speed))

    payload = {
        "video_inputs": video_inputs,
        "dimension": {"width": width, "height": height},
        "aspect_ratio": aspect_ratio,
        "caption": captions,
    }
    r = requests.post(f"{BASE_URL}/v2/video/generate", headers=headers(api_key),
                       data=json.dumps(payload))
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        sys.exit(f"HeyGen devolvió un error: {data['error']}")
    return data["data"]["video_id"]


def wait_for_video(api_key: str, video_id: str, poll_seconds: int = 5,
                    timeout_seconds: int = 600) -> str:
    """Espera a que el video termine de renderizar y devuelve la video_url."""
    elapsed = 0
    while elapsed < timeout_seconds:
        r = requests.get(f"{BASE_URL}/v1/video_status.get?video_id={video_id}",
                          headers=headers(api_key))
        r.raise_for_status()
        status_data = r.json()["data"]
        status = status_data["status"]
        if status == "completed":
            return status_data["video_url"]
        if status == "failed":
            sys.exit(f"La generación falló: {status_data.get('error')}")
        print(f"  [{video_id}] estado: {status} — esperando...")
        time.sleep(poll_seconds)
        elapsed += poll_seconds
    sys.exit(f"Tiempo de espera agotado para el video {video_id}")


def download_video(video_url: str, output_path: str):
    r = requests.get(video_url, stream=True)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  Guardado en: {output_path}")


def mix_background_music(video_path: str, music_path: str, music_volume: float = 0.15):
    """Mezcla una pista de audio local por debajo de la narración del video,
    usando ffmpeg (debe estar instalado: https://ffmpeg.org/download.html).
    Sobrescribe video_path con la versión mezclada."""
    import shutil
    import subprocess

    if not shutil.which("ffmpeg"):
        print("  ⚠️  ffmpeg no está instalado — omito la música de fondo. "
              "Instálalo (ej. 'brew install ffmpeg' o 'apt install ffmpeg') "
              "y vuelve a correr con --music-file.")
        return

    tmp_output = video_path + ".with_music.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", music_path,
        "-filter_complex",
        f"[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-shortest",
        tmp_output,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  ffmpeg falló al mezclar música: {result.stderr[-500:]}")
        return
    shutil.move(tmp_output, video_path)
    print(f"  🎵 Música de fondo mezclada en: {video_path}")


def cmd_generate(args):
    api_key = get_api_key(args.api_key)
    print("Enviando guion a HeyGen...")
    video_id = create_video(
        api_key, args.avatar_id, args.voice_id, args.script,
        aspect_ratio=args.aspect_ratio,
        background_color=args.background_color,
        background_url=args.background_url,
        background_type=args.background_type,
        captions=args.captions,
        hook_speed=args.hook_speed,
        voice_speed=args.voice_speed,
        pitch=args.pitch,
    )
    print(f"Video en proceso (id: {video_id}). Renderizando...")
    video_url = wait_for_video(api_key, video_id)
    download_video(video_url, args.output)
    if args.music_file:
        mix_background_music(args.output, args.music_file, args.music_volume)


def split_scripts(raw_text: str) -> list[str]:
    """Divide el archivo de guiones. Soporta separador '---' entre guiones,
    o si no hay separador, un guion por línea no vacía."""
    if "---" in raw_text:
        parts = [p.strip() for p in raw_text.split("---")]
    else:
        parts = [line.strip() for line in raw_text.splitlines()]
    return [p for p in parts if p]


def cmd_generate_batch(args):
    api_key = get_api_key(args.api_key)
    raw_text = Path(args.scripts_file).read_text(encoding="utf-8")
    scripts = split_scripts(raw_text)
    if not scripts:
        sys.exit("No encontré guiones en el archivo.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Encontré {len(scripts)} guion(es). Generando uno por uno...\n")
    for i, script_text in enumerate(scripts, start=1):
        print(f"[{i}/{len(scripts)}] Enviando guion...")
        video_id = create_video(
            api_key, args.avatar_id, args.voice_id, script_text,
            aspect_ratio=args.aspect_ratio,
            background_color=args.background_color,
            background_url=args.background_url,
            background_type=args.background_type,
            captions=args.captions,
            hook_speed=args.hook_speed,
            voice_speed=args.voice_speed,
            pitch=args.pitch,
        )
        video_url = wait_for_video(api_key, video_id)
        output_path = output_dir / f"video_{i:02d}.mp4"
        download_video(video_url, str(output_path))
        if args.music_file:
            mix_background_music(str(output_path), args.music_file, args.music_volume)
        print()

    print(f"Listo. {len(scripts)} videos guardados en {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Generar videos de HeyGen desde guiones")
    parser.add_argument("--api-key", help="API key de HeyGen (o usa HEYGEN_API_KEY)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-avatars", help="Listar avatares disponibles")
    sub.add_parser("list-voices", help="Listar voces disponibles")

    def add_common_flags(p):
        p.add_argument("--aspect-ratio", default="9:16", choices=["9:16", "16:9", "1:1", "4:5"],
                        help="9:16 vertical (default, ideal Reels/TikTok)")
        p.add_argument("--background-color", default="#FAFAFA",
                        help="Color de fondo en hex, usado si no das --background-url")
        p.add_argument("--background-url", default=None,
                        help="URL pública de imagen o video para el fondo")
        p.add_argument("--background-type", default="image", choices=["image", "video"],
                        help="Tipo de --background-url (solo aplica si lo usas)")
        p.add_argument("--captions", action="store_true",
                        help="Quemar subtítulos en el video")
        p.add_argument("--hook-speed", type=float, default=1.15,
                        help="Velocidad de voz para la parte antes del marcador '||' (default 1.15)")
        p.add_argument("--voice-speed", type=float, default=1.0,
                        help="Velocidad de voz para el resto del guion (default 1.0)")
        p.add_argument("--pitch", type=int, default=0,
                        help="Tono de voz, entero (0 = default de la voz)")
        p.add_argument("--music-file", default=None,
                        help="Ruta a un archivo de audio local para mezclar como música de fondo (requiere ffmpeg)")
        p.add_argument("--music-volume", type=float, default=0.15,
                        help="Volumen relativo de la música (0.0-1.0, default 0.15 para no tapar la voz)")

    p_gen = sub.add_parser("generate", help="Generar un solo video")
    p_gen.add_argument("--avatar-id", required=True)
    p_gen.add_argument("--voice-id", required=True)
    p_gen.add_argument("--script", required=True,
                        help="Texto que dirá el avatar. Usa '||' para separar hook del resto, ej: 'Hook aquí.||Resto del guion...'")
    p_gen.add_argument("--output", default="video.mp4")
    add_common_flags(p_gen)

    p_batch = sub.add_parser("generate-batch", help="Generar varios videos desde un archivo")
    p_batch.add_argument("--avatar-id", required=True)
    p_batch.add_argument("--voice-id", required=True)
    p_batch.add_argument("--scripts-file", required=True,
                          help="Archivo .txt con guiones separados por '---' (usa '||' dentro de cada uno para marcar el hook)")
    p_batch.add_argument("--output-dir", default="./videos_generados")
    add_common_flags(p_batch)

    args = parser.parse_args()

    if args.command == "list-avatars":
        list_avatars(get_api_key(args.api_key))
    elif args.command == "list-voices":
        list_voices(get_api_key(args.api_key))
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "generate-batch":
        cmd_generate_batch(args)


if __name__ == "__main__":
    main()
