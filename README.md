# Buscador de Platos

Aplicación web minimalista para buscar fichas técnicas (PDF) almacenadas en Google Drive.

## Características

- Búsqueda por **código** o **nombre** del plato
- Sincronización automática con la carpeta de Drive
- Diseño elegante, rápido y optimizado para móviles
- Ideal para QR / NFC: un solo enlace para todos los trabajadores

## Cómo funciona la sincronización

No hace falta ninguna API Key de Google.

- La carpeta de Drive ([Fichas técnicas en pdf](https://drive.google.com/drive/folders/1EWy2BGDZigiy1-IfBEmVVbxisvDiqkPl)) debe estar compartida como **Cualquier persona con el enlace → Lector** (ya lo está).
- Una GitHub Action (`.github/workflows/sync-drive.yml`) lee la carpeta **cada ~10 minutos**, regenera `files.json` con la lista de PDF, descarga una copia de los PDF nuevos o modificados y vuelve a publicar la web si algo ha cambiado.
- Los PDF se sirven desde la propia web (`/pdfs/<ID>.pdf`), así que en el móvil se abren directamente, sin pedir cuenta de Google. Las copias no se guardan en el repositorio, solo en la web publicada.
- Se puede forzar una sincronización al momento desde **Actions → Sincronizar Drive y publicar → Run workflow**.
- La web se publica con GitHub Pages en:

**https://antoniomunozindio2.github.io/buscador-platos/**

## Uso

1. Genera un código QR o configura una etiqueta NFC que apunte a la URL de GitHub Pages
2. El trabajador escanea / acerca el móvil
3. Escribe el código (ej. `490`) o parte del nombre
4. Pulsa **Abrir** para ver el PDF

## Gestión de documentos

Solo tienes que gestionar los PDF desde Google Drive:

- Añadir un PDF nuevo → aparece automáticamente (en unos 10 minutos)
- Eliminar un PDF → desaparece
- Sustituir un PDF → se abre la versión nueva
- Cambiar el nombre → se refleja en el buscador

**Formato recomendado de nombre:** `CÓDIGO - Nombre del plato.pdf`

Ejemplo: `490 - Lentejas con verduras.pdf`
