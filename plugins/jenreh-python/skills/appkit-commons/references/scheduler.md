# Scheduler

Read this when adding a scheduled or recurring job.

Two backends: `APScheduler` (distributed-safe, default) and `PGQueuerScheduler`.

### Define a scheduled service

```python
from appkit_commons.scheduler import ScheduledService, CronTrigger, IntervalTrigger
from appkit_commons.database.session import get_asyncdb_session


class NightlyCleanupService(ScheduledService):
    job_id = "nightly_cleanup"
    name = "Nightly Cleanup"

    @property
    def trigger(self) -> CronTrigger:
        return CronTrigger(hour=2, minute=0)

    async def execute(self, *args, **kwargs) -> None:
        async with get_asyncdb_session() as session:
            await my_entity_repo.delete_old_items(session)
```

### Trigger types

```python
# Cron — standard cron fields, all optional (default *)
CronTrigger(hour=2, minute=30)  # daily at 02:30
CronTrigger(day_of_week="mon", hour=9)  # every Monday 09:00
CronTrigger(minute="*/15")  # every 15 minutes

# Fixed interval
IntervalTrigger(minutes=5)  # every 5 minutes
IntervalTrigger(hours=1, minutes=30)  # every 90 minutes

# Calendar interval (month/year-aware)
from appkit_commons.scheduler import CalendarIntervalTrigger

CalendarIntervalTrigger(months=1, day=1)  # 1st of each month
```

### Register and start

```python
from appkit_commons.scheduler import APScheduler

scheduler = APScheduler()
scheduler.add_service(NightlyCleanupService())
service_registry().register(scheduler)

# In app lifespan:
await scheduler.start()

# On shutdown:
await scheduler.shutdown()
```

`APScheduler` auto-configures from `DatabaseConfig`. In multi-node deployments it coordinates via the SQL datastore so each job runs on only one node. Uses `PsycopgEventBroker` for real-time scheduling when PostgreSQL is available.
