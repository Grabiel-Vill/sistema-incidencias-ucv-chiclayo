export class ApiServiceBase {
  constructor(httpClient, rutaBase) {
    this._http = httpClient;
    this._rutaBase = rutaBase;
  }
}
