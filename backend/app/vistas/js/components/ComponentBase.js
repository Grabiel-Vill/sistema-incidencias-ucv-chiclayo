export class ComponentBase {
  constructor(contenedor, props = {}) {
    if (!contenedor) {
      throw new Error("ComponentBase requiere un elemento contenedor");
    }
    this.contenedor = contenedor;
    this.props = props;
    this._listenersRegistrados = [];
    this.render();
  }

  render() {
    throw new Error("render() debe ser implementado por la subclase");
  }

  actualizar(nuevasProps = {}) {
    this._limpiarListeners();
    this.props = { ...this.props, ...nuevasProps };
    this.render();
  }

  destruir() {
    this._limpiarListeners();
    this.contenedor.innerHTML = "";
  }

  _escuchar(elemento, evento, manejador) {
    elemento.addEventListener(evento, manejador);
    this._listenersRegistrados.push({ elemento, evento, manejador });
  }

  _limpiarListeners() {
    for (const { elemento, evento, manejador } of this._listenersRegistrados) {
      elemento.removeEventListener(evento, manejador);
    }
    this._listenersRegistrados = [];
  }
}
