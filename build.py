#!/usr/bin/env python3
"""Genera la web estática (castellano + valenciano) de Álvaro Bàguena.

Uso:
    python3 build.py              # genera los HTML, sitemap y robots
    python3 build.py --imagenes   # además, optimiza las fotos de originales/ -> img/

Todo el contenido (textos, fotos, FAQ) está en este archivo. Para cambiar un texto,
busca la frase y edítala en las dos lenguas: T("castellano", "valencià").
Las fotos originales van en originales/ (no se suben a GitHub, solo las optimizadas).
"""
import html, json, os, subprocess, sys, urllib.parse

# ---------------------------------------------------------------- CONFIGURACIÓN
BASE_URL = "https://baguenafernandez-lang.github.io/baaaguenaaa"  # cambia al usar dominio propio
NAME = "Álvaro Bàguena"
EMAIL = "baguenafernandez@gmail.com"
PHONE = "+34 601 758 935"
PHONE_RAW = "34601758935"
INSTAGRAM = "https://www.instagram.com/baaaguena/"
BEHANCE = "https://www.behance.net/baaaguena"
LINKEDIN = "https://www.linkedin.com/in/b%C3%A0guena-fern%C3%A1ndez"
FORM_ACTION = f"https://formsubmit.co/{EMAIL}"

ROOT = os.path.dirname(os.path.abspath(__file__))
LANG = "es"


def T(es, va):
    return es if LANG == "es" else va


def e(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- PÁGINAS
PAGES = {
    "home": {"es": "index.html", "va": "va/index.html"},
    "deporte": {"es": "fotografo-deportivo-valencia.html", "va": "va/fotograf-esportiu-valencia.html"},
    "eventos": {"es": "fotografo-eventos-valencia.html", "va": "va/fotograf-esdeveniments-valencia.html"},
    "contacto": {"es": "contacto.html", "va": "va/contacte.html"},
    "gracias": {"es": "gracias.html", "va": "va/gracies.html"},
    "privacidad": {"es": "privacidad.html", "va": "va/privacitat.html"},
}


def path_of(page, lang=None):
    return PAGES[page][lang or LANG]


def href(page, lang=None):
    """Enlace relativo desde la página actual (que está en LANG)."""
    target = path_of(page, lang)
    prefix = "../" if LANG == "va" else ""
    rel = prefix + target
    if rel.startswith("../va/"):
        rel = rel[6:]
    return rel


def url_of(page, lang):
    p = path_of(page, lang)
    if p.endswith("index.html"):
        p = p[: -len("index.html")]
    return f"{BASE_URL}/{p}"


def asset(p):
    return ("../" if LANG == "va" else "") + p


# ---------------------------------------------------------------- IMÁGENES
# (archivo original en originales/, nombre de salida, alt castellano, alt valencià)
SPORT = [
    ("foto-carrusel-3.webp", "deporte/futbolistas-celebracion", "Dos futbolistas celebrando juntos tras un partido", "Dos futbolistes celebrant junts després d'un partit"),
    ("galeria3.webp", "deporte/baloncesto-lanzamiento", "Lanzamiento a canasta en un partido de baloncesto femenino", "Llançament a cistella en un partit de bàsquet femení"),
    ("galeria10.webp", "deporte/entrenador-banda", "Entrenador dando instrucciones desde la banda, en blanco y negro", "Entrenador donant instruccions des de la banda, en blanc i negre"),
    ("foto-carrusel-2.webp", "deporte/jugadora-valencia-basket", "Jugadora de Valencia Basket en la pista", "Jugadora del València Basket a la pista"),
    ("galeria2.webp", "deporte/duelo-futbol", "Duelo por el balón en un partido de fútbol", "Duel per la pilota en un partit de futbol"),
    ("galeria5.webp", "deporte/esgrima-accion", "Esgrimista en plena acción durante un asalto", "Esgrimista en plena acció durant un assalt"),
    ("galeria18.webp", "deporte/jugadora-baloncesto-retrato", "Retrato de una jugadora de baloncesto en la pista", "Retrat d'una jugadora de bàsquet a la pista"),
    ("foto-carrusel-1.webp", "deporte/jugador-retrato", "Retrato de perfil de un jugador joven", "Retrat de perfil d'un jugador jove"),
    ("galeria9.webp", "deporte/esgrima-combate", "Combate de esgrima en un pabellón", "Combat d'esgrima en un pavelló"),
    ("galeria12.webp", "deporte/estadio-blanco-negro", "Estadio iluminado, en blanco y negro", "Estadi il·luminat, en blanc i negre"),
    ("galeria6.webp", "deporte/mascota-baloncesto", "Mascota animando al público en un partido de baloncesto", "Mascota animant el públic en un partit de bàsquet"),
]
WEDDING = [
    ("_MG_1349.jpg", "bodas/finca-mediterranea", "Finca mediterránea donde se celebró la boda", "Finca mediterrània on es va celebrar el casament"),
    ("B14A5701.jpg", "bodas/ceremonia-arco", "Ceremonia civil bajo un arco con vegetación", "Cerimònia civil sota un arc amb vegetació"),
    ("B14A4789.jpg", "bodas/invitada-perfil", "Invitada de perfil durante la ceremonia", "Convidada de perfil durant la cerimònia"),
    ("B14A4940.jpg", "bodas/novio-emocionado", "El novio sonríe emocionado durante la ceremonia", "El nuvi somriu emocionat durant la cerimònia"),
    ("B14A5172-Topaz-Sharpen-Auto.jpg", "bodas/nino-alianzas", "Un niño entrega las alianzas a los novios", "Un xiquet entrega les aliances als nuvis"),
    ("B14A5283.jpg", "bodas/intercambio-alianzas", "Intercambio de alianzas", "Intercanvi d'aliances"),
    ("_MG_1431.jpg", "bodas/momento-ceremonia", "Momento emotivo de la ceremonia en el porche", "Moment emotiu de la cerimònia al porxo"),
    ("B14A6147.jpg", "bodas/novios-jardin-velo", "Los novios en el jardín con el velo extendido", "Els nuvis al jardí amb el vel estés"),
    ("B14A6440.jpg", "bodas/novia-velo-largo", "La novia de espaldas con un velo largo frente a la casa", "La núvia d'esquena amb un vel llarg davant de la casa"),
    ("B14A6346.jpg", "bodas/ramo-anillo", "Detalle del ramo de novia y el anillo", "Detall del ram de núvia i l'anell"),
    ("B14A6710.jpg", "bodas/llegada-coctel", "Los novios llegan al cóctel entre los invitados", "Els nuvis arriben al còctel entre els convidats"),
    ("_MG_2568.jpg", "bodas/novia-baila-velo", "La novia baila con el velo en el cóctel", "La núvia balla amb el vel al còctel"),
    ("_MG_2703.jpg", "bodas/novia-saluda-jardin", "La novia saluda con el brazo en alto en el jardín", "La núvia saluda amb el braç en alt al jardí"),
    ("B14A7368.jpg", "bodas/entrada-banquete", "La novia levanta el ramo al entrar al banquete", "La núvia alça el ram en entrar al banquet"),
    ("_MG_2838.jpg", "bodas/servilletas-banquete", "Invitados agitando servilletas en el banquete", "Convidats agitant tovallons al banquet"),
    ("B14A8126.jpg", "bodas/novia-riendo-fiesta", "La novia ríe durante la fiesta", "La núvia riu durant la festa"),
    ("B14A8131.jpg", "bodas/abrazo-fiesta", "Abrazo de la novia con un invitado en la fiesta", "Abraçada de la núvia amb un convidat a la festa"),
    ("B14A8281.jpg", "bodas/novia-amiga-atardecer", "La novia abraza a una amiga al atardecer", "La núvia abraça una amiga a la posta de sol"),
    ("B14A8205.jpg", "bodas/novia-bailando-bn", "La novia bailando en la pista, en blanco y negro", "La núvia ballant a la pista, en blanc i negre"),
    ("_MG_2356.jpg", "bodas/novia-cielo-azul", "La novia levanta el brazo contra el cielo azul", "La núvia alça el braç contra el cel blau"),
]
EVENTS = [
    ("galeria11.webp", "eventos/concierto-directo", "Concierto en directo con luz de escenario", "Concert en directe amb llum d'escenari"),
    ("galeria4.webp", "eventos/bateria-directo", "Batería tocando en directo, en blanco y negro", "Bateria tocant en directe, en blanc i negre"),
    ("galeria20.webp", "eventos/artista-humo", "Artista entre humo durante un concierto", "Artista entre fum durant un concert"),
]
CLIENTS = [
    ("client1.webp", "clientes/save-the-children", "Save the Children"),
    ("client2.webp", "clientes/liga-endesa", "Liga Endesa"),
    ("client3.webp", "clientes/universidad-europea", "Universidad Europea"),
    ("client4.webp", "clientes/mensajeros-de-la-paz", "Mensajeros de la Paz"),
    ("client5.webp", "clientes/russafart", "Russafart"),
    ("client6.webp", "clientes/fem-coliving", "FEM Coliving"),
]
WIDTHS = (800, 1600)


def sips_dims(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p], capture_output=True, text=True).stdout
    vals = [int(l.split(":")[1]) for l in out.splitlines() if "pixel" in l]
    return vals[0], vals[1]


