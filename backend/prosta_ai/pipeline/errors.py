"""Errores controlados del pipeline."""


class StageError(Exception):
    """Fallo controlado de una etapa del procesamiento.

    `stage` es el nombre de la etapa (ver `stages`) y `message` un texto
    comprensible para el usuario, sin detalles internos.
    """

    def __init__(self, stage: str, message: str):
        super().__init__(f"{stage}: {message}")
        self.stage = stage
        self.message = message
