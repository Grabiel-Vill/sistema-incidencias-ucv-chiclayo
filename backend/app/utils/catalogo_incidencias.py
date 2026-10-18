from app.models.enums import TipoFallaEnum

_CATALOGO = [
    {
        "categoria": "HARDWARE",
        "etiqueta": "Hardware",
        "subcategorias": [
            {"nombre": "Proyector no enciende", "tipo_falla": TipoFallaEnum.HARDWARE},
            {"nombre": "PC no enciende", "tipo_falla": TipoFallaEnum.HARDWARE},
            {"nombre": "Mouse/Teclado defectuoso", "tipo_falla": TipoFallaEnum.HARDWARE},
        ],
    },
    {
        "categoria": "RED",
        "etiqueta": "Red",
        "subcategorias": [
            {"nombre": "Sin internet", "tipo_falla": TipoFallaEnum.RED},
            {"nombre": "Wi-Fi inestable", "tipo_falla": TipoFallaEnum.RED},
            {"nombre": "Punto de red dañado", "tipo_falla": TipoFallaEnum.RED},
        ],
    },
    {
        "categoria": "SOFTWARE",
        "etiqueta": "Software",
        "subcategorias": [
            {"nombre": "Programa no abre", "tipo_falla": TipoFallaEnum.SOFTWARE},
            {"nombre": "Licencia vencida", "tipo_falla": TipoFallaEnum.SOFTWARE},
            {"nombre": "Sistema lento", "tipo_falla": TipoFallaEnum.SOFTWARE},
        ],
    },
    {
        "categoria": "ELECTRICIDAD_ILUMINACION",
        "etiqueta": "Electricidad/Iluminación",
        "subcategorias": [
            {"nombre": "Sin energía", "tipo_falla": TipoFallaEnum.ELECTRICIDAD},
            {"nombre": "Tomacorriente dañado", "tipo_falla": TipoFallaEnum.ELECTRICIDAD},
            {"nombre": "Luminaria apagada", "tipo_falla": TipoFallaEnum.ILUMINACION},
        ],
    },
]


class CatalogoIncidencias:
    """Fuente unica de categorias/subcategorias de falla (UI) y su tipo_falla real asociado.

    La categoria "Electricidad/Iluminacion" agrupa dos valores de TipoFallaEnum distintos
    (ELECTRICIDAD/ILUMINACION): el front elige la categoria y subcategoria, y este catalogo
    le dice que tipo_falla enviar al registrar la incidencia.
    """

    @staticmethod
    def obtener() -> list[dict]:
        return [
            {
                "categoria": entrada["categoria"],
                "etiqueta": entrada["etiqueta"],
                "subcategorias": [
                    {"nombre": sub["nombre"], "tipo_falla": sub["tipo_falla"].value}
                    for sub in entrada["subcategorias"]
                ],
            }
            for entrada in _CATALOGO
        ]

    @staticmethod
    def categoria_por_tipo_falla(tipo_falla: TipoFallaEnum) -> str:
        """Mapeo inverso: dado un tipo_falla ya clasificado (ej. por el chatbot), indica a que
        categoria de la UI pertenece (para precargar el primer desplegable del formulario)."""
        for entrada in _CATALOGO:
            if any(sub["tipo_falla"] == tipo_falla for sub in entrada["subcategorias"]):
                return entrada["categoria"]
        return tipo_falla.value
