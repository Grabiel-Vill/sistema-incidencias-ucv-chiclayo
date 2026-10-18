import { Icon } from "./Icon.js";

const DURACION_MS = 4000;
const ID_CONTENEDOR = "contenedor-toasts";

const VARIANTES = {
  exito: { clase: "toast-exito", icono: "check" },
  error: { clase: "toast-error", icono: "alerta" },
  info: { clase: "toast-info", icono: "campana" },
};

export class Toast {
  static exito(mensaje) {
    Toast._mostrar(mensaje, VARIANTES.exito);
  }

  static error(mensaje) {
    Toast._mostrar(mensaje, VARIANTES.error);
  }

  static info(mensaje) {
    Toast._mostrar(mensaje, VARIANTES.info);
  }

  static _obtenerContenedor() {
    let contenedor = document.getElementById(ID_CONTENEDOR);
    if (!contenedor) {
      contenedor = document.createElement("div");
      contenedor.id = ID_CONTENEDOR;
      contenedor.className = "contenedor-toasts";
      document.body.appendChild(contenedor);
    }
    return contenedor;
  }

  static _mostrar(mensaje, { clase, icono }) {
    const contenedor = Toast._obtenerContenedor();
    const toast = document.createElement("div");
    toast.className = `toast ${clase}`;

    toast.appendChild(Icon.elemento(icono, { tamano: 18 }));

    const texto = document.createElement("span");
    texto.textContent = mensaje;
    toast.appendChild(texto);

    contenedor.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add("toast-visible"));

    setTimeout(() => {
      toast.classList.remove("toast-visible");
      setTimeout(() => toast.remove(), 200);
    }, DURACION_MS);
  }
}
