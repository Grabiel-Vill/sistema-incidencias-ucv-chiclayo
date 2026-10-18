from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from app.exceptions import AccesoDenegadoException, CredencialesInvalidasException, ValidacionException
from app.models.enums import RolEnum
from app.utils.password_hasher import PasswordHasher

if TYPE_CHECKING:
    from app.models.notificacion import Notificacion

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Usuario(ABC):
    """Clase base abstracta de la jerarquia de usuarios (Docente, Tecnico, Administrador)."""

    def __init__(
        self,
        id_usuario: int,
        codigo_ucv: str,
        nombre: str,
        apellido: str,
        email: str,
        password_hash: str,
        estado: bool = True,
    ):
        self._id_usuario = id_usuario
        self.codigo_ucv = codigo_ucv
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self._password_hash = password_hash
        self._estado = estado
        self._sesion_activa = False
        self._notificaciones: list["Notificacion"] = []

    # --- Encapsulamiento: atributos privados expuestos mediante propiedades validadas ---

    @property
    def id_usuario(self) -> int:
        return self._id_usuario

    @property
    def codigo_ucv(self) -> str:
        return self._codigo_ucv

    @codigo_ucv.setter
    def codigo_ucv(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El codigo UCV no puede estar vacio", campo="codigo_ucv")
        self._codigo_ucv = valor.strip()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El nombre no puede estar vacio", campo="nombre")
        self._nombre = valor.strip()

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ValidacionException("El apellido no puede estar vacio", campo="apellido")
        self._apellido = valor.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or not _EMAIL_REGEX.match(valor):
            raise ValidacionException("El email no tiene un formato valido", campo="email")
        self._email = valor.strip().lower()

    @property
    def estado(self) -> bool:
        return self._estado

    @property
    def nombre_completo(self) -> str:
        return f"{self._nombre} {self._apellido}"

    # --- Abstraccion / Polimorfismo: cada subclase define su propio rol y permisos ---

    @abstractmethod
    def obtener_rol(self) -> RolEnum:
        """Cada subclase concreta indica a que rol de RolEnum pertenece."""

    def tiene_permiso(self, accion: str) -> bool:
        return False

    # --- Autenticacion (RF: iniciar/cerrar sesion con credenciales UCV) ---

    def verificar_password(self, password_plano: str) -> bool:
        return PasswordHasher.verificar_password(password_plano, self._password_hash)

    def cambiar_password(self, password_actual: str, password_nuevo: str) -> None:
        if not self.verificar_password(password_actual):
            raise CredencialesInvalidasException("La contrasena actual no coincide")
        if not password_nuevo or len(password_nuevo) < 8:
            raise ValidacionException("La nueva contrasena debe tener al menos 8 caracteres", campo="password")
        self._password_hash = PasswordHasher.hash_password(password_nuevo)

    def iniciar_sesion(self, password_plano: str) -> dict:
        if not self._estado:
            raise AccesoDenegadoException("El usuario se encuentra inactivo")
        if not self.verificar_password(password_plano):
            raise CredencialesInvalidasException()
        self._sesion_activa = True
        return {
            "id_usuario": self._id_usuario,
            "codigo_ucv": self._codigo_ucv,
            "rol": self.obtener_rol().value,
            "emitido_en": datetime.now().isoformat(),
        }

    def cerrar_sesion(self) -> None:
        self._sesion_activa = False

    @property
    def sesion_activa(self) -> bool:
        return self._sesion_activa

    @staticmethod
    def generar_password_hash(password_plano: str) -> str:
        return PasswordHasher.hash_password(password_plano)

    def restablecer_password(self, password_nuevo: str) -> None:
        """Fija una contrasena nueva sin requerir la actual (accion exclusiva del Administrador)."""
        self._password_hash = PasswordHasher.hash_password(password_nuevo)

    # --- Gestion de cuenta (usada por Administrador.gestionar_usuario) ---

    def activar(self) -> None:
        self._estado = True

    def desactivar(self) -> None:
        self._estado = False
        self._sesion_activa = False

    # --- Asociacion Usuario 1 -- 0..* Notificacion ---

    def recibir_notificacion(self, notificacion: "Notificacion") -> None:
        self._notificaciones.append(notificacion)

    def listar_notificaciones(self, solo_no_leidas: bool = False) -> list["Notificacion"]:
        if solo_no_leidas:
            return [n for n in self._notificaciones if not n.leido]
        return list(self._notificaciones)

    # --- Sobrecarga de operadores: dos usuarios son iguales si comparten id ---

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Usuario) and self._id_usuario == other._id_usuario

    def __hash__(self) -> int:
        return hash(self._id_usuario)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id_usuario}, codigo_ucv='{self._codigo_ucv}')"
