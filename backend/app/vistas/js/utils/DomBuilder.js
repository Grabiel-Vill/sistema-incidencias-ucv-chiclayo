export function el(tag, atributos = {}, hijos = []) {
  const elemento = document.createElement(tag);

  for (const [clave, valor] of Object.entries(atributos)) {
    if (valor === undefined || valor === null || valor === false) {
      continue;
    }
    if (clave === "className") {
      elemento.className = valor;
    } else if (clave === "html") {
      elemento.innerHTML = valor;
    } else if (clave === "texto") {
      elemento.textContent = valor;
    } else if (clave.startsWith("on") && typeof valor === "function") {
      elemento.addEventListener(clave.slice(2).toLowerCase(), valor);
    } else if (clave in elemento) {
      elemento[clave] = valor;
    } else {
      elemento.setAttribute(clave, valor);
    }
  }

  const listaHijos = Array.isArray(hijos) ? hijos : [hijos];
  for (const hijo of listaHijos) {
    if (hijo === null || hijo === undefined || hijo === false) {
      continue;
    }
    elemento.appendChild(typeof hijo === "string" ? document.createTextNode(hijo) : hijo);
  }

  return elemento;
}

export function limpiar(elemento) {
  elemento.innerHTML = "";
}
