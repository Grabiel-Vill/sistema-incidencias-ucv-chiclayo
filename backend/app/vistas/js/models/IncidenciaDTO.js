import { ApiException } from "../utils/ApiException.js";
import { Validators } from "../utils/Validators.js";

export class IncidenciaDTO {
  constructor(
    descripcion,
    tipoFalla,
    idLaboratorio,
    idEquipo = null,
    tipoRequerimiento = "FALLA_TECNICA",
    fechaHoraApertura = null,
    subcategoria = null,
  ) {
    if (!Validators.esNoVacio(descripcion)) {
      throw new ApiException("VALIDACION", "La descripcion no puede estar vacia");
    }
    if (!Validators.esEnteroPositivo(idLaboratorio)) {
      throw new ApiException("VALIDACION", "El laboratorio es obligatorio");
    }
    if (tipoRequerimiento === "APERTURA_ANTICIPADA") {
      if (!fechaHoraApertura) {
        throw new ApiException("VALIDACION", "La apertura anticipada requiere fecha y hora de inicio de clase");
      }
      if (!Validators.esFechaFutura(fechaHoraApertura)) {
        throw new ApiException("VALIDACION", "La fecha y hora de apertura anticipada debe ser futura");
      }
    }
    this.descripcion = descripcion.trim();
    this.tipoFalla = tipoFalla;
    this.idLaboratorio = idLaboratorio;
    this.idEquipo = idEquipo;
    this.tipoRequerimiento = tipoRequerimiento;
    this.fechaHoraApertura = fechaHoraApertura;
    this.subcategoria = subcategoria;
  }

  toJSON() {
    return {
      descripcion: this.descripcion,
      tipo_falla: this.tipoFalla,
      id_laboratorio: this.idLaboratorio,
      id_equipo: this.idEquipo,
      tipo_requerimiento: this.tipoRequerimiento,
      fecha_hora_apertura: this.fechaHoraApertura,
      subcategoria: this.subcategoria,
    };
  }
}