def process_images():
    os.makedirs(os.path.join(ROOT, "img"), exist_ok=True)
    for src, slug, *_ in SPORT + WEDDING + EVENTS:
        s = os.path.join(ROOT, "originales", src)
        w, _h = sips_dims(s)
        for target in WIDTHS:
            out = os.path.join(ROOT, "img", f"{slug}-{target}.jpg")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            tw = min(target, w)
            q = "74" if target <= 800 else "62"
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", q,
                            "--resampleWidth", str(tw), s, "--out", out], capture_output=True, check=True)
    for src, slug, _ in CLIENTS:
        out = os.path.join(ROOT, "img", slug + ".png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(["sips", "-s", "format", "png", "-Z", "480", os.path.join(ROOT, "originales", src), "--out", out], capture_output=True, check=True)
    o = lambda *p: os.path.join(ROOT, *p)
    import shutil; shutil.copy(o("originales", "logo2.png"), o("img", "logo.png"))
    subprocess.run(["sips", "-s", "format", "png", "-Z", "180", o("originales", "logo2.png"), "--out", o("img", "apple-touch-icon.png")], capture_output=True, check=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", "-Z", "900", o("originales", "sobre-mi.webp"), "--out", o("img", "alvaro-baguena.jpg")], capture_output=True, check=True)
    # Imagen para compartir en redes (1200x630)
    og = o("img", "og-image.jpg")
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "75", "--resampleWidth", "1200",
                    o("originales", "foto-carrusel-3.webp"), "--out", og], capture_output=True, check=True)
    subprocess.run(["sips", "--cropToHeightWidth", "630", "1200", og], capture_output=True, check=True)


DIMS = {}


def dims(slug, width):
    key = f"{slug}-{width}"
    if key not in DIMS:
        DIMS[key] = sips_dims(os.path.join(ROOT, "img", f"{slug}-{width}.jpg"))
    return DIMS[key]


def img_tag(item, sizes="(max-width: 700px) 100vw, 50vw", eager=False, cls=""):
    _src, slug, alt_es, alt_va = item
    w, h = dims(slug, 800)
    small = asset(f"img/{slug}-800.jpg")
    big = asset(f"img/{slug}-1600.jpg")
    bw, _ = dims(slug, 1600)
    srcset = f"{small} {w}w, {big} {bw}w" if bw > w else f"{small} {w}w"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img src="{small}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{e(T(alt_es, alt_va))}" {load}{c}>')


def gallery(items, name, cls="gallery"):
    out = [f'<div class="{cls}" data-gallery="{name}">']
    for it in items:
        big = asset(f"img/{it[1]}-1600.jpg")
        out.append(f'<a class="gallery-item" href="{big}" data-lightbox>{img_tag(it, "(max-width: 700px) 100vw, (max-width: 1100px) 50vw, 33vw")}</a>')
    out.append("</div>")
    return "\n".join(out)


# ---------------------------------------------------------------- COMPONENTES
def whatsapp_link(service=None):
    msg = T("Hola Álvaro, he visto tu web y quiero información", "Hola Álvaro, he vist la teua web i vull informació")
    if service:
        msg += T(f" sobre {service}.", f" sobre {service}.")
    else:
        msg += "."
    return f"https://wa.me/{PHONE_RAW}?text={urllib.parse.quote(msg)}"


def header(current):
    nav = [
        ("deporte", T("Deporte", "Esport")),
        ("eventos", T("Eventos", "Esdeveniments")),
    ]
    cur = ' aria-current="page"'
    items = "".join(
        f'<li><a href="{href(p)}"{cur if p == current else ""}>{label}</a></li>' for p, label in nav)
    items += f'<li><a href="{href("home")}#sobre-mi">{T("Sobre mí", "Sobre mi")}</a></li>'
    other = "va" if LANG == "es" else "es"
    other_page = current if current in PAGES else "home"
    other_href = href(other_page, other)
    other_label = "VA" if other == "va" else "ES"
    other_title = "Valencià" if other == "va" else "Castellano"
    return f'''
<a class="skip" href="#main">{T("Saltar al contenido", "Anar al contingut")}</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{href("home")}" aria-label="{NAME} — {T("inicio", "inici")}">
      <img src="{asset("img/logo.png")}" alt="" width="40" height="46">
      <span>Álvaro Bàguena</span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="{T("Abrir menú", "Obrir menú")}"><span></span><span></span></button>
    <nav id="nav" class="nav" aria-label="{T("Principal", "Principal")}">
      <ul>{items}</ul>
      <a class="lang" href="{other_href}" hreflang="{"ca" if other == "va" else "es"}" lang="{"ca" if other == "va" else "es"}" title="{other_title}">{other_label}</a>
      <a class="btn btn-primary btn-sm" href="{href("contacto")}">{T("Pide presupuesto", "Demana pressupost")}</a>
    </nav>
  </div>
</header>'''


