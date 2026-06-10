from celery import shared_task
from app.core.celery_app import celery_app
from app.core.docker_sandbox import get_sandbox


@celery_app.task(bind=True, time_limit=43200)
def start_compute_session(self, session_id: int, notebook_content: dict = None, hardware: str = "CPU", dataset_mounts: list = None):
    try:
        self.update_state(state="PROGRESS", meta={"status": "creating container"})
        result = get_sandbox().start_notebook_session(
            session_id=str(session_id),
            notebook_content=notebook_content,
            hardware=hardware,
            dataset_mounts=dataset_mounts,
        )
        self.update_state(state="SUCCESS", meta={"status": "running", "container_id": result["container_id"]})
        return result
    except Exception as exc:
        self.update_state(state="FAILURE", meta={"status": "failed", "error": str(exc)})
        raise


@celery_app.task
def stop_compute_session(container_id: str):
    get_sandbox().stop_session(container_id)
    return {"status": "stopped", "container_id": container_id}


@celery_app.task(bind=True, time_limit=300)
def execute_code_in_sandbox(self, container_id: str, code: str):
    try:
        self.update_state(state="PROGRESS", meta={"status": "executing"})
        output = get_sandbox().exec_code(container_id, code)
        self.update_state(state="SUCCESS", meta={"status": "completed", "output": output})
        return {"container_id": container_id, "output": output}
    except Exception as exc:
        self.update_state(state="FAILURE", meta={"status": "failed", "error": str(exc)})
        raise
