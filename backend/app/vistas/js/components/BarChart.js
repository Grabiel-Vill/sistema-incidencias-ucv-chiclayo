import { ComponentBase } from "./ComponentBase.js";
import { EmptyState } from "./EmptyState.js";

const ALTO_PX = 230;
const PADDING_IZQ = 32;
const PADDING_DER = 16;
const PADDING_VERT = 28;
const LINEAS_GRID = 4;

export class BarChart extends ComponentBase {
  // props: { etiquetas: string[], valores: number[], colorBarra = "#4f46e5" }
  render() {
    const { etiquetas = [], valores = [] } = this.props;

    this.contenedor.innerHTML = "";
    this.contenedor.className = "grafico-barras";

    if (valores.length === 0 || valores.every((valor) => !valor)) {
      new EmptyState(this.contenedor, {
        icono: "dashboard",
        titulo: "Sin datos suficientes",
        descripcion: "Aun no hay incidencias registradas para graficar.",
      });
      return;
    }

    this._canvas = document.createElement("canvas");
    this._canvas.className = "grafico-barras-lienzo";
    this._canvas.width = this.contenedor.clientWidth || 480;
    this._canvas.height = ALTO_PX;
    this.contenedor.appendChild(this._canvas);

    const etiquetasDiv = document.createElement("div");
    etiquetasDiv.className = "grafico-barras-leyenda";
    this.contenedor.appendChild(etiquetasDiv);

    this._dibujar(etiquetas, valores);
  }

  _dibujar(etiquetas, valores) {
    const contexto = this._canvas.getContext && this._canvas.getContext("2d");
    if (!contexto) {
      return;
    }

    const colorBarra = this.props.colorBarra || "#4f46e5";
    const ancho = this._canvas.width;
    const alto = this._canvas.height;
    const maximo = Math.max(1, ...valores);
    const areaUtilAncho = ancho - PADDING_IZQ - PADDING_DER;
    const areaUtilAlto = alto - PADDING_VERT * 2;
    const anchoBarra = areaUtilAncho / Math.max(1, valores.length);

    contexto.clearRect(0, 0, ancho, alto);

    // Lineas de referencia horizontales
    contexto.strokeStyle = "#e2e8f0";
    contexto.lineWidth = 1;
    contexto.fillStyle = "#94a3b8";
    contexto.font = "11px Inter, sans-serif";
    contexto.textAlign = "right";
    for (let i = 0; i <= LINEAS_GRID; i += 1) {
      const y = PADDING_VERT + (areaUtilAlto * i) / LINEAS_GRID;
      contexto.beginPath();
      contexto.moveTo(PADDING_IZQ, y);
      contexto.lineTo(ancho - PADDING_DER, y);
      contexto.stroke();
      const valorEtiqueta = Math.round(maximo - (maximo * i) / LINEAS_GRID);
      contexto.fillText(String(valorEtiqueta), PADDING_IZQ - 8, y + 3);
    }

    valores.forEach((valor, indice) => {
      const alturaBarra = (areaUtilAlto * valor) / maximo;
      const x = PADDING_IZQ + indice * anchoBarra + anchoBarra * 0.18;
      const anchoReal = anchoBarra * 0.64;
      const y = PADDING_VERT + areaUtilAlto - alturaBarra;

      const degradado = contexto.createLinearGradient(0, y, 0, y + alturaBarra);
      degradado.addColorStop(0, colorBarra);
      degradado.addColorStop(1, `${colorBarra}99`);
      contexto.fillStyle = degradado;
      _rectRedondeado(contexto, x, y, anchoReal, alturaBarra, 4);

      contexto.fillStyle = "#1e293b";
      contexto.font = "600 11px Inter, sans-serif";
      contexto.textAlign = "center";
      contexto.fillText(String(valor), x + anchoReal / 2, Math.max(14, y - 6));
    });

    const leyenda = this.contenedor.querySelector(".grafico-barras-leyenda");
    leyenda.innerHTML = "";
    leyenda.style.paddingLeft = `${PADDING_IZQ}px`;
    valores.forEach((_valor, indice) => {
      const item = document.createElement("span");
      item.style.width = `${(100 / valores.length).toFixed(2)}%`;
      item.textContent = etiquetas[indice] ?? "";
      leyenda.appendChild(item);
    });
  }
}

function _rectRedondeado(contexto, x, y, ancho, alto, radio) {
  const r = Math.min(radio, ancho / 2, alto / 2 > 0 ? alto / 2 : 0);
  contexto.beginPath();
  contexto.moveTo(x + r, y);
  contexto.lineTo(x + ancho - r, y);
  contexto.quadraticCurveTo(x + ancho, y, x + ancho, y + r);
  contexto.lineTo(x + ancho, y + alto);
  contexto.lineTo(x, y + alto);
  contexto.lineTo(x, y + r);
  contexto.quadraticCurveTo(x, y, x + r, y);
  contexto.closePath();
  contexto.fill();
}