def footer():
    return f'''
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="brand" href="{href("home")}"><img src="{asset("img/logo.png")}" alt="" width="40" height="46"><span>Álvaro Bàguena</span></a>
      <p class="muted">{T("Fotógrafo en Valencia. Deporte y eventos: bodas, fallas, conciertos y fiestas.", "Fotògraf a València. Esport i esdeveniments: bodes, falles, concerts i festes.")}</p>
      <div class="social">
        <a href="{INSTAGRAM}" rel="me noopener" target="_blank" aria-label="Instagram"><i class="bi bi-instagram"></i></a>
        <a href="{BEHANCE}" rel="me noopener" target="_blank" aria-label="Behance"><i class="bi bi-behance"></i></a>
        <a href="{LINKEDIN}" rel="me noopener" target="_blank" aria-label="LinkedIn"><i class="bi bi-linkedin"></i></a>
      </div>
    </div>
    <div>
      <p class="footer-title">{T("Servicios", "Serveis")}</p>
      <ul>
        <li><a href="{href("deporte")}">{T("Fotografía deportiva", "Fotografia esportiva")}</a></li>
        <li><a href="{href("eventos")}">{T("Eventos", "Esdeveniments")}</a></li>
        <li><a href="{href("contacto")}">{T("Pedir presupuesto", "Demanar pressupost")}</a></li>
      </ul>
    </div>
    <div>
      <p class="footer-title">{T("Contacto", "Contacte")}</p>
      <ul>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><a href="{whatsapp_link()}" target="_blank" rel="noopener">WhatsApp · {PHONE}</a></li>
        <li class="muted">València, {T("España", "Espanya")}</li>
      </ul>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <p>© 2026 Álvaro Bàguena</p>
    <p><a href="{href("privacidad")}">{T("Privacidad", "Privacitat")}</a> · <a href="{href("home", "va" if LANG == "es" else "es")}">{T("Valencià", "Castellano")}</a></p>
  </div>
</footer>
<a class="wa-float" href="{whatsapp_link()}" target="_blank" rel="noopener" aria-label="{T("Escríbeme por WhatsApp", "Escriu-me per WhatsApp")}"><i class="bi bi-whatsapp"></i></a>
<dialog class="lightbox" aria-label="{T("Visor de fotos", "Visor de fotos")}">
  <button class="lb-close" aria-label="{T("Cerrar", "Tancar")}">×</button>
  <button class="lb-prev" aria-label="{T("Anterior", "Anterior")}">‹</button>
  <img alt="">
  <button class="lb-next" aria-label="{T("Siguiente", "Següent")}">›</button>
  <p class="lb-caption"></p>
</dialog>'''


SERVICE_OPTIONS = [
    ("deporte", ("Fotografía deportiva", "Fotografia esportiva")),
    ("boda", ("Boda", "Boda")),
    ("fallas", ("Fallas", "Falles")),
    ("concierto", ("Concierto", "Concert")),
    ("fiesta", ("Fiesta o celebración", "Festa o celebració")),
    ("otro", ("Otro", "Altre")),
]


def contact_form(preselect=None, title=True):
    opts = "".join(
        f'<option value="{T(*lab)}" data-key="{k}"{" selected" if k == preselect else ""}>{T(*lab)}</option>'
        for k, lab in SERVICE_OPTIONS)
    if not preselect:
        opts = f'<option value="" disabled selected>{T("Elige una opción", "Tria una opció")}</option>' + opts
    next_url = url_of("gracias", LANG)
    return f'''
<form class="form" action="{FORM_ACTION}" method="POST" data-ajax>
  <input type="hidden" name="_subject" value="{T("Nueva solicitud de presupuesto desde la web", "Nova sol·licitud de pressupost des de la web")}">
  <input type="hidden" name="_next" value="{next_url}">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="idioma" value="{LANG}">
  <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="field-row">
    <label class="field"><span>{T("Nombre", "Nom")} *</span><input name="nombre" autocomplete="name" required></label>
    <label class="field"><span>Email *</span><input type="email" name="email" autocomplete="email" required></label>
  </div>
  <div class="field-row">
    <label class="field"><span>{T("Teléfono", "Telèfon")}</span><input type="tel" name="telefono" autocomplete="tel"></label>
    <label class="field"><span>{T("¿Qué necesitas?", "Què necessites?")} *</span><select name="servicio" required>{opts}</select></label>
  </div>
  <div class="field-row">
    <label class="field"><span>{T("Fecha (si la sabes)", "Data (si la saps)")}</span><input type="date" name="fecha"></label>
    <label class="field"><span>{T("Lugar", "Lloc")}</span><input name="lugar" placeholder="{T("Ej.: Valencia, Paterna…", "Ex.: València, Paterna…")}"></label>
  </div>
  <label class="field"><span>{T("Cuéntame un poco más", "Explica'm una mica més")} *</span><textarea name="mensaje" rows="4" required placeholder="{T("Tipo de evento, número de personas, qué te gustaría conseguir…", "Tipus d'esdeveniment, nombre de persones, què t'agradaria aconseguir…")}"></textarea></label>
  <label class="check"><input type="checkbox" name="privacidad" value="aceptada" required><span>{T("He leído y acepto la", "He llegit i accepte la")} <a href="{href("privacidad")}" target="_blank">{T("política de privacidad", "política de privacitat")}</a>.</span></label>
  <button class="btn btn-primary btn-lg" type="submit">{T("Pedir presupuesto sin compromiso", "Demanar pressupost sense compromís")}</button>
  <p class="form-note"><i class="bi bi-clock"></i> {T("Respondo en menos de 24 h.", "Responc en menys de 24 h.")} <a href="{whatsapp_link()}" target="_blank" rel="noopener">{T("¿Prefieres WhatsApp?", "Prefereixes WhatsApp?")}</a></p>
  <p class="form-error" role="alert" hidden>{T("No se ha podido enviar. Escríbeme a", "No s'ha pogut enviar. Escriu-me a")} <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</form>'''


def cta_section(preselect=None, heading=None, lead=None):
    heading = heading or T("¿Hablamos de tu proyecto?", "Parlem del teu projecte?")
    lead = lead or T("Cuéntame qué necesitas y te envío una propuesta a medida, sin compromiso.",
                     "Explica'm què necessites i t'envie una proposta a mida, sense compromís.")
    return f'''
<section class="section cta" id="presupuesto">
  <div class="wrap cta-grid">
    <div>
      <p class="eyebrow">{T("Presupuesto en 24 h", "Pressupost en 24 h")}</p>
      <h2>{heading}</h2>
      <p class="lead">{lead}</p>
      <ul class="ticks">
        <li>{T("Respuesta personal en menos de 24 h", "Resposta personal en menys de 24 h")}</li>
        <li>{T("Propuesta clara, sin letra pequeña", "Proposta clara, sense lletra menuda")}</li>
        <li>{T("Valencia y alrededores, y desplazamientos", "València i rodalia, i desplaçaments")}</li>
      </ul>
    </div>
    {contact_form(preselect)}
  </div>
</section>'''


