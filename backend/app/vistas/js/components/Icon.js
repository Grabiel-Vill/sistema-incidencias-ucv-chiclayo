import { Icons } from "../utils/Icons.js";

// Icon es un helper estatico (como Toast) y no extiende ComponentBase: no gestiona estado
// propio ni listeners, solo produce un nodo <span> con el SVG embebido para que lo incrusten
// libremente otros componentes (Sidebar, StatCard, Toast, etc.) sin montar una subinstancia.
export class Icon {
  static elemento(nombre, opciones = {}) {
    const envoltorio = document.createElement("span");
    envoltorio.className = "icono";
    envoltorio.innerHTML = Icons.svg(nombre, opciones);
    return envoltorio;
  }
}
