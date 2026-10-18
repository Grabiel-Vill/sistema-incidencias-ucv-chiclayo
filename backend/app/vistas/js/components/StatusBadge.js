import { Formatter } from "../utils/Formatter.js";
import { ComponentBase } from "./ComponentBase.js";

const ETIQUETAS = {
  RECIBIDO: "Recibido",
  PROGRAMADO: "Programado",
  EN_PROCESO: "En proceso",
  RESUELTO: "Resuelto",
  ALTA: "Alta",
  MEDIA: "Media",
  BAJA: "Baja",
  OPERATIVO: "Operativo",
  DEFECTUOSO: "Defectuoso",
  EN_MANTENIMIENTO: "En mantenimiento",
};

export class StatusBadge extends ComponentBase {
  // props: { valor, tipo: "estado" | "prioridad" | "estadoEquipo", etiquetas?: objeto que sobreescribe
  // la etiqueta por defecto para un valor puntual (ej. PROGRAMADO="Tecnico asignado" para el docente,
  // "Pendiente" para el tecnico) }
  render() {
    const { valor, tipo = "estado", etiquetas = {} } = this.props;
    const color = StatusBadge._colorPara(tipo, valor);

    this.contenedor.innerHTML = "";
    const pastilla = document.createElement("span");
    pastilla.className = "badge-estado";
    pastilla.style.setProperty("--color-badge", color);

    const punto = document.createElement("span");
    punto.className = "badge-estado-punto";
    pastilla.appendChild(punto);

    const texto = document.createElement("span");
    texto.textContent = etiquetas[valor] || ETIQUETAS[valor] || valor || "-";
    pastilla.appendChild(texto);

    this.contenedor.appendChild(pastilla);
  }

  static _colorPara(tipo, valor) {
    if (tipo === "prioridad") {
      return Formatter.prioridadColor(valor);
    }
    if (tipo === "estadoEquipo") {
      return Formatter.estadoEquipoColor(valor);
    }
    return Formatter.estadoColor(valor);
  }
}