def steps():
    data = [
        (T("Cuéntame", "Explica'm"), T("Rellena el formulario o escríbeme por WhatsApp: fecha, lugar y qué tienes en mente.", "Ompli el formulari o escriu-me per WhatsApp: data, lloc i què tens en ment.")),
        (T("Propuesta", "Proposta"), T("En menos de 24 h te envío una propuesta adaptada a lo que necesitas, con precio cerrado.", "En menys de 24 h t'envie una proposta adaptada al que necessites, amb preu tancat.")),
        (T("Sesión y entrega", "Sessió i lliurament"), T("Hago las fotos y te entrego una galería online con la selección editada, lista para compartir.", "Faig les fotos i et lliure una galeria en línia amb la selecció editada, preparada per a compartir.")),
    ]
    items = "".join(f'<li><span class="step-n">0{i+1}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(data))
    return f'''
<section class="section">
  <div class="wrap">
    <p class="eyebrow">{T("Cómo trabajo", "Com treballe")}</p>
    <h2>{T("Tres pasos, sin complicaciones", "Tres passos, sense complicacions")}</h2>
    <ol class="steps">{items}</ol>
  </div>
</section>'''


def clients_strip():
    logos = "".join(
        f'<li><img src="{asset("img/" + slug + ".png")}" alt="{name}" loading="lazy"></li>' for _s, slug, name in CLIENTS)
    return f'''
<section class="clients" aria-label="{T("Han confiado en mí", "Han confiat en mi")}">
  <div class="wrap">
    <p class="eyebrow center">{T("Han confiado en mi trabajo", "Han confiat en el meu treball")}</p>
    <ul class="logos">{logos}</ul>
  </div>
</section>'''


def faq_section(items, title=None):
    det = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items)
    return f'''
<section class="section">
  <div class="wrap narrow">
    <p class="eyebrow">FAQ</p>
    <h2>{title or T("Preguntas frecuentes", "Preguntes freqüents")}</h2>
    <div class="faq">{det}</div>
  </div>
</section>'''


def faq_schema(items):
    import re
    strip = lambda s: re.sub("<[^>]+>", "", s)
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}


def business_schema():
    return {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "@id": f"{BASE_URL}/#negocio",
        "name": "Álvaro Bàguena · Fotografía",
        "description": T("Fotógrafo en Valencia: fotografía deportiva y de eventos (bodas, fallas, conciertos y fiestas).", "Fotògraf a València: fotografia esportiva i d'esdeveniments (bodes, falles, concerts i festes)."),
        "url": f"{BASE_URL}/",
        "image": f"{BASE_URL}/img/og-image.jpg",
        "logo": f"{BASE_URL}/img/logo.png",
        "email": EMAIL,
        "telephone": "+" + PHONE_RAW,
        "address": {"@type": "PostalAddress", "addressLocality": "València", "addressRegion": "Comunitat Valenciana", "addressCountry": "ES"},
        "areaServed": [{"@type": "City", "name": "València"}, {"@type": "AdministrativeArea", "name": "Comunitat Valenciana"}],
        "founder": {"@type": "Person", "name": NAME, "jobTitle": T("Fotógrafo", "Fotògraf"), "sameAs": [INSTAGRAM, BEHANCE, LINKEDIN]},
        "sameAs": [INSTAGRAM, BEHANCE, LINKEDIN],
        "knowsLanguage": ["es", "ca", "en"],
    }


def breadcrumb_schema(page, name):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": T("Inicio", "Inici"), "item": url_of("home", LANG)},
        {"@type": "ListItem", "position": 2, "name": name, "item": url_of(page, LANG)}]}


def layout(page, title, description, body, schemas=(), noindex=False, og_image="img/og-image.jpg"):
    alt_links = "".join(
        f'<link rel="alternate" hreflang="{h}" href="{url_of(page, l)}">' for l, h in (("es", "es"), ("va", "ca")))
    alt_links += f'<link rel="alternate" hreflang="x-default" href="{url_of(page, "es")}">'
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    robots = '<meta name="robots" content="noindex, follow">' if noindex else '<meta name="robots" content="index, follow, max-image-preview:large">'
    return f'''<!doctype html>
<html lang="{"es" if LANG == "es" else "ca"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add("js")</script>
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{robots}
<link rel="canonical" href="{url_of(page, LANG)}">
{alt_links}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Álvaro Bàguena">
<meta property="og:locale" content="{"es_ES" if LANG == "es" else "ca_ES"}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url_of(page, LANG)}">
<meta property="og:image" content="{BASE_URL}/{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b1223">
<link rel="icon" href="{asset("img/logo.png")}" type="image/png">
<link rel="apple-touch-icon" href="{asset("img/apple-touch-icon.png")}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700;800&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<link rel="stylesheet" href="{asset("assets/site.css")}">
{ld}
</head>
<body>
{header(page)}
<main id="main">
{body}
</main>
{footer()}
<script src="{asset("assets/site.js")}" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------- PÁGINAS
def find(lst, slug_part):
    return next(i for i in lst if slug_part in i[1])


def page_home():
    hero_l = find(SPORT, "jugadora-valencia-basket")
    hero_r = find(WEDDING, "novios-jardin-velo")
    selected = [find(SPORT, "duelo-futbol"), find(WEDDING, "novia-baila-velo"), find(SPORT, "baloncesto-lanzamiento"),
                find(WEDDING, "intercambio-alianzas"), find(SPORT, "entrenador"), find(WEDDING, "novia-bailando-bn"),
                find(EVENTS, "concierto"), find(SPORT, "esgrima-accion"), find(WEDDING, "novia-cielo-azul")]
    faq = [
        (T("¿Cuánto cuesta una sesión?", "Quant costa una sessió?"),
         T("Depende del tipo de trabajo, la duración y la entrega. Cuéntame qué necesitas y en menos de 24 h te envío un presupuesto cerrado, sin compromiso.",
           "Depén del tipus de treball, la durada i el lliurament. Explica'm què necessites i en menys de 24 h t'envie un pressupost tancat, sense compromís.")),
        (T("¿Trabajas fuera de Valencia?", "Treballes fora de València?"),
         T("Sí. Trabajo sobre todo en Valencia y alrededores, pero me desplazo a cualquier punto de España. Los desplazamientos largos se incluyen en el presupuesto.",
           "Sí. Treballe sobretot a València i rodalia, però em desplace a qualsevol punt d'Espanya. Els desplaçaments llargs s'inclouen en el pressupost.")),
        (T("¿Cuánto tardas en entregar las fotos?", "Quant tardes a lliurar les fotos?"),
         T("Normalmente entre 1 y 2 semanas desde la sesión. Si necesitas algunas fotos antes para redes, lo acordamos.",
           "Normalment entre 1 i 2 setmanes des de la sessió. Si necessites algunes fotos abans per a xarxes, ho acordem.")),
        (T("¿Cómo reservo una fecha?", "Com reserve una data?"),
         T("Escríbeme con la fecha y el lugar. Si estoy libre, te envío la propuesta y la fecha queda reservada al confirmarla.",
           "Escriu-me amb la data i el lloc. Si estic lliure, t'envie la proposta i la data queda reservada en confirmar-la.")),
    ]
    body = f'''
