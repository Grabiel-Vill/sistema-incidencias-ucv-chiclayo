import { CredencialesDTO } from "../models/CredencialesDTO.js";
import { TokenDTO } from "../models/TokenDTO.js";
import { UsuarioDTO } from "../models/UsuarioDTO.js";
import { SessionStore } from "../state/SessionStore.js";
import { ApiServiceBase } from "./ApiServiceBase.js";

export class AuthService extends ApiServiceBase {
  constructor(httpClient, sessionStore = SessionStore) {
    super(httpClient, "/auth");
    this._sessionStore = sessionStore;
  }

  async login(credencialesDTO) {
    const tokenJson = await this._http.post(`${this._rutaBase}/login`, credencialesDTO.toJSON());
    const token = TokenDTO.fromJSON(tokenJson);

    // El login solo devuelve el token; guardamos primero el token (HttpClient lo necesita
    // para autenticar la siguiente llamada) y luego pedimos el perfil completo.
    this._sessionStore.iniciarSesion(token.accessToken, null);
    const perfilJson = await this._http.get("/auth/me");
    const usuario = UsuarioDTO.fromJSON(perfilJson);
    this._sessionStore.iniciarSesion(token.accessToken, usuario);

    return token;
  }

  async logout() {
    try {
      await this._http.post(`${this._rutaBase}/logout`);
    } finally {
      this._sessionStore.cerrarSesion();
    }
  }
}
