import { ComponentBase } from "./ComponentBase.js";

export class Modal extends ComponentBase {
  render() {
    this.contenedor.innerHTML = "";
    this.contenedor.className = "modal-overlay modal-oculto";

    this._caja = document.createElement("div");
    this._caja.className = "modal-caja";
    this.contenedor.appendChild(this._caja);

    this._escuchar(this.contenedor, "click", (evento) => {
      if (evento.target === this.contenedor) {
        this.cerrar();
      }
    });
  }

  abrir(contenidoHtml) {
    this._caja.innerHTML = contenidoHtml;
    this.contenedor.classList.remove("modal-oculto");
  }

  cerrar() {
    this.contenedor.classList.add("modal-oculto");
    this._caja.innerHTML = "";
  }

  confirmar(mensaje, { tituloConfirmar = "Confirmar", peligroso = true } = {}) {
    return new Promise((resolve) => {
      this._caja.innerHTML = `
        <p class="modal-mensaje">${mensaje}</p>
        <div class="modal-acciones">
          <button type="button" class="boton boton-secundario" data-accion="cancelar">Cancelar</button>
          <button type="button" class="boton ${peligroso ? "boton-peligro" : "boton-primario"}" data-accion="confirmar">${tituloConfirmar}</button>
        </div>
      `;
      this.contenedor.classList.remove("modal-oculto");

      const finalizar = (resultado) => {
        this.cerrar();
        resolve(resultado);
      };

      this._caja.querySelector('[data-accion="cancelar"]').addEventListener(
        "click",
        () => finalizar(false),
        { once: true },
      );
      this._caja.querySelector('[data-accion="confirmar"]').addEventListener(
        "click",
        () => finalizar(true),
        { once: true },
      );
    });
  }
}
