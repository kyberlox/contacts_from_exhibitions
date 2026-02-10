from .exhibitions import router as exhibitions_router
from .contacts import router as contacts_router
from .files import router as files_router
from .users import router as users_router

__all__ = ["exhibitions_router", "contacts_router", "files_router", "users_router"]
__version__ = "0.1.0"