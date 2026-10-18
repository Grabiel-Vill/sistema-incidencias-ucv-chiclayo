import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";

export class EmptyState extends ComponentBase {
  // props: { icono = "caja", titulo, descripcion?, accionTexto?, alAccionar? }
  render() {
    const { icono = "caja", titulo, descripcion, accionTexto, alAccionar } = this.props;

    this.contenedor.innerHTML = "";
    this.contenedor.className = "empty-state";

    const iconoEnvoltorio = document.createElement("div");
    iconoEnvoltorio.className = "empty-state-icono";
    iconoEnvoltorio.appendChild(Icon.elemento(icono, { tamano: 26, color: "var(--gris-400)" }));
    this.contenedor.appendChild(iconoEnvoltorio);

    const tituloElemento = document.createElement("p");
    tituloElemento.className = "empty-state-titulo";
    tituloElemento.textContent = titulo;
    this.contenedor.appendChild(tituloElemento);

    if (descripcion) {
      const descripcionElemento = document.createElement("p");
      descripcionElemento.className = "empty-state-descripcion";
      descripcionElemento.textContent = descripcion;
      this.contenedor.appendChild(descripcionElemento);
    }

    if (accionTexto && typeof alAccionar === "function") {
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "boton boton-primario";
      boton.textContent = accionTexto;
      this._escuchar(boton, "click", alAccionar);
      this.contenedor.appendChild(boton);
    }
  }
}
