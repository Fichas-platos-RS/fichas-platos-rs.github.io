# Buscador de Platos

Aplicación web minimalista para buscar fichas técnicas (PDF) almacenadas en Google Drive.

## Características

- Búsqueda por **código** o **nombre** del plato
- Sincronización automática con la carpeta de Drive
- Diseño elegante, rápido y optimizado para móviles
- Ideal para QR / NFC: un solo enlace para todos los trabajadores

## Configuración necesaria (una sola vez)

### 1. Haz pública la carpeta de Drive

1. Abre la carpeta: [Fichas técnicas en pdf](https://drive.google.com/drive/folders/1EWy2BGDZigiy1-IfBEmVVbxisvDiqkPl)
2. Haz clic en **Compartir**
3. Cambia el acceso a **Cualquier persona con el enlace** → **Lector**
4. Copia el enlace (ya lo tienes)

### 2. Crea una API Key de Google

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo (o usa uno existente)
3. Activa la **Google Drive API**
4. Ve a **Credenciales** → **Crear credenciales** → **Clave de API**
5. (Recomendado) Restringe la clave solo a la Google Drive API
6. Copia la clave

### 3. Añade la API Key al proyecto

1. Edita el archivo `index.html`
2. Busca la línea:
   ```js
   const API_KEY = 'YOUR_GOOGLE_API_KEY';
   ```
3. Sustituye `YOUR_GOOGLE_API_KEY` por tu clave real
4. Haz commit y push (o edita directamente en GitHub)

### 4. Activa GitHub Pages

1. Ve a **Settings** → **Pages** del repositorio
2. Source: **Deploy from a branch**
3. Branch: `main` / `/ (root)`
4. Guarda

En unos minutos la web estará disponible en:

**https://antoniomunozindio2.github.io/buscador-platos/**

## Uso

1. Genera un código QR o configura una etiqueta NFC que apunte a la URL de GitHub Pages
2. El trabajador escanea / acerca el móvil
3. Escribe el código (ej. `490`) o parte del nombre
4. Pulsa **Abrir** para ver el PDF

## Gestión de documentos

Solo tienes que gestionar los PDF desde Google Drive:

- Añadir un PDF nuevo → aparece automáticamente
- Eliminar un PDF → desaparece
- Sustituir un PDF → se abre la versión nueva
- Cambiar el nombre → se refleja en el buscador

**Formato recomendado de nombre:** `CÓDIGO - Nombre del plato.pdf`

Ejemplo: `490 - Lentejas con verduras.pdf`
