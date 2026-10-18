import { ComponentBase } from "./ComponentBase.js";
import { Icon } from "./Icon.js";

export class StatCard extends ComponentBase {
  // props: { titulo, valor, icono = "dashboard", tendenciaTexto?, tendenciaPositiva = true }
  render() {
    const { titulo, valor, icono = "dashboard", tendenciaTexto, tendenciaPositiva = true } = this.props;

    this.contenedor.innerHTML = "";
    this.contenedor.className = "stat-card";

    const encabezado = document.createElement("div");
    encabezado.className = "stat-card-encabezado";

    const etiqueta = document.createElement("span");
    etiqueta.className = "stat-card-titulo";
    etiqueta.textContent = titulo;
    encabezado.appendChild(etiqueta);

    const iconoEnvoltorio = document.createElement("span");
    iconoEnvoltorio.className = "stat-card-icono";
    iconoEnvoltorio.appendChild(Icon.elemento(icono, { tamano: 18, color: "var(--marca-600)" }));
    encabezado.appendChild(iconoEnvoltorio);
    this.contenedor.appendChild(encabezado);

    const valorElemento = document.createElement("p");
    valorElemento.className = "stat-card-valor";
    valorElemento.textContent = valor;
    this.contenedor.appendChild(valorElemento);

    if (tendenciaTexto) {
      const tendencia = document.createElement("div");
      tendencia.className = `stat-card-tendencia ${tendenciaPositiva ? "stat-card-tendencia-positiva" : "stat-card-tendencia-negativa"}`;
      tendencia.appendChild(Icon.elemento("tendencia", { tamano: 14 }));
      const textoTendencia = document.createElement("span");
      textoTendencia.textContent = tendenciaTexto;
      tendencia.appendChild(textoTendencia);
      this.contenedor.appendChild(tendencia);
    }
  }
}
