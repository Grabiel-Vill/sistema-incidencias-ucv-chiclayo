import smtplib
from email.message import EmailMessage

from app.config.settings import Settings


class EmailClient:
    """Envio de correos (opcional) para notificaciones de asignacion/cambio de estado."""

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self.host = self._settings.obtener("SMTP_HOST")
        self.puerto = self._settings.obtener_entero("SMTP_PORT", 587)
        self.usuario = self._settings.obtener("SMTP_USER")
        self.password = self._settings.obtener("SMTP_PASSWORD")
        self.remitente = self._settings.obtener("SMTP_FROM") or self.usuario

    @property
    def esta_configurado(self) -> bool:
        return all([self.host, self.usuario, self.password])

    def enviar(self, destinatario: str, asunto: str, cuerpo: str) -> bool:
        if not self.esta_configurado:
            return False

        mensaje = EmailMessage()
        mensaje["Subject"] = asunto
        mensaje["From"] = self.remitente
        mensaje["To"] = destinatario
        mensaje.set_content(cuerpo)

        with smtplib.SMTP(self.host, self.puerto, timeout=10) as servidor:
            servidor.starttls()
            servidor.login(self.usuario, self.password)
            servidor.send_message(mensaje)
        return True
