# Backend patterns — service registry, repositories, database models

Read this when adding a configuration class, a service, a repository, or a database
entity to a feature package. For the full `appkit_commons` API (YAML profiles,
secrets, scheduler, migrations), use the `appkit-commons` skill.

## Service registry and dependency injection

Use `service_registry()` (from `appkit_commons`) as the single IoC container.

### Configuration

```python
# configuration.py
from appkit_commons.registry import service_registry

class MyFeatureConfig(BaseConfig):
    api_url: str | None = None
    api_key: SecretStr | None = None
```

Register in `configure()` in `app/configuration.py` by adding to `AppConfig`:

```python
class AppConfig(ApplicationConfig):
    my_feature: MyFeatureConfig | None = None
```

### Services

```python
class MyService:
    def __init__(self) -> None:
        self._config = service_registry().get(MyFeatureConfig)
```

Register in `app/app.py` `_initialize_services()` in dependency order.

### Accessing in state

```python
def _do_work(self) -> None:
    config = service_registry().get(MyFeatureConfig)
    svc = service_registry().get(MyService)
```


## Repository pattern

`BaseRepository` (from `appkit_commons`) already provides full CRUD:
`create()`, `update()`, `save()`, `find_by_id()`, `find_all()`, `delete_by_id()`, `delete()`, `exists_by_id()`, `count()`

Only add custom methods for queries not covered by the base class (e.g., `find_by_email`, `find_all_paginated`):

```python
# backend/repository.py

from appkit_commons.repositories.base import BaseRepository
from appkit_commons.database.session import get_asyncdb_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class MyModelRepository(BaseRepository[MyModelEntity]):

    async def find_by_name(
        self, session: AsyncSession, name: str
    ) -> MyModelEntity | None:
        result = await session.execute(
            select(MyModelEntity).where(MyModelEntity.name == name)
        )
        return result.scalar_one_or_none()


my_model_repo = MyModelRepository(MyModelEntity)
```

Always use `get_asyncdb_session()` — not `rx.asession()` — as the session factory:

```python
# In state event handlers
async with get_asyncdb_session() as session:
    items = await my_model_repo.find_all(session)
    entity = await my_model_repo.find_by_id(session, item_id)
    await my_model_repo.create(session, new_entity)
    await my_model_repo.update(session, entity)
    await my_model_repo.delete_by_id(session, item_id)
```

Never use `rx.asession()` — it does not work in background processors or callbacks outside the Reflex request lifecycle.


## Database models

### SQLAlchemy Entity (DB table)

Inherit from both `Entity` and `Base` from `appkit_commons.database.entities`. `Entity` provides `id`, `created`, and `updated` automatically. Add `to_dict()` for conversion to Pydantic/display models:

```python
# backend/entities.py
from appkit_commons.database.entities import Base, Entity
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class MyEntity(Entity, Base):
    __tablename__ = "my_feature_items"

    name: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_active": self.is_active,
        }
```

### Pydantic display model (UI-layer DTO)

Use `rx.Base` for models stored in Reflex state — never store SQLAlchemy `table=True` models directly:

```python
# backend/models.py
import reflex as rx

class MyModel(rx.Base):
    """UI-only DTO — safe to store in state."""
    id: int
    name: str
    is_active: bool = True
```

Convert in state: `self.items = [MyModel(**e.to_dict()) for e in entities]`

**Important**: Never store SQLAlchemy entity objects (those with relationships) directly in Reflex state — lazy-loaded relationships will fail outside the session context.
