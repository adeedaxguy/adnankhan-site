import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';

const root = new URL('..', import.meta.url).pathname;
const locales = {
  es: {
    label: 'Español', locale: 'es_ES',
    nav: ['Servicios', 'Auditoría gratis'], contact: 'Hablar de un proyecto',
    home: {
      path: '/', title: 'Diseño y desarrollo web para empresas | Lofts Studio',
      description: 'Lofts Studio diseña y desarrolla sitios web rápidos para empresas que necesitan más visibilidad, confianza y oportunidades comerciales.',
      eyebrow: 'Diseño web · Desarrollo · SEO y AEO',
      heading: 'Sitios web que convierten la atención en oportunidades reales.',
      lead: 'Diseñamos y mejoramos sitios para empresas de servicios, clínicas, SaaS y comercio electrónico. La estrategia, la velocidad, el contenido y la conversión se trabajan como un solo sistema.',
      answer: 'Lofts Studio combina diseño, desarrollo, SEO técnico, arquitectura de contenidos y medición. El objetivo no es entregar páginas bonitas: es crear un sitio útil que pueda encontrarse, entenderse y generar contactos.',
      cards: [
        ['Arquitectura antes del diseño', 'Mapeamos servicios, intención de búsqueda, páginas prioritarias, enlaces internos y recorridos de conversión antes de diseñar.'],
        ['Desarrollo rápido y accesible', 'Construimos experiencias móviles, rápidas y fáciles de mantener en WordPress, Webflow, Shopify o una solución a medida.'],
        ['Crecimiento medible', 'Configuramos analítica, eventos, SEO/AEO y mejoras continuas sobre las páginas que ya muestran potencial.']
      ],
      section: 'Un socio senior para diseño web, desarrollo y crecimiento orgánico.'
    },
    service: {
      path: '/services/website-development-company.html', title: 'Empresa de desarrollo web para negocios | Lofts Studio',
      description: 'Desarrollo web para empresas de servicios que necesitan velocidad, SEO, mejores conversiones y una estructura fácil de gestionar.',
      eyebrow: 'Empresa de desarrollo web · Estrategia y ejecución',
      heading: 'Desarrollo web para empresas que necesitan conseguir clientes.',
      lead: 'Creamos sitios que conectan la oferta, la intención de búsqueda y el siguiente paso del usuario. Cada página tiene un propósito comercial y una función dentro de la arquitectura SEO.',
      answer: 'Una empresa de desarrollo web responsable debe estudiar el negocio, las búsquedas, la competencia, el recorrido del comprador y los riesgos técnicos antes de diseñar. Así se evita reconstruir un sitio que sigue sin producir resultados.',
      cards: [
        ['Sitios para empresas de servicios', 'Páginas de servicios, ubicaciones, casos, reseñas, formularios y llamadas a la acción conectados con una estructura clara.'],
        ['SaaS y productos digitales', 'Páginas de producto, comparativas, documentación, pruebas y recorridos de registro pensados para búsqueda y conversión.'],
        ['Mejoras sobre sitios existentes', 'Velocidad, mensajes, SEO técnico, enlaces internos y páginas de alto potencial antes de recomendar una reconstrucción.']
      ],
      section: 'La web se planifica como un sistema de búsqueda y conversión.'
    },
    audit: {
      path: '/free-audit/', title: 'Auditoría web gratuita con plan de mejoras | Lofts Studio',
      description: 'Solicita una auditoría web gratuita para detectar problemas de SEO, rendimiento móvil, confianza, contenido y conversión.',
      eyebrow: 'Auditoría web gratuita · Diagnóstico inicial',
      heading: 'Descubre qué impide que tu sitio atraiga y convierta más visitas.',
      lead: 'Revisamos señales observables de rastreo, indexación, rendimiento móvil, claridad del mensaje, confianza y conversión. Recibirás prioridades prácticas, no una lista automática sin contexto.',
      answer: 'La auditoría inicial identifica dónde se pierde la oportunidad: acceso de Google, páginas débiles, intención mal cubierta, velocidad, prueba insuficiente o fricción en formularios y llamadas a la acción.',
      cards: [
        ['SEO técnico', 'Revisamos canonicals, indexación, sitemap, robots, enlaces rotos, metadatos y datos estructurados.'],
        ['Experiencia y confianza', 'Comprobamos la primera pantalla móvil, la claridad de la oferta, las pruebas y la facilidad para completar la acción principal.'],
        ['Plan priorizado', 'Ordenamos los cambios por impacto, esfuerzo y riesgo para que el equipo sepa qué corregir primero.']
      ],
      section: 'Empieza con evidencia antes de pagar por un rediseño.'
    }
  },
  fr: {
    label: 'Français', locale: 'fr_FR',
    nav: ['Services', 'Audit gratuit'], contact: 'Parler du projet',
    home: {
      path: '/', title: 'Conception et développement web pour entreprises | Lofts Studio',
      description: 'Lofts Studio conçoit des sites rapides pour les entreprises qui veulent davantage de visibilité, de confiance et de prospects.',
      eyebrow: 'Design web · Développement · SEO et AEO',
      heading: 'Des sites web qui transforment l’attention en opportunités concrètes.',
      lead: 'Nous concevons et améliorons des sites pour les entreprises de services, les cliniques, les SaaS et le e-commerce. Stratégie, vitesse, contenu et conversion sont traités comme un seul système.',
      answer: 'Lofts Studio réunit design, développement, SEO technique, architecture éditoriale et mesure. Le but n’est pas seulement de livrer de belles pages, mais un site utile, trouvable, compréhensible et capable de générer des demandes.',
      cards: [
        ['Architecture avant le design', 'Nous cartographions les services, les intentions de recherche, les pages prioritaires, les liens internes et les parcours de conversion avant de concevoir.'],
        ['Développement rapide et accessible', 'Nous créons des expériences mobiles rapides et maintenables avec WordPress, Webflow, Shopify ou une solution sur mesure.'],
        ['Croissance mesurable', 'Nous mettons en place l’analytics, les événements, le SEO/AEO et l’amélioration continue des pages à fort potentiel.']
      ],
      section: 'Un partenaire senior pour le design web, le développement et la croissance organique.'
    },
    service: {
      path: '/services/website-development-company.html', title: 'Agence de développement web pour entreprises | Lofts Studio',
      description: 'Développement web pour les entreprises de services qui ont besoin de vitesse, de SEO, de conversions et d’une structure simple à gérer.',
      eyebrow: 'Développement web · Stratégie et réalisation',
      heading: 'Une agence web pour les entreprises qui doivent générer des clients.',
      lead: 'Nous créons des sites qui relient l’offre, l’intention de recherche et la prochaine action. Chaque page possède un objectif commercial et un rôle précis dans l’architecture SEO.',
      answer: 'Une agence de développement web sérieuse étudie l’activité, les recherches, la concurrence, le parcours d’achat et les risques techniques avant le design. Cela évite de reconstruire un site qui ne produit toujours pas de résultats.',
      cards: [
        ['Entreprises de services', 'Pages de services et de zones, études de cas, avis, formulaires et appels à l’action reliés dans une structure claire.'],
        ['SaaS et produits numériques', 'Pages produit, comparatifs, documentation, essais et parcours d’inscription pensés pour la recherche et la conversion.'],
        ['Optimisation de l’existant', 'Vitesse, message, SEO technique, maillage interne et pages à fort potentiel avant de recommander une refonte.']
      ],
      section: 'Le site est conçu comme un système de recherche et de conversion.'
    },
    audit: {
      path: '/free-audit/', title: 'Audit de site gratuit et plan d’amélioration | Lofts Studio',
      description: 'Demandez un audit de site gratuit pour identifier les problèmes de SEO, mobile, confiance, contenu et conversion.',
      eyebrow: 'Audit de site gratuit · Diagnostic initial',
      heading: 'Découvrez ce qui empêche votre site d’attirer et de convertir davantage.',
      lead: 'Nous examinons les signaux observables liés à l’exploration, l’indexation, l’expérience mobile, la clarté du message, la confiance et la conversion. Vous recevez des priorités utiles, pas une liste automatique sans contexte.',
      answer: 'L’audit initial montre où l’opportunité se perd : accès de Google, pages trop faibles, intention mal couverte, lenteur, manque de preuves ou friction dans les formulaires et appels à l’action.',
      cards: [
        ['SEO technique', 'Nous vérifions les canonicals, l’indexation, le sitemap, robots.txt, les liens cassés, les métadonnées et les données structurées.'],
        ['Expérience et confiance', 'Nous évaluons le premier écran mobile, la clarté de l’offre, les preuves et la facilité d’accomplir l’action principale.'],
        ['Plan priorisé', 'Nous classons les changements par impact, effort et risque afin de savoir quoi corriger en premier.']
      ],
      section: 'Commencez par des preuves avant de financer une refonte.'
    }
  },
  it: {
    label: 'Italiano', locale: 'it_IT',
    nav: ['Servizi', 'Audit gratuito'], contact: 'Parliamo del progetto',
    home: {
      path: '/', title: 'Web design e sviluppo per aziende | Lofts Studio',
      description: 'Lofts Studio progetta siti veloci per aziende che vogliono più visibilità, fiducia e richieste commerciali.',
      eyebrow: 'Web design · Sviluppo · SEO e AEO',
      heading: 'Siti web che trasformano l’attenzione in opportunità reali.',
      lead: 'Progettiamo e miglioriamo siti per aziende di servizi, cliniche, SaaS ed ecommerce. Strategia, velocità, contenuti e conversione vengono gestiti come un unico sistema.',
      answer: 'Lofts Studio unisce design, sviluppo, SEO tecnica, architettura dei contenuti e misurazione. L’obiettivo non è soltanto creare belle pagine, ma un sito utile, trovabile, comprensibile e capace di generare contatti.',
      cards: [
        ['Architettura prima del design', 'Mappiamo servizi, intento di ricerca, pagine prioritarie, collegamenti interni e percorsi di conversione prima di progettare.'],
        ['Sviluppo veloce e accessibile', 'Creiamo esperienze mobile rapide e facili da gestire con WordPress, Webflow, Shopify o soluzioni su misura.'],
        ['Crescita misurabile', 'Configuriamo analytics, eventi, SEO/AEO e miglioramenti continui sulle pagine che mostrano già potenziale.']
      ],
      section: 'Un partner senior per web design, sviluppo e crescita organica.'
    },
    service: {
      path: '/services/website-development-company.html', title: 'Azienda di sviluppo web per imprese | Lofts Studio',
      description: 'Sviluppo web per aziende di servizi che hanno bisogno di velocità, SEO, conversioni e una struttura facile da gestire.',
      eyebrow: 'Sviluppo web · Strategia ed esecuzione',
      heading: 'Sviluppo web per aziende che devono acquisire clienti.',
      lead: 'Creiamo siti che collegano l’offerta, l’intento di ricerca e la prossima azione dell’utente. Ogni pagina ha uno scopo commerciale e un ruolo nell’architettura SEO.',
      answer: 'Un’azienda di sviluppo web affidabile studia il business, le ricerche, la concorrenza, il percorso d’acquisto e i rischi tecnici prima del design. In questo modo non si ricostruisce un sito che continua a non produrre risultati.',
      cards: [
        ['Aziende di servizi', 'Pagine di servizio e località, casi studio, recensioni, moduli e call to action collegati in una struttura chiara.'],
        ['SaaS e prodotti digitali', 'Pagine prodotto, confronti, documentazione, prove e percorsi di registrazione pensati per ricerca e conversione.'],
        ['Miglioramento del sito esistente', 'Velocità, messaggio, SEO tecnica, collegamenti interni e pagine ad alto potenziale prima di consigliare un rifacimento.']
      ],
      section: 'Il sito viene pianificato come un sistema di ricerca e conversione.'
    },
    audit: {
      path: '/free-audit/', title: 'Audit gratuito del sito e piano di miglioramento | Lofts Studio',
      description: 'Richiedi un audit gratuito del sito per individuare problemi SEO, mobile, fiducia, contenuti e conversione.',
      eyebrow: 'Audit gratuito del sito · Diagnosi iniziale',
      heading: 'Scopri cosa impedisce al tuo sito di attirare e convertire più visitatori.',
      lead: 'Analizziamo segnali osservabili di scansione, indicizzazione, esperienza mobile, chiarezza del messaggio, fiducia e conversione. Riceverai priorità pratiche, non una lista automatica senza contesto.',
      answer: 'L’audit iniziale mostra dove si perde l’opportunità: accesso di Google, pagine deboli, intento non coperto, lentezza, prove insufficienti o attrito nei moduli e nelle call to action.',
      cards: [
        ['SEO tecnica', 'Controlliamo canonical, indicizzazione, sitemap, robots.txt, link interrotti, metadati e dati strutturati.'],
        ['Esperienza e fiducia', 'Valutiamo la prima schermata mobile, la chiarezza dell’offerta, le prove e la facilità dell’azione principale.'],
        ['Piano prioritario', 'Ordiniamo le modifiche per impatto, impegno e rischio, così il team sa cosa correggere per primo.']
      ],
      section: 'Parti dai dati prima di investire in un nuovo design.'
    }
  }
};

