#!/usr/bin/env python3
"""Sincroniza la carpeta pública de Google Drive con la web.

1. Lee la lista de PDF de la vista embebida pública (embeddedfolderview), sin API key.
2. Descarga cada PDF a pdfs/<ID>.pdf (solo los nuevos o modificados; la versión
   se detecta con Last-Modified + Content-Length de la descarga pública).
3. Borra de pdfs/ los que ya no están en Drive.
4. Escribe files.json (ordenado y estable). Si un PDF no se pudo descargar,
   queda con "local": false y la web abre el enlace de Drive como respaldo.
Falla sin tocar files.json si no puede leer la carpeta.
"""
import html
import json
import os
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

FOLDER_ID = "1EWy2BGDZigiy1-IfBEmVVbxisvDiqkPl"
OUT = "files.json"
PDF_DIR = "pdfs"
MANIFEST = os.path.join(PDF_DIR, ".manifest.json")  # id -> versión del archivo descargado
LIST_URL = "https://drive.google.com/embeddedfolderview?id={}"
DL_URL = "https://drive.usercontent.google.com/download?id={}&export=download&confirm=t"
UA = {"User-Agent": "Mozilla/5.0"}

ENTRY_RE = re.compile(
    r'<div class="flip-entry" id="entry-([\w-]+)".*?<a href="([^"]+)".*?'
    r'flip-entry-list-icon"><img src="([^"]*)".*?flip-entry-title">([^<]*)</div>',
    re.S,
)


def request(url, method="GET", tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA, method=method)
            r = urllib.request.urlopen(req, timeout=120)
            return r
        except Exception as e:  # noqa: BLE001
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def walk(folder_id, prefix="", seen=None):
    seen = seen if seen is not None else set()
    if folder_id in seen:
        return []
    seen.add(folder_id)
    with request(LIST_URL.format(folder_id)) as r:
        page = r.read().decode("utf-8")
    if 'class="flip-entries"' not in page:
        raise RuntimeError(f"Respuesta inesperada para la carpeta {folder_id}")
    files = []
    for fid, href, icon, title in ENTRY_RE.findall(page):
        name = html.unescape(title).strip()
        if "/folders/" in href or "folder" in icon:
            files += walk(fid, f"{prefix}{name}/", seen)
        elif name.lower().endswith(".pdf") or "application/pdf" in icon:
            entry = {"id": fid, "name": name}
            if prefix:
                entry["folder"] = prefix.rstrip("/")
            files.append(entry)
    return files


def version_of(fid):
    """Versión remota: 'Last-Modified|Content-Length' de la descarga pública."""
    with request(DL_URL.format(fid), method="HEAD") as r:
        return f"{r.headers.get('Last-Modified', '')}|{r.headers.get('Content-Length', '')}"


def download(fid, dest):
    with request(DL_URL.format(fid)) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"{fid}: la descarga no es un PDF")
    tmp = dest + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(data)
    os.replace(tmp, dest)


def mirror(entry, manifest):
    fid = entry["id"]
    dest = os.path.join(PDF_DIR, f"{fid}.pdf")
    try:
        ver = version_of(fid)
        if not (os.path.exists(dest) and manifest.get(fid) == ver):
            download(fid, dest)
            print(f"Descargado: {entry['name']}")
        manifest[fid] = ver
        return True
    except Exception as e:  # noqa: BLE001
        print(f"AVISO {entry['name']}: {e}", file=sys.stderr)
        # Si ya teníamos una copia, la seguimos sirviendo.
        return os.path.exists(dest)


def main():
    files = walk(FOLDER_ID)
    if not files:
        sys.exit("No se ha encontrado ningún PDF; no se actualiza files.json")

    os.makedirs(PDF_DIR, exist_ok=True)
    try:
        with open(MANIFEST, encoding="utf-8") as fh:
            manifest = json.load(fh)
    except (OSError, ValueError):
        manifest = {}

    with ThreadPoolExecutor(max_workers=16) as pool:
        ok = list(pool.map(lambda f: mirror(f, manifest), files))
    for f, good in zip(files, ok):
        f["local"] = good
        if good:
            f["v"] = manifest[f["id"]] if f["id"] in manifest else ""

    # Borrar PDF que ya no están en Drive
    keep = {f["id"] for f in files}
    for fn in os.listdir(PDF_DIR):
        if fn.endswith(".pdf") and fn[:-4] not in keep:
            os.remove(os.path.join(PDF_DIR, fn))
            print(f"Eliminado: {fn}")
    manifest = {k: v for k, v in manifest.items() if k in keep}
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)

    files.sort(key=lambda f: (f.get("folder", ""), f["name"].lower(), f["id"]))
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(files, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    total = sum(os.path.getsize(os.path.join(PDF_DIR, f"{f['id']}.pdf")) for f in files if f["local"])
    print(f"{len(files)} PDF en {OUT}; {sum(ok)} en local; {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
