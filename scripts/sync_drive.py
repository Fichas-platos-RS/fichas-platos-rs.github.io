#!/usr/bin/env python3
"""Genera files.json con los PDF de la carpeta pública de Google Drive.

Usa la vista embebida pública (embeddedfolderview), que no necesita API key.
Recorre subcarpetas si las hay. Falla (sin tocar files.json) si no puede leer.
"""
import html
import json
import re
import sys
import urllib.request

FOLDER_ID = "1EWy2BGDZigiy1-IfBEmVVbxisvDiqkPl"
OUT = "files.json"
URL = "https://drive.google.com/embeddedfolderview?id={}"

ENTRY_RE = re.compile(
    r'<div class="flip-entry" id="entry-([\w-]+)".*?<a href="([^"]+)".*?'
    r'flip-entry-list-icon"><img src="([^"]*)".*?flip-entry-title">([^<]*)</div>',
    re.S,
)


def fetch(folder_id):
    req = urllib.request.Request(URL.format(folder_id), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status != 200:
            raise RuntimeError(f"HTTP {r.status} en carpeta {folder_id}")
        return r.read().decode("utf-8")


def walk(folder_id, prefix="", seen=None):
    seen = seen if seen is not None else set()
    if folder_id in seen:
        return []
    seen.add(folder_id)
    page = fetch(folder_id)
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


def main():
    files = walk(FOLDER_ID)
    if not files:
        sys.exit("No se ha encontrado ningún PDF; no se actualiza files.json")
    files.sort(key=lambda f: (f.get("folder", ""), f["name"].lower(), f["id"]))
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(files, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print(f"{len(files)} PDF escritos en {OUT}")


if __name__ == "__main__":
    main()
