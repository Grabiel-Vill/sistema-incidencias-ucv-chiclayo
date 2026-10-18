const ICONOS = {
  dashboard: '<rect x="3" y="3" width="7" height="9" rx="1.5"></rect><rect x="14" y="3" width="7" height="5" rx="1.5"></rect><rect x="14" y="12" width="7" height="9" rx="1.5"></rect><rect x="3" y="16" width="7" height="5" rx="1.5"></rect>',
  usuarios: '<circle cx="9" cy="8" r="3.2"></circle><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"></path><circle cx="17" cy="9" r="2.4"></circle><path d="M21 20c0-2.6-1.8-4.8-4.2-5.5"></path>',
  laboratorio: '<path d="M9 2.5h6"></path><path d="M10 3v6.5L4.8 18a2 2 0 0 0 1.7 3h10.9a2 2 0 0 0 1.7-3L14 9.5V3"></path><path d="M7.5 14.5h9"></path>',
  equipo: '<rect x="3" y="4" width="18" height="12" rx="1.5"></rect><path d="M8 20h8"></path><path d="M12 16v4"></path>',
  campana: '<path d="M6 10a6 6 0 0 1 12 0c0 4 1.5 5.5 1.5 5.5h-15S6 14 6 10Z"></path><path d="M10 19a2 2 0 0 0 4 0"></path>',
  chat: '<path d="M4 5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5v9A1.5 1.5 0 0 1 18.5 16H9l-4.5 4v-4H5.5A1.5 1.5 0 0 1 4 14.5Z"></path>',
  salir: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><path d="M16 17l5-5-5-5"></path><path d="M21 12H9"></path>',
  mas: '<path d="M12 5v14"></path><path d="M5 12h14"></path>',
  check: '<path d="M20 6 9 17l-5-5"></path>',
  alerta: '<path d="M12 3 2 20h20L12 3Z"></path><path d="M12 10v4"></path><path d="M12 17h.01"></path>',
  buscar: '<circle cx="10.5" cy="10.5" r="6.5"></circle><path d="M20 20l-4.3-4.3"></path>',
  descargar: '<path d="M12 3v12"></path><path d="M7 10l5 5 5-5"></path><path d="M5 20h14"></path>',
  chevronAbajo: '<path d="M6 9l6 6 6-6"></path>',
  chevronDerecha: '<path d="M9 6l6 6-6 6"></path>',
  ticket: '<path d="M3 9.5V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2.5a1.5 1.5 0 0 0 0 3V15a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2.5a1.5 1.5 0 0 0 0-3Z"></path><path d="M14 5.5v13"></path>',
  menu: '<path d="M4 7h16"></path><path d="M4 12h16"></path><path d="M4 17h16"></path>',
  cerrar: '<path d="M6 6l12 12"></path><path d="M18 6L6 18"></path>',
  reloj: '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3.5 2"></path>',
  tendencia: '<path d="M3 17l6-6 4 4 7-8"></path><path d="M15 7h5v5"></path>',
  enviar: '<path d="M21 3 3 10.5l7.5 3L13.5 21 21 3Z"></path>',
  reportes: '<path d="M7 3h7l4 4v14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"></path><path d="M14 3v4h4"></path><path d="M9 13h6"></path><path d="M9 17h6"></path>',
  bandeja: '<path d="M3 11l2.5-6A1.5 1.5 0 0 1 6.9 4h10.2a1.5 1.5 0 0 1 1.4 1l2.5 6"></path><path d="M3 11v6a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-6H15a3 3 0 0 1-6 0Z"></path>',
  ojo: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"></path><circle cx="12" cy="12" r="3"></circle>',
  ojoOculto: '<path d="M3 3l18 18"></path><path d="M10.6 6.1A10 10 0 0 1 12 6c6.4 0 10 6 10 6a17 17 0 0 1-3.2 3.9"></path><path d="M6.6 6.7A16.6 16.6 0 0 0 2 12s3.6 6 10 6a9.8 9.8 0 0 0 4.2-.9"></path><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"></path>',
  correo: '<rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="M3.5 7l8.5 6 8.5-6"></path>',
  candado: '<rect x="5" y="11" width="14" height="9" rx="2"></rect><path d="M8 11V8a4 4 0 0 1 8 0v3"></path>',
  persona: '<circle cx="12" cy="8" r="3.6"></circle><path d="M4.5 20c0-4 3.4-6.5 7.5-6.5s7.5 2.5 7.5 6.5"></path>',
  credencial: '<rect x="3" y="5" width="18" height="14" rx="2"></rect><circle cx="9" cy="11" r="2"></circle><path d="M6.5 16c.4-1.6 1.4-2.4 2.5-2.4s2.1.8 2.5 2.4"></path><path d="M14.5 10h4"></path><path d="M14.5 14h3"></path>',
  caja: '<circle cx="12" cy="12" r="9"></circle><path d="M8 12l3 3 5-6"></path>',
  estrella: '<path d="M12 2.5l2.9 6.4 6.9.8-5.1 4.7 1.4 6.9L12 17.9l-6.1 3.4 1.4-6.9-5.1-4.7 6.9-.8Z"></path>',
};

export class Icons {
  static svg(nombre, { tamano = 20, color = "currentColor", grosor = 1.8 } = {}) {
    const contenido = ICONOS[nombre];
    if (!contenido) {
      return "";
    }
    return `<svg width="${tamano}" height="${tamano}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${grosor}" stroke-linecap="round" stroke-linejoin="round">${contenido}</svg>`;
  }

  static disponibles() {
    return Object.keys(ICONOS);
  }
}
