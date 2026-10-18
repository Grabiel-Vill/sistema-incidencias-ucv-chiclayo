import { Loader } from "../components/Loader.js";
import { Toast } from "../components/Toast.js";
import { ReporteService } from "../services/ReporteService.js";
import { ApiException } from "../utils/ApiException.js";
import { Formatter } from "../utils/Formatter.js";
import { PageControllerBase } from "./PageControllerBase.js";

const FORMATOS = ["PDF", "EXCEL"];

export class AdminReportesController extends PageControllerBase {
  constructor(contenedor) {
    super(contenedor, ["ADMINISTRADOR"], "Reportes");
  }

  inicializar() {
    this.reporteService = new ReporteService(this.http);
    this._montarGenerar();
    this._contenedorHistorial = document.getElementById("contenedor-historial-reportes");
    this._cargarHistorial();
  }

  _montarGenerar() {
    const contenedor = document.getElementById("contenedor-generar-reporte");
    contenedor.innerHTML = "";

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "boton boton-primario";
    boton.textContent = "Generar nuevo reporte";
    boton.addEventListener("click", () => this._generar(boton));
    contenedor.appendChild(boton);
  }

  async _generar(boton) {
    boton.disabled = true;
    try {
      await this.reporteService.generar();
      Toast.exito("Reporte generado");
      this._cargarHistorial();
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo generar el reporte";
      Toast.error(mensaje);
    } finally {
      boton.disabled = false;
    }
  }

  async _cargarHistorial() {
    new Loader(this._contenedorHistorial, { texto: "Cargando historial..." });
    try {
      const reportes = await this.reporteService.listarHistorial();
      this._pintarHistorial(reportes);
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo cargar el historial";
      Toast.error(mensaje);
    }
  }

  _pintarHistorial(reportes) {
    this._contenedorHistorial.innerHTML = "";

    if (reportes.length === 0) {
      const vacio = document.createElement("p");
      vacio.className = "texto-marcador";
      vacio.textContent = "Aun no se ha generado ningun reporte.";
      this._contenedorHistorial.appendChild(vacio);
      return;
    }

    const envoltorio = document.createElement("div");
    envoltorio.className = "tabla-incidencias-envoltorio";

    const tabla = document.createElement("table");
    const encabezado = document.createElement("thead");
    encabezado.innerHTML = "<tr><th>Fecha</th><th></th></tr>";
    tabla.appendChild(encabezado);

    const cuerpo = document.createElement("tbody");
    for (const reporte of reportes) {
      const fila = document.createElement("tr");

      const celdaFecha = document.createElement("td");
      celdaFecha.textContent = Formatter.fechaLegible(reporte.fechaGeneracion);
      fila.appendChild(celdaFecha);

      const celdaExportar = document.createElement("td");
      celdaExportar.className = "tabla-incidencias-acciones";
      for (const formato of FORMATOS) {
        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "boton boton-secundario boton-sm";
        boton.textContent = formato;
        boton.addEventListener("click", () => this._exportar(reporte, formato));
        celdaExportar.appendChild(boton);
      }
      fila.appendChild(celdaExportar);

      cuerpo.appendChild(fila);
    }
    tabla.appendChild(cuerpo);
    envoltorio.appendChild(tabla);
    this._contenedorHistorial.appendChild(envoltorio);
  }

  async _exportar(reporte, formato) {
    try {
      const blob = await this.reporteService.exportar(reporte.idReporte, formato);
      const extension = Formatter.formatoArchivo(formato);
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement("a");
      enlace.href = url;
      enlace.download = `reporte-${reporte.idReporte}.${extension}`;
      enlace.click();
      URL.revokeObjectURL(url);
      Toast.exito("Descarga iniciada");
    } catch (error) {
      const mensaje = error instanceof ApiException ? error.message : "No se pudo exportar el reporte";
      Toast.error(mensaje);
    }
  }
}