<section class="hero">
  <div class="hero-media" aria-hidden="false">
    <a href="{href("deporte")}" class="hero-half">{img_tag(hero_l, "50vw", eager=True)}<span class="hero-tag">{T("Deporte", "Esport")} <i class="bi bi-arrow-right"></i></span></a>
    <a href="{href("eventos")}" class="hero-half">{img_tag(hero_r, "50vw", eager=True)}<span class="hero-tag">{T("Eventos", "Esdeveniments")} <i class="bi bi-arrow-right"></i></span></a>
  </div>
  <div class="hero-copy wrap">
    <p class="eyebrow">{T("Deporte y eventos", "Esport i esdeveniments")}</p>
    <h1>{T("Fotógrafo en Valencia", "Fotògraf a València")}</h1>
    <p class="lead">{T("Capturo el momento exacto: el gesto, la tensión y la emoción que no se repiten. En un partido, en una boda, en plena mascletà o en primera fila de un concierto.",
                         "Capture el moment exacte: el gest, la tensió i l'emoció que no es repeteixen. En un partit, en una boda, en plena mascletà o en primera fila d'un concert.")}</p>
    <div class="actions">
      <a class="btn btn-primary btn-lg" href="{href("contacto")}">{T("Pide presupuesto", "Demana pressupost")}</a>
      <a class="btn btn-ghost btn-lg" href="#trabajos">{T("Ver trabajos", "Veure treballs")}</a>
    </div>
    <p class="micro"><i class="bi bi-clock"></i> {T("Respuesta en menos de 24 h", "Resposta en menys de 24 h")}</p>
  </div>
</section>
{clients_strip()}
<section class="section" id="servicios">
  <div class="wrap">
    <p class="eyebrow">{T("Servicios", "Serveis")}</p>
    <h2>{T("¿Qué quieres que fotografíe?", "Què vols que fotografie?")}</h2>
    <div class="services">
      <a class="service-card" href="{href("deporte")}">
        {img_tag(find(SPORT, "futbolistas"), "(max-width: 800px) 100vw, 50vw")}
        <div class="service-body">
          <h3>{T("Fotografía deportiva", "Fotografia esportiva")}</h3>
          <p>{T("Partidos, retratos de plantilla y contenido para redes y patrocinadores. Para clubes, deportistas y competiciones.",
                "Partits, retrats de plantilla i contingut per a xarxes i patrocinadors. Per a clubs, esportistes i competicions.")}</p>
          <span class="link">{T("Ver fotografía deportiva", "Veure fotografia esportiva")} <i class="bi bi-arrow-right"></i></span>
        </div>
      </a>
      <a class="service-card" href="{href("eventos")}">
        {img_tag(find(WEDDING, "novia-velo-largo"), "(max-width: 800px) 100vw, 50vw")}
        <div class="service-body">
          <h3>{T("Fotografía de eventos", "Fotografia d'esdeveniments")}</h3>
          <p>{T("Bodas, fallas, conciertos y fiestas. Fotografía natural y documental: la emoción real, sin poses forzadas.",
                "Bodes, falles, concerts i festes. Fotografia natural i documental: l'emoció real, sense poses forçades.")}</p>
          <span class="link">{T("Ver eventos", "Veure esdeveniments")} <i class="bi bi-arrow-right"></i></span>
        </div>
      </a>
    </div>
  </div>
</section>
<section class="section" id="trabajos">
  <div class="wrap">
    <p class="eyebrow">{T("Trabajos seleccionados", "Treballs seleccionats")}</p>
    <h2>{T("Momentos que no se repiten", "Moments que no es repeteixen")}</h2>
    {gallery(selected, "home")}
  </div>
</section>
{steps()}
<section class="section about" id="sobre-mi">
  <div class="wrap about-grid">
    <img src="{asset("img/alvaro-baguena.jpg")}" alt="{T("Retrato de Álvaro Bàguena, fotógrafo en Valencia", "Retrat d'Álvaro Bàguena, fotògraf a València")}" width="778" height="900" loading="lazy" class="about-img">
    <div>
      <p class="eyebrow">{T("Sobre mí", "Sobre mi")}</p>
      <h2>{T("Hola, soy Álvaro", "Hola, soc Álvaro")}</h2>
      <p class="lead">{T("Fotógrafo y diseñador gráfico en Valencia. Antes de la cámara iba para biólogo: de ahí viene mi manera de mirar, con paciencia y atención al detalle.",
                         "Fotògraf i dissenyador gràfic a València. Abans de la càmera anava per a biòleg: d'ací ve la meua manera de mirar, amb paciència i atenció al detall.")}</p>
      <p>{T("Me muevo igual de cómodo en una pista, en una boda o en plena mascletà: en todos la clave es anticiparse al momento y estar donde tiene que estar la cámara sin molestar a nadie. Trabajo con un estilo natural, cálido y con carácter mediterráneo.",
            "Em moc igual de còmode en una pista, en una boda o en plena mascletà: a tots la clau és anticipar-se al moment i estar on ha d'estar la càmera sense molestar ningú. Treballe amb un estil natural, càlid i amb caràcter mediterrani.")}</p>
      <a class="btn btn-ghost" href="{INSTAGRAM}" target="_blank" rel="noopener"><i class="bi bi-instagram"></i> {T("Sígueme en Instagram", "Segueix-me a Instagram")}</a>
    </div>
  </div>
</section>
{faq_section(faq)}
{cta_section()}
'''
    title = T("Fotógrafo en Valencia · Deporte y eventos · Álvaro Bàguena",
              "Fotògraf a València · Esport i esdeveniments · Álvaro Bàguena")
    desc = T("Fotógrafo en Valencia: fotografía deportiva y de eventos (bodas, fallas, conciertos y fiestas). Fotos naturales y con emoción. Pide presupuesto: respuesta en 24 h.",
             "Fotògraf a València: fotografia esportiva i d'esdeveniments (bodes, falles, concerts i festes). Fotos naturals i amb emoció. Demana pressupost: resposta en 24 h.")
    return layout("home", title, desc, body, [business_schema(), faq_schema(faq)])


def service_page(page, key, h1, lead, hero_item, audiences, gallery_html, faq, title, desc, svc_name, extra=""):
    aud = "".join(f'<li><i class="bi {ic}"></i><h3>{t}</h3><p>{d}</p></li>' for ic, t, d in audiences)
    body = f'''
<section class="page-hero">
  {img_tag(hero_item, "100vw", eager=True, cls="page-hero-img")}
  <div class="wrap page-hero-copy">
    <nav class="crumbs" aria-label="{T("Ruta", "Ruta")}"><a href="{href("home")}">{T("Inicio", "Inici")}</a> / <span>{svc_name}</span></nav>
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    <div class="actions">
      <a class="btn btn-primary btn-lg" href="#presupuesto">{T("Pide presupuesto", "Demana pressupost")}</a>
      <a class="btn btn-ghost btn-lg" href="{whatsapp_link(svc_name.lower())}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i> WhatsApp</a>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <p class="eyebrow">{T("Para quién", "Per a qui")}</p>
    <h2>{T("¿En qué te puedo ayudar?", "En què et puc ajudar?")}</h2>
    <ul class="audiences">{aud}</ul>
  </div>
