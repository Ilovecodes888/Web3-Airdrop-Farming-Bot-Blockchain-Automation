import csv, random, time
from typing import Dict, Any, List
from .core.logger import get_logger
from .core.rpc import get_w3
from .core.wallet import Wallet
from .core.task import TaskContext
from .tasks.swap_uniswap_v2 import SwapUniswapV2
from .tasks.mint_erc721 import MintERC721
from .tasks.stake_erc20 import StakeERC20
from .utils.strategy import get_profile, pick_jitter_range
log = get_logger(__name__)
_TASKS = {
    "swap_uniswap_v2": SwapUniswapV2,
    "mint_erc721": MintERC721,
    "stake_erc20": StakeERC20,
}
class Scheduler:
    def __init__(self, env: Dict[str, Any], plan: Dict[str, Any], dry_run: bool, report_path: str):
        self.env = env; self.plan = plan; self.dry_run = dry_run; self.report_path = report_path
        self.report_rows: List[Dict[str, Any]] = []
    def execute(self):
        net = self.plan.get("network", {})
        rpc_url = net.get("rpc_url") or self.env.get("RPC_URL")
        chain_id = net.get("chain_id") or self.env.get("CHAIN_ID")
        w3 = get_w3(rpc_url)
        wallets = self.plan.get("wallets") or [self.env.get("PRIVATE_KEY")]
        wallets = [w for w in wallets if w and w != "${PRIVATE_KEY}"]
        random.shuffle(wallets)
        strategy_name = self.plan.get("strategy", "balanced")
        profile = get_profile(strategy_name)
        net["strategy"] = strategy_name
        net["chain_id"] = chain_id
        if "jitter" in self.plan:
            jitter_cfg = self.plan.get("jitter") or {"min_seconds": 0, "max_seconds": 0}
            jitter = (jitter_cfg.get("min_seconds", 0), jitter_cfg.get("max_seconds", 0))
        else:
            jitter = pick_jitter_range(profile)
        log.info("Strategy=%s, jitter=%s", strategy_name, jitter)
        tasks = self.plan.get("tasks", [])
        for pk in wallets:
            wallet = Wallet(pk)
            log.info("Using wallet: %s", wallet.address)
            for task_cfg in tasks:
                ctx = TaskContext(w3=w3, wallet=wallet, network={"chain_id": chain_id, "strategy": strategy_name, "jitter": {"min_seconds": jitter[0], "max_seconds": jitter[1]}}, dry_run=self.dry_run, report=self.report_rows)
                kind = task_cfg.get("kind")
                TaskCls = _TASKS.get(kind)
                if not TaskCls:
                    log.warning("Unknown task kind: %s", kind); continue
                TaskCls(task_cfg).run(ctx)
                if jitter[1] > 0:
                    delay = random.uniform(*jitter)
                    time.sleep(delay)
        self._write_report()
    def _write_report(self):
        if not self.report_rows:
            log.info("No report rows to write."); return
        keys = sorted(set().union(*[r.keys() for r in self.report_rows]))
        with open(self.report_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(self.report_rows)
        log.info("Report saved to %s", self.report_path)