const englishPaths = {
  home: '/',
  service: '/services/website-development-company.html',
  audit: '/free-audit/'
};

function alternates(key) {
  const englishPath = englishPaths[key];
  const localizedPath = englishPath === '/' ? '' : englishPath.replace(/\/$/, '');
  return [
    ['en', `https://lofts.studio${englishPath === '/' ? '/' : localizedPath}`],
    ...Object.keys(locales).map((locale) => [locale, `https://lofts.studio/${locale}${localizedPath}`]),
    ['x-default', `https://lofts.studio${englishPath === '/' ? '/' : localizedPath}`]
  ].map(([lang, href]) => `<link rel="alternate" hreflang="${lang}" href="${href}" />`).join('\n');
}

function page(locale, common, key, data) {
  const route = data.path === '/' ? '' : data.path.replace(/\/$/, '');
  const canonical = `https://lofts.studio/${locale}${route}`;
  const home = `/${locale}`;
  const service = `/${locale}/services/website-development-company.html`;
  const audit = `/${locale}/free-audit`;
  const schema = {
    '@context': 'https://schema.org',
    '@type': key === 'audit' ? 'WebPage' : key === 'service' ? 'Service' : 'WebSite',
    name: data.title,
    url: canonical,
    description: data.description,
    inLanguage: locale,
    provider: { '@type': 'Organization', name: 'Lofts Studio', url: 'https://lofts.studio/' }
  };
  return `<!doctype html>
<html lang="${locale}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${data.title}</title>
  <meta name="description" content="${data.description}" />
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1" />
  <link rel="canonical" href="${canonical}" />
  ${alternates(key)}
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="${common.locale}" />
  <meta property="og:url" content="${canonical}" />
  <meta property="og:title" content="${data.title}" />
  <meta property="og:description" content="${data.description}" />
  <meta property="og:image" content="https://lofts.studio/assets/og.jpg?v=2" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="/assets/locale-pilot.css?v=20260925a" />
  <script type="application/ld+json">${JSON.stringify(schema)}</script>
</head>
<body class="locale-page">
  <a href="#content" style="position:absolute;left:-9999px;">Skip to content</a>
  <header class="locale-nav">
    <div class="locale-shell locale-nav__inner">
      <a class="locale-brand" href="${home}">Lofts<small>STUDIO</small></a>
      <nav class="locale-nav__links" aria-label="Main">
        <a href="${service}">${common.nav[0]}</a>
        <a href="${audit}">${common.nav[1]}</a>
        <a href="${audit}">${common.contact}</a>
      </nav>
    </div>
  </header>
  <main id="content">
    <section class="locale-hero">
      <div class="locale-shell">
        <p class="locale-eyebrow">${data.eyebrow}</p>
        <h1 class="locale-title">${data.heading}</h1>
        <p class="locale-lead">${data.lead}</p>
        <div class="locale-actions">
          <a class="locale-button" href="${audit}">${common.nav[1]}</a>
          <a class="locale-button locale-button--secondary" href="${service}">${common.nav[0]}</a>
        </div>
        <div class="locale-answer"><p>${data.answer}</p></div>
      </div>
    </section>
    <section class="locale-section">
      <div class="locale-shell">
        <p class="locale-eyebrow">Lofts Studio</p>
        <h2>${data.section}</h2>
        <div class="locale-grid">
          ${data.cards.map(([title, text]) => `<article class="locale-card"><h3>${title}</h3><p>${text}</p></article>`).join('\n          ')}
        </div>
      </div>
    </section>
  </main>
  <footer class="locale-footer"><div class="locale-shell locale-footer__inner"><span>© ${new Date().getFullYear()} Lofts Studio</span><span><a href="${home}">${common.label}</a> · <a href="/">English</a></span></div></footer>
  <script src="/assets/locale-switcher.js?v=20260925a" defer></script>
</body>
</html>`;
}

for (const [locale, common] of Object.entries(locales)) {
  for (const key of ['home', 'service', 'audit']) {
    const data = common[key];
    const relative = data.path === '/' ? `${locale}/index.html` : `${locale}${data.path}${data.path.endsWith('/') ? 'index.html' : ''}`;
    const target = join(root, relative);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, page(locale, common, key, data));
  }
}

console.log('Built 9 localized Lofts Studio pilot pages.');