</section>
{gallery_html}
{extra}
{steps()}
{faq_section(faq)}
{cta_section(key)}
'''
    svc = {"@context": "https://schema.org", "@type": "Service", "name": svc_name, "serviceType": svc_name,
           "provider": {"@id": f"{BASE_URL}/#negocio"}, "areaServed": {"@type": "City", "name": "València"},
           "url": url_of(page, LANG), "description": desc}
    return layout(page, title, desc, body, [business_schema(), svc, faq_schema(faq), breadcrumb_schema(page, svc_name)])


def page_deporte():
    audiences = [
        ("bi-shield", T("Clubes y entidades", "Clubs i entitats"), T("Cobertura de partidos, fotos de plantilla, presentaciones de equipaciones y contenido para la temporada.", "Cobertura de partits, fotos de plantilla, presentacions d'equipacions i contingut per a la temporada.")),
        ("bi-person-arms-up", T("Deportistas", "Esportistes"), T("Retratos y fotos de acción para tu marca personal, tus redes y tus patrocinadores.", "Retrats i fotos d'acció per a la teua marca personal, les teues xarxes i els teus patrocinadors.")),
        ("bi-trophy", T("Competiciones y torneos", "Competicions i tornejos"), T("Torneos, campus, carreras y eventos deportivos, con fotos listas para publicar.", "Tornejos, campus, carreres i esdeveniments esportius, amb fotos preparades per a publicar.")),
        ("bi-megaphone", T("Marcas y patrocinadores", "Marques i patrocinadors"), T("Imágenes de campaña con deportistas reales y en contexto real.", "Imatges de campanya amb esportistes reals i en context real.")),
    ]
    faq = [
        (T("¿Qué deportes fotografías?", "Quins esports fotografies?"),
         T("Baloncesto, fútbol, esgrima y mucho más. Me adapto a pista cubierta, campo abierto y condiciones de poca luz.",
           "Bàsquet, futbol, esgrima i molt més. M'adapte a pista coberta, camp obert i condicions de poca llum.")),
        (T("¿Cuánto tardas en entregar las fotos de un partido?", "Quant tardes a lliurar les fotos d'un partit?"),
         T("La galería completa suele estar en 1–2 semanas. Si necesitas fotos rápidas para redes después del partido, lo incluimos en la propuesta.",
           "La galeria completa sol estar en 1–2 setmanes. Si necessites fotos ràpides per a xarxes després del partit, ho incloem en la proposta.")),
        (T("¿Puedo usar las fotos para patrocinadores y prensa?", "Puc usar les fotos per a patrocinadors i premsa?"),
         T("Sí. Los usos (redes, web, prensa, publicidad) se acuerdan en el presupuesto para que no tengas dudas.",
           "Sí. Els usos (xarxes, web, premsa, publicitat) s'acorden en el pressupost perquè no tingues dubtes.")),
        (T("¿Haces packs para toda la temporada?", "Fas paquets per a tota la temporada?"),
         T("Sí, para clubes que necesitan cobertura recurrente preparo una propuesta por temporada o por número de partidos.",
           "Sí, per a clubs que necessiten cobertura recurrent prepare una proposta per temporada o per nombre de partits.")),
    ]
    gal = f'''
<section class="section">
  <div class="wrap">
    <p class="eyebrow">Portfolio</p>
    <h2>{T("Baloncesto, fútbol, esgrima y más", "Bàsquet, futbol, esgrima i més")}</h2>
    {gallery(SPORT, "deporte")}
  </div>
</section>'''
    return service_page(
        "deporte", "deporte",
        T("Fotógrafo deportivo en Valencia", "Fotògraf esportiu a València"),
        T("Fotografía para clubes, deportistas y competiciones: la acción, la tensión y la celebración, contadas con fotos que dan ganas de compartir.",
          "Fotografia per a clubs, esportistes i competicions: l'acció, la tensió i la celebració, contades amb fotos que fan ganes de compartir."),
        find(SPORT, "futbolistas"), audiences, gal, faq,
        T("Fotógrafo deportivo en Valencia · Clubes y deportistas · Álvaro Bàguena", "Fotògraf esportiu a València · Clubs i esportistes · Álvaro Bàguena"),
        T("Fotógrafo deportivo en Valencia para clubes, deportistas y competiciones. Partidos, retratos y contenido para redes y patrocinadores. Presupuesto en 24 h.",
          "Fotògraf esportiu a València per a clubs, esportistes i competicions. Partits, retrats i contingut per a xarxes i patrocinadors. Pressupost en 24 h."),
        T("Fotografía deportiva", "Fotografia esportiva"))


def page_eventos():
    audiences = [
        ("bi-heart", T("Bodas", "Bodes"), T("Del primer momento a la fiesta: ceremonia, cóctel, banquete y baile, con un estilo natural y sin poses forzadas.", "Del primer moment a la festa: cerimònia, còctel, banquet i ball, amb un estil natural i sense poses forçades.")),
        ("bi-fire", T("Fallas", "Falles"), T("Plantà, ofrenda, mascletà y cremà. Fotos para tu comisión, el llibret y las redes de la falla.", "Plantà, ofrena, mascletà i cremà. Fotos per a la teua comissió, el llibret i les xarxes de la falla.")),
        ("bi-music-note-beamed", T("Conciertos", "Concerts"), T("Directos con luz de escenario para grupos, salas y festivales.", "Directes amb llum d'escenari per a grups, sales i festivals.")),
        ("bi-balloon", T("Fiestas y celebraciones", "Festes i celebracions"), T("Fiestas populares, cumpleaños, comuniones y celebraciones privadas o de empresa.", "Festes populars, aniversaris, comunions i celebracions privades o d'empresa.")),
    ]
    faq = [
        (T("¿Qué estilo de fotografía haces en eventos?", "Quin estil de fotografia fas en esdeveniments?"),
         T("Natural y documental: estoy atento a lo que pasa sin interrumpir, para que las fotos cuenten lo que se vivió de verdad. Si hace falta, también hago retratos y fotos de grupo.",
           "Natural i documental: estic atent al que passa sense interrompre, perquè les fotos conten el que es va viure de veritat. Si cal, també faig retrats i fotos de grup.")),
        (T("¿Cubres las fallas enteras o actos concretos?", "Cobreixes les falles senceres o actes concrets?"),
         T("Las dos cosas. Puedo cubrir un acto (la plantà, la ofrenda, la cremà…) o acompañar a la comisión toda la semana fallera. También preparo fotos para el llibret.",
           "Les dues coses. Puc cobrir un acte (la plantà, l'ofrena, la cremà…) o acompanyar la comissió tota la setmana fallera. També prepare fotos per al llibret.")),
        (T("¿Cuánto tardas en entregar las fotos?", "Quant tardes a lliurar les fotos?"),
         T("Recibes un adelanto en pocos días y la galería completa editada en 1–2 semanas. En bodas te confirmo el plazo exacto en la propuesta.",
           "Reps un avançament en pocs dies i la galeria completa editada en 1–2 setmanes. En bodes et confirme el termini exacte en la proposta.")),
        (T("¿Cómo reservo la fecha?", "Com reserve la data?"),
         T("Escríbeme con la fecha y el lugar. Si estoy libre, te envío la propuesta y la fecha queda reservada al confirmarla. En bodas y fallas conviene hacerlo con tiempo.",
           "Escriu-me amb la data i el lloc. Si estic lliure, t'envie la proposta i la data queda reservada en confirmar-la. En bodes i falles convé fer-ho amb temps.")),
        (T("¿Te desplazas fuera de Valencia?", "Et desplaces fora de València?"),
         T("Sí, a cualquier punto de España. El desplazamiento se incluye en el presupuesto desde el principio.",
           "Sí, a qualsevol punt d'Espanya. El desplaçament s'inclou en el pressupost des del principi.")),
    ]
    chips = "".join(f'<a href="#{a}">{t}</a>' for a, t in (
        ("bodas", T("Bodas", "Bodes")), ("fallas", T("Fallas", "Falles")),
        ("conciertos", T("Conciertos", "Concerts")), ("fiestas", T("Fiestas", "Festes"))))
    gal = f'''
