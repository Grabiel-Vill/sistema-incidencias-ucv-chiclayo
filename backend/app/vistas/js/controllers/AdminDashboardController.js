import { BarChart } from "../components/BarChart.js";
import { StatCard } from "../components/StatCard.js";
import { Toast } from "../components/Toast.js";
import { DashboardService } from "../services/DashboardService.js";
import { ApiException } from "../utils/ApiException.js";
import { Formatter } from "../utils/Formatter.js";
import { PageControllerBase } from "./PageControllerBase.js";

const FORMATOS = [
  { valor: "PDF", texto: "PDF" },
  { valor: "EXCEL", texto: "Excel" },
];

export class AdminDashboardController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["ADMINISTRADOR"], "Dashboard");
  }

  inicializar() {
    this.dashboardService = new DashboardService(this.http);
    this.statCards = [];
    this._montarExportar();
    this._cargarMetricas();
  }

  async _cargarMetricas() {
    try {
      const metricas = await this.dashboardService.obtenerMetricas();
      this._pintarStats(metricas);
      this._pintarGraficoKpis(metricas.kpisLaboratorios);
      this._pintarGraficoFallas(metricas.frecuenciaFallas);
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudieron cargar las metricas";
      Toast.error(mensaje);
    }
  }

  _pintarStats(metricas) {
    const resumenes = Object.values(metricas.kpisLaboratorios || {});
    const totalIncidencias = resumenes.reduce((acc, r) => acc + r.total_incidencias, 0);
    const resueltas = resumenes.reduce((acc, r) => acc + r.resueltas, 0);
    const tiempos = resumenes
      .map((r) => r.tiempo_promedio_atencion_minutos)
      .filter((tiempo) => tiempo !== null && tiempo !== undefined);
    const tiempoPromedio = tiempos.length ? tiempos.reduce((a, b) => a + b, 0) / tiempos.length : null;

    const contenedor = document.getElementById("contenedor-stats");
    for (const card of this.statCards) {
      card.destruir();
    }
    contenedor.innerHTML = "";
    contenedor.className = "contenedor-stats";

    const datos = [
      { titulo: "Total de incidencias", valor: String(totalIncidencias), icono: "ticket" },
      { titulo: "Resueltas", valor: String(resueltas), icono: "check" },
      { titulo: "Laboratorios monitoreados", valor: String(resumenes.length), icono: "laboratorio" },
      { titulo: "Tiempo promedio de atencion", valor: Formatter.duracion(tiempoPromedio), icono: "reloj" },
      {
        titulo: "Evaluacion promedio de tecnicos",
        valor:
          metricas.evaluacionPromedioTecnicos === null || metricas.evaluacionPromedioTecnicos === undefined
            ? "Sin datos"
            : `${metricas.evaluacionPromedioTecnicos.toFixed(1)}/5`,
        icono: "estrella",
      },
      {
        titulo: "Cumplimiento de aperturas anticipadas",
        valor:
          metricas.puntualidadApertura === null || metricas.puntualidadApertura === undefined
            ? "Sin datos"
            : `${metricas.puntualidadApertura}%`,
        icono: "reloj",
      },
    ];

    this.statCards = datos.map((dato) => {
      const espacio = document.createElement("div");
      contenedor.appendChild(espacio);
      return new StatCard(espacio, dato);
    });
  }

  _pintarGraficoKpis(kpisLaboratorios) {
    const resumenes = Object.values(kpisLaboratorios || {});
    const contenedor = document.getElementById("contenedor-grafico-kpis");
    this.graficoKpis?.destruir();
    this.graficoKpis = new BarChart(contenedor, {
      etiquetas: resumenes.map((resumen) => resumen.laboratorio),
      valores: resumenes.map((resumen) => resumen.total_incidencias),
      colorBarra: "#4f46e5",
    });
  }

  _pintarGraficoFallas(frecuenciaFallas) {
    const contenedor = document.getElementById("contenedor-grafico-fallas");
    this.graficoFallas?.destruir();
    this.graficoFallas = new BarChart(contenedor, {
      etiquetas: Object.keys(frecuenciaFallas || {}),
      valores: Object.values(frecuenciaFallas || {}),
      colorBarra: "#f59e0b",
    });
  }

  _montarExportar() {
    const contenedor = document.getElementById("contenedor-exportar");
    contenedor.innerHTML = "";

    const selectFormato = document.createElement("select");
    for (const formato of FORMATOS) {
      const opcion = document.createElement("option");
      opcion.value = formato.valor;
      opcion.textContent = formato.texto;
      selectFormato.appendChild(opcion);
    }
    contenedor.appendChild(selectFormato);

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "boton boton-primario";
    boton.textContent = "Exportar reporte";
    boton.addEventListener("click", () => this._exportar(selectFormato.value));
    contenedor.appendChild(boton);
  }

  async _exportar(formato) {
    try {
      const blob = await this.dashboardService.exportarReporte(formato);
      const extension = Formatter.formatoArchivo(formato);
      this._descargarBlob(blob, `reporte-mantenimiento.${extension}`);
      Toast.exito("Reporte exportado");
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo exportar el reporte";
      Toast.error(mensaje);
    }
  }

  _descargarBlob(blob, nombreArchivo) {
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = nombreArchivo;
    enlace.click();
    URL.revokeObjectURL(url);
  }
}
