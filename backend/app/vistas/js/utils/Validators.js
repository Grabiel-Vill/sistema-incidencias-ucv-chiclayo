const REGEX_EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export class Validators {
  static esEmailValido(email) {
    return typeof email === "string" && REGEX_EMAIL.test(email.trim());
  }

  static esNoVacio(valor) {
    return typeof valor === "string" && valor.trim().length > 0;
  }

  static esEnteroPositivo(valor) {
    return Number.isInteger(valor) && valor > 0;
  }

  static tieneExtensionValida(nombreArchivo, extensionesPermitidas) {
    if (!Validators.esNoVacio(nombreArchivo)) {
      return false;
    }
    const nombre = nombreArchivo.toLowerCase();
    return extensionesPermitidas.some((extension) => nombre.endsWith(extension.toLowerCase()));
  }

  static esFechaFutura(valorIso) {
    if (!valorIso) {
      return false;
    }
    const fecha = new Date(valorIso);
    return !Number.isNaN(fecha.getTime()) && fecha.getTime() > Date.now();
  }
}