<div class="wrap"><nav class="chips" aria-label="{T("Tipos de evento", "Tipus d'esdeveniment")}">{chips}</nav></div>
<section class="section" id="bodas">
  <div class="wrap">
    <p class="eyebrow">{T("Bodas", "Bodes")}</p>
    <h2>{T("Fotógrafo de bodas en Valencia", "Fotògraf de bodes a València")}</h2>
    <p class="lead narrow-text">{T("Una boda real en un jardín mediterráneo, de la ceremonia a la última canción: así es como cuento un día entero.", "Una boda real en un jardí mediterrani, de la cerimònia a l'última cançó: així és com conte un dia sencer.")}</p>
    {gallery(WEDDING, "boda")}
    <a class="btn btn-primary" href="{href("contacto")}?servicio=boda">{T("Consultar disponibilidad para mi boda", "Consultar disponibilitat per a la meua boda")}</a>
  </div>
</section>
<section class="section" id="fallas">
  <div class="wrap feature">
    <div>
      <p class="eyebrow">{T("Fallas", "Falles")}</p>
      <h2>{T("Fotógrafo de fallas en Valencia", "Fotògraf de falles a València")}</h2>
      <p class="lead">{T("La pólvora, el monumento, la ofrenda y la emoción de la cremà. Fotos para que la comisión recuerde su año fallero y tenga material para el llibret y las redes.",
                         "La pólvora, el monument, l'ofrena i l'emoció de la cremà. Fotos perquè la comissió recorde el seu any faller i tinga material per al llibret i les xarxes.")}</p>
      <ul class="ticks">
        <li>{T("Actos sueltos o toda la semana fallera", "Actes solts o tota la setmana fallera")}</li>
        <li>{T("Fotos para el llibret y las redes de la falla", "Fotos per al llibret i les xarxes de la falla")}</li>
        <li>{T("Retratos de falleras, falleros y comisión", "Retrats de falleres, fallers i comissió")}</li>
      </ul>
      <a class="btn btn-primary" href="{href("contacto")}?servicio=fallas">{T("Pedir presupuesto para mi falla", "Demanar pressupost per a la meua falla")}</a>
    </div>
  </div>
</section>
<section class="section" id="conciertos">
  <div class="wrap">
    <p class="eyebrow">{T("Conciertos", "Concerts")}</p>
    <h2>{T("Luz de escenario y energía en directo", "Llum d'escenari i energia en directe")}</h2>
    {gallery(EVENTS, "conciertos", "gallery gallery-3")}
  </div>
</section>
<section class="section" id="fiestas">
  <div class="wrap feature">
    <div>
      <p class="eyebrow">{T("Fiestas y celebraciones", "Festes i celebracions")}</p>
      <h2>{T("Fiestas que merecen recordarse", "Festes que mereixen recordar-se")}</h2>
      <p class="lead">{T("Fiestas populares, cumpleaños, comuniones o la cena de empresa: me muevo entre la gente sin que se note y capto el ambiente tal y como fue.",
                         "Festes populars, aniversaris, comunions o el sopar d'empresa: em moc entre la gent sense que es note i capte l'ambient tal com va ser.")}</p>
      <a class="btn btn-primary" href="{href("contacto")}?servicio=fiesta">{T("Contar mi celebración", "Explicar la meua celebració")}</a>
    </div>
  </div>
</section>'''
    return service_page(
        "eventos", None,
        T("Fotógrafo de eventos en Valencia", "Fotògraf d'esdeveniments a València"),
        T("Bodas, fallas, conciertos y fiestas. Fotografía natural y documental que cuenta la emoción de verdad, sin poses forzadas.",
          "Bodes, falles, concerts i festes. Fotografia natural i documental que conta l'emoció de veritat, sense poses forçades."),
        find(EVENTS, "concierto"), audiences, gal, faq,
        T("Fotógrafo de eventos en Valencia · Bodas, fallas y conciertos · Álvaro Bàguena", "Fotògraf d'esdeveniments a València · Bodes, falles i concerts · Álvaro Bàguena"),
        T("Fotógrafo de eventos en Valencia: bodas, fallas, conciertos y fiestas. Fotografía natural y documental. Consulta tu fecha y recibe presupuesto en 24 h.",
          "Fotògraf d'esdeveniments a València: bodes, falles, concerts i festes. Fotografia natural i documental. Consulta la teua data i rep pressupost en 24 h."),
        T("Eventos", "Esdeveniments"))


def page_contacto():
    body = f'''
<section class="section page-top">
  <div class="wrap cta-grid">
    <div>
      <p class="eyebrow">{T("Contacto", "Contacte")}</p>
      <h1>{T("Cuéntame tu proyecto", "Explica'm el teu projecte")}</h1>
      <p class="lead">{T("Rellena el formulario y te respondo en menos de 24 h con una propuesta a medida. Si lo prefieres, escríbeme directamente.",
                         "Ompli el formulari i et responc en menys de 24 h amb una proposta a mida. Si ho prefereixes, escriu-me directament.")}</p>
      <ul class="contact-list">
        <li><a href="{whatsapp_link()}" target="_blank" rel="noopener"><i class="bi bi-whatsapp"></i><span><strong>WhatsApp</strong>{PHONE}</span></a></li>
        <li><a href="mailto:{EMAIL}"><i class="bi bi-envelope"></i><span><strong>Email</strong>{EMAIL}</span></a></li>
        <li><a href="{INSTAGRAM}" target="_blank" rel="noopener"><i class="bi bi-instagram"></i><span><strong>Instagram</strong>@baaaguena</span></a></li>
        <li><span class="nolink"><i class="bi bi-geo-alt"></i><span><strong>{T("Zona", "Zona")}</strong>{T("Valencia y alrededores · desplazamientos", "València i rodalia · desplaçaments")}</span></span></li>
      </ul>
    </div>
    {contact_form()}
  </div>
</section>
{steps()}
'''
    return layout("contacto", T("Contacto y presupuesto · Álvaro Bàguena, fotógrafo en Valencia", "Contacte i pressupost · Álvaro Bàguena, fotògraf a València"),
                  T("Pide presupuesto para fotografía deportiva o de eventos en Valencia: bodas, fallas, conciertos y fiestas. Respuesta en menos de 24 h por email o WhatsApp.",
                    "Demana pressupost per a fotografia esportiva o d'esdeveniments a València: bodes, falles, concerts i festes. Resposta en menys de 24 h per email o WhatsApp."),
                  body, [business_schema()])


def page_gracias():
    body = f'''
