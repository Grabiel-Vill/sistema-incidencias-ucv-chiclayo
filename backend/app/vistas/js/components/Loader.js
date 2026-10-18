import { ComponentBase } from "./ComponentBase.js";

export class Loader extends ComponentBase {
  // props: { texto = "Cargando..." }
  render() {
    this.contenedor.innerHTML = "";
    this.contenedor.className = "loader";

    const spinner = document.createElement("span");
    spinner.className = "loader-spinner";
    this.contenedor.appendChild(spinner);

    const texto = document.createElement("span");
    texto.className = "loader-texto";
    texto.textContent = this.props.texto || "Cargando...";
    this.contenedor.appendChild(texto);
  }
}
