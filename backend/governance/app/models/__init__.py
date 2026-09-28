"""
app/models/__init__.py

Import all models so Alembic autogenerate can discover them.
"""
from app.models.user import User  # noqa: F401
from app.models.review import Review, ReviewHistory  # noqa: F401
from app.models.national_material import NationalMaterial, NationalMaterialHistory  # noqa: F401
from app.models.cpse_material_mapping import CPSEMaterialMapping  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