<section class="section page-top thanks">
  <div class="wrap narrow center">
    <img src="{asset("img/logo.png")}" alt="" width="72" height="83">
    <h1>{T("¡Gracias! Mensaje recibido", "Gràcies! Missatge rebut")}</h1>
    <p class="lead">{T("Te respondo en menos de 24 h. Mientras tanto, puedes ver más trabajos en Instagram.",
                       "Et responc en menys de 24 h. Mentrestant, pots veure més treballs a Instagram.")}</p>
    <div class="actions center">
      <a class="btn btn-primary" href="{INSTAGRAM}" target="_blank" rel="noopener"><i class="bi bi-instagram"></i> @baaaguena</a>
      <a class="btn btn-ghost" href="{href("home")}">{T("Volver al inicio", "Tornar a l'inici")}</a>
    </div>
  </div>
</section>'''
    return layout("gracias", T("Gracias · Álvaro Bàguena", "Gràcies · Álvaro Bàguena"),
                  T("Mensaje recibido.", "Missatge rebut."), body, noindex=True)


def page_privacidad():
    es = f'''
<h1>Política de privacidad</h1>
<p><strong>Responsable:</strong> {NAME}. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>. València (España).</p>
<h2>Qué datos recojo y para qué</h2>
<p>Cuando rellenas el formulario de contacto recojo tu nombre, email, teléfono (opcional) y la información que me cuentas sobre tu proyecto. Los uso únicamente para responder a tu solicitud y, si lo aceptas, preparar y gestionar el presupuesto.</p>
<h2>Base legal</h2>
<p>Tu consentimiento al enviar el formulario y la aplicación de medidas precontractuales a petición tuya (art. 6.1.a y 6.1.b del RGPD).</p>
<h2>Cuánto tiempo los guardo</h2>
<p>El tiempo necesario para atender tu solicitud y, si hay encargo, durante la relación profesional y los plazos legales que correspondan.</p>
<h2>Con quién se comparten</h2>
<p>No cedo tus datos a terceros. El envío del formulario se gestiona con el servicio FormSubmit, que actúa como encargado del tratamiento para hacerme llegar el mensaje por email.</p>
<h2>Tus derechos</h2>
<p>Puedes pedir acceso, rectificación, supresión, oposición, limitación o portabilidad de tus datos escribiendo a <a href="mailto:{EMAIL}">{EMAIL}</a>. También puedes reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>
<h2>Cookies</h2>
<p>Esta web no usa cookies propias de análisis ni de publicidad.</p>
<h2>Fotografías</h2>
<p>Las fotografías publicadas se muestran con el permiso de las personas que aparecen. Si apareces en alguna y quieres que la retire, escríbeme.</p>'''
    va = f'''
<h1>Política de privacitat</h1>
<p><strong>Responsable:</strong> {NAME}. Email: <a href="mailto:{EMAIL}">{EMAIL}</a>. València (Espanya).</p>
<h2>Quines dades arreplegue i per a què</h2>
<p>Quan omplis el formulari de contacte arreplegue el teu nom, email, telèfon (opcional) i la informació que m'expliques sobre el teu projecte. Les use únicament per a respondre la teua sol·licitud i, si ho acceptes, preparar i gestionar el pressupost.</p>
<h2>Base legal</h2>
<p>El teu consentiment en enviar el formulari i l'aplicació de mesures precontractuals a petició teua (art. 6.1.a i 6.1.b del RGPD).</p>
<h2>Quant de temps les guarde</h2>
<p>El temps necessari per a atendre la teua sol·licitud i, si hi ha encàrrec, durant la relació professional i els terminis legals que corresponguen.</p>
<h2>Amb qui es comparteixen</h2>
<p>No cedisc les teues dades a tercers. L'enviament del formulari es gestiona amb el servei FormSubmit, que actua com a encarregat del tractament per a fer-me arribar el missatge per email.</p>
<h2>Els teus drets</h2>
<p>Pots demanar accés, rectificació, supressió, oposició, limitació o portabilitat de les teues dades escrivint a <a href="mailto:{EMAIL}">{EMAIL}</a>. També pots reclamar davant de l'Agència Espanyola de Protecció de Dades (aepd.es).</p>
<h2>Galetes</h2>
<p>Aquesta web no usa galetes pròpies d'anàlisi ni de publicitat.</p>
<h2>Fotografies</h2>
<p>Les fotografies publicades es mostren amb el permís de les persones que hi apareixen. Si hi apareixes i vols que la retire, escriu-me.</p>'''
    body = f'<section class="section page-top"><div class="wrap narrow prose">{T(es, va)}</div></section>'
    return layout("privacidad", T("Política de privacidad · Álvaro Bàguena", "Política de privacitat · Álvaro Bàguena"),
                  T("Política de privacidad de la web de Álvaro Bàguena.", "Política de privacitat de la web d'Álvaro Bàguena."), body, noindex=True)


def page_404():
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página no encontrada · Álvaro Bàguena</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@700;800&family=Inter:wght@400;500&display=swap">
<link rel="stylesheet" href="{BASE_URL}/assets/site.css"><link rel="icon" href="{BASE_URL}/img/logo.png"></head>
<body><main class="section page-top"><div class="wrap narrow center">
<img src="{BASE_URL}/img/logo.png" alt="" width="72" height="83">
<h1>Esta página no existe</h1><p class="lead">Puede que el enlace haya cambiado. / Pot ser que l'enllaç haja canviat.</p>
<div class="actions center"><a class="btn btn-primary" href="{BASE_URL}/">Ir al inicio</a><a class="btn btn-ghost" href="{BASE_URL}/va/">Anar a l'inici</a></div>
</div></main></body></html>'''


def redirect(target, title):
    url = f"{BASE_URL}/{target}"
    return f'''<!doctype html><html lang="ca"><head><meta charset="utf-8"><title>{title}</title>
<link rel="canonical" href="{url}"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}"></head>
<body><p><a href="{target}">{title}</a></p></body></html>'''


def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    global LANG
    if "--imagenes" in sys.argv:
        process_images()
    builders = {"home": page_home, "deporte": page_deporte, "eventos": page_eventos,
                "contacto": page_contacto, "gracias": page_gracias, "privacidad": page_privacidad}
    for LANG in ("es", "va"):
        for page, fn in builders.items():
            write(path_of(page), fn())
    LANG = "es"
    write("404.html", page_404())
    # Redirecciones de las URLs antiguas (estaban en valenciano)
    write("servicios.html", redirect("va/index.html#serveis", "Serveis"))
    write("galeria.html", redirect("va/fotograf-esportiu-valencia.html", "Galeria"))
    write("sobremi.html", redirect("va/index.html#sobre-mi", "Sobre mi"))
    write("contactos.html", redirect("va/contacte.html", "Contacte"))
    # Sitemap con versiones alternativas
    urls = []
    for page in ("home", "deporte", "eventos", "contacto"):
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{h}" href="{url_of(page, l)}"/>' for l, h in (("es", "es"), ("va", "ca")))
        for l in ("es", "va"):
            pri = "1.0" if page == "home" else ("0.9" if page in ("deporte", "eventos") else "0.7")
            urls.append(f"<url><loc>{url_of(page, l)}</loc>{alts}<priority>{pri}</priority></url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
          + "\n".join(urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n")
    print("Web generada.")


if __name__ == "__main__":
    main()
