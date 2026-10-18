import { RespuestaIADTO } from "../models/RespuestaIADTO.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class ChatbotService extends ApiServiceBase {
  constructor(httpClient) {
    super(httpClient, "/chatbot");
  }

  async procesarMensaje(mensaje, idLaboratorio, idEquipo = null) {
    const json = await this._http.post(`${this._rutaBase}/mensaje`, {
      mensaje,
      id_laboratorio: idLaboratorio,
      id_equipo: idEquipo,
    });
    return RespuestaIADTO.fromJSON(json);
  }
}
