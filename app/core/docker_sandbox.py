from typing import Optional, List
from app.core.config import settings


class DockerSandbox:
    def __init__(self):
        import docker
        self._docker = docker
        self.client = docker.from_env()
        self.image = settings.DATA_SCIENCE_IMAGE

    def _ensure_isolated_network(self) -> str:
        network_name = "kaggle-sandbox-net"
        try:
            self.client.networks.get(network_name)
        except self._docker.errors.NotFound:
            self.client.networks.create(
                network_name,
                driver="bridge",
                internal=True,
                options={"com.docker.network.bridge.enable_icc": "false"},
            )
        return network_name

    def start_notebook_session(
        self,
        session_id: str,
        notebook_content: Optional[dict] = None,
        hardware: str = "CPU",
        dataset_mounts: Optional[List[dict]] = None,
    ) -> dict:
        mem_limit = "4g" if hardware == "CPU" else "8g"
        nano_cpus = 2_000_000_000  # 2 CPU cores
        device_requests = []
        if hardware == "GPU":
            device_requests = [self._docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])]

        network = self._ensure_isolated_network()

        volumes = {}
        if dataset_mounts:
            for mount in dataset_mounts:
                volumes[mount["host_path"]] = {
                    "bind": mount["container_path"],
                    "mode": "ro",
                }

        container = self.client.containers.run(
            image=self.image,
            detach=True,
            name=f"notebook-{session_id}",
            mem_limit=mem_limit,
            nano_cpus=nano_cpus,
            device_requests=device_requests,
            user="1000:1000",
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],
            read_only=True,
            tmpfs={"/tmp": "noexec,nosuid,size=100m"},
            network=network,
            environment={"JUPYTER_ENABLE_LAB": "yes"},
            ports={"8888/tcp": None},
            labels={"type": "compute-session", "session_id": str(session_id)},
            auto_remove=True,
            volumes=volumes,
            command=["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''"],
        )
        return {
            "container_id": container.id,
            "status": container.status,
            "name": container.name,
        }

    def exec_code(self, container_id: str, code: str) -> str:
        container = self.client.containers.get(container_id)
        result = container.exec_run(
            cmd=["python", "-c", code],
            user="1000:1000",
            demux=True,
        )
        stdout = result.output[0].decode("utf-8") if result.output and result.output[0] else ""
        stderr = result.output[1].decode("utf-8") if result.output and result.output[1] else ""
        return stdout + stderr

    def stop_session(self, container_id: str) -> None:
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
        except self._docker.errors.NotFound:
            pass

    def get_session_logs(self, container_id: str, tail: int = 100) -> str:
        try:
            container = self.client.containers.get(container_id)
            return container.logs(tail=tail).decode("utf-8")
        except self._docker.errors.NotFound:
            return "Container not found"

    def list_active_sessions(self) -> list:
        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "labels": c.labels,
            }
            for c in self.client.containers.list()
            if c.labels.get("type") == "compute-session"
        ]


_sandbox_instance = None

def get_sandbox() -> DockerSandbox:
    global _sandbox_instance
    if _sandbox_instance is None:
        _sandbox_instance = DockerSandbox()
    return _sandbox_instance
