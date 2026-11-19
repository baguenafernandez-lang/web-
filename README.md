# baaaguenaaa

Web de Álvaro Bàguena — fotógrafo deportivo, de bodas y eventos en València.
Castellano en la raíz y valenciano en `va/`.

## Cómo se edita

Todo el contenido (textos, fotos, preguntas frecuentes) está en `build.py`.
Cada texto aparece en las dos lenguas: `T("castellano", "valencià")`.

```bash
python3 build.py              # regenera los HTML, sitemap.xml y robots.txt
python3 build.py --imagenes   # además, optimiza las fotos de originales/ en img/
```

No edites los `.html` a mano: se sobrescriben al ejecutar `build.py`.
Los estilos están en `assets/site.css` y el JavaScript en `assets/site.js`.

## Fotos

1. Copia la foto original a `originales/` (no se sube a GitHub).
2. Añádela a la lista `SPORT`, `WEDDING` o `EVENTS` de `build.py`, con su texto alternativo en las dos lenguas.
3. Ejecuta `python3 build.py --imagenes`.

## Formulario

Funciona con [FormSubmit](https://formsubmit.co): los mensajes llegan al email configurado en `build.py`.
El primer envío manda un email de activación que hay que confirmar una vez.

## Dominio propio

Cambia `BASE_URL` en `build.py`, vuelve a ejecutarlo y añade el archivo `CNAME` con el dominio.
