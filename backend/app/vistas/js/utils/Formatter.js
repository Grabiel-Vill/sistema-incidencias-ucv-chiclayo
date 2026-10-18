const COLORES_PRIORIDAD = {
  ALTA: "var(--color-alta)",
  MEDIA: "var(--color-media)",
  BAJA: "var(--color-baja)",
};

const COLORES_ESTADO_INCIDENCIA = {
  RECIBIDO: "var(--color-recibido)",
  PROGRAMADO: "var(--color-programado)",
  EN_PROCESO: "var(--color-en-proceso)",
  RESUELTO: "var(--color-resuelto)",
};

const COLORES_ESTADO_EQUIPO = {
  OPERATIVO: "var(--color-operativo)",
  DEFECTUOSO: "var(--color-defectuoso)",
  EN_MANTENIMIENTO: "var(--color-en-mantenimiento)",
};

const EXTENSIONES_FORMATO = {
  PDF: "pdf",
  EXCEL: "xlsx",
};

export class Formatter {
  static fechaLegible(isoString) {
    if (!isoString) {
      return "-";
    }
    const fecha = new Date(isoString);
    if (Number.isNaN(fecha.getTime())) {
      return "-";
    }
    return fecha.toLocaleString("es-PE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  static fechaCorta(isoString) {
    if (!isoString) {
      return "-";
    }
    const fecha = new Date(isoString);
    if (Number.isNaN(fecha.getTime())) {
      return "-";
    }
    return fecha.toLocaleDateString("es-PE", { day: "2-digit", month: "short" });
  }

  static duracion(minutos) {
    if (minutos === null || minutos === undefined) {
      return "-";
    }
    const horas = Math.floor(minutos / 60);
    const minutosRestantes = Math.round(minutos % 60);
    return `${horas}h ${minutosRestantes}m`;
  }

  static prioridadColor(prioridad) {
    return COLORES_PRIORIDAD[prioridad] || "var(--color-texto-tenue)";
  }

  static estadoColor(estado) {
    return COLORES_ESTADO_INCIDENCIA[estado] || "var(--color-texto-tenue)";
  }

  static estadoEquipoColor(estado) {
    return COLORES_ESTADO_EQUIPO[estado] || "var(--color-texto-tenue)";
  }

  static formatoArchivo(formatoEnum) {
    return EXTENSIONES_FORMATO[formatoEnum] || "bin";
  }

  static iniciales(nombre, apellido) {
    const letraNombre = nombre ? nombre.trim().charAt(0) : "";
    const letraApellido = apellido ? apellido.trim().charAt(0) : "";
    return `${letraNombre}${letraApellido}`.toUpperCase() || "?";
  }
}
