class BaseAppException(Exception):
    """Clase base para errores controlados de la aplicación"""
    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ResourceNotFound(BaseAppException):
    def __init__(self, resource: str):
        super().__init__(f"{resource} no encontrado", status_code=404)

class AIModelError(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(f"Error en el modelo de IA: {detail}", status_code=503)