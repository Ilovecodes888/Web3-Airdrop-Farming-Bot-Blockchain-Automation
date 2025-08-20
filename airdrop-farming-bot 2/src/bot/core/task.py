from dataclasses import dataclass
from typing import Dict, Any, List
from .logger import get_logger
log = get_logger(__name__)
@dataclass
class TaskContext:
    w3: any
    wallet: any
    network: Dict[str, Any]
    dry_run: bool
    report: List[Dict[str, Any]]
class BaseTask:
    kind: str = "base"
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
    def run(self, ctx: TaskContext):
        raise NotImplementedError
    def _record(self, ctx: TaskContext, status: str, detail: Dict[str, Any]):
        entry = {"kind": self.kind, "wallet": ctx.wallet.address, "status": status, **detail}
        ctx.report.append(entry)
        log.info("[%s] %s - %s", self.kind, status, detail)
