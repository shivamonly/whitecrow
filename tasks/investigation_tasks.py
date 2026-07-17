import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks.celery_app import celery_app
from whitecrow.orchestrator import run_investigation_sync


@celery_app.task(bind=True, name="investigate")
def investigate_task(self, email=None, phone=None, username=None, photo_path=None):
    self.update_state(state="RUNNING")
    result = run_investigation_sync(
        email=email,
        phone=phone,
        username=username,
        photo_path=photo_path,
    )
    return result.model_dump(mode="json")
