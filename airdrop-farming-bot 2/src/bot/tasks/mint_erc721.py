import json, os, time
from typing import List
from eth_utils import keccak, to_checksum_address
from eth_abi import encode as abi_encode
from web3 import Web3
from ..core.task import BaseTask, TaskContext
from ..core.logger import get_logger
from ..utils.tx_helper import fill_defaults, sign_and_send_with_retry
from ..utils.strategy import get_profile, choose_gas
log = get_logger(__name__)
COMMON_SIGNATURES = [
    ("mint()", []),
    ("mint(address)", ["address"]),
    ("safeMint(address)", ["address"]),
    ("publicMint(uint256)", ["uint256"]),
    ("mint(uint256)", ["uint256"]),
    ("claim()", []),
]
def _encode_signature(sig: str):
    return keccak(text=sig)[:4]
def _encode_args(types: List[str], values: List):
    if not types: return b""
    return abi_encode(types, values)
class MintERC721(BaseTask):
    kind = "mint_erc721"
    def run(self, ctx: TaskContext):
        w3 = ctx.w3; acct = ctx.wallet.account; chain_id = ctx.network.get("chain_id")
        contract_address = self.cfg.get("contract_address")
        if not contract_address:
            self._record(ctx, "error", {"reason": "contract_address missing"}); return
        to_addr = self.cfg.get("to_address", acct.address)
        value_wei = int(self.cfg.get("value_wei", "0"))
        rate_limit_sec = int(self.cfg.get("rate_limit_sec", "0"))
        wait_receipt = bool(self.cfg.get("wait_receipt", False))
        mode = self.cfg.get("mode", "common")  # common | abi
        # Gas from strategy
        profile = get_profile(ctx.network.get("strategy", "balanced"))
        max_fee, prio = choose_gas(w3, profile)
        if mode == "abi":
            abi_path = self.cfg.get("abi_path"); method = self.cfg.get("method_name", "mint"); args = self.cfg.get("args", [])
            if not abi_path or not os.path.exists(abi_path):
                self._record(ctx, "error", {"reason": "abi_path missing/not found"}); return
            with open(abi_path, "r") as f: abi = json.load(f)
            contract = w3.eth.contract(address=to_checksum_address(contract_address), abi=abi)
            try:
                func = getattr(contract.functions, method)(*args)
                tx = func.build_transaction({"from": acct.address, "value": value_wei})
                tx.setdefault("maxFeePerGas", max_fee); tx.setdefault("maxPriorityFeePerGas", prio)
                tx = fill_defaults(w3, tx, chain_id, acct.address)
                if ctx.dry_run:
                    self._record(ctx, "ok", {"action": "mint_erc721_dryrun(abi)", "to": contract_address})
                else:
                    h = sign_and_send_with_retry(w3, acct, tx, wait_receipt=wait_receipt)
                    self._record(ctx, "ok", {"action": "mint_erc721(abi)", "tx_hash": h})
            except Exception as e:
                self._record(ctx, "error", {"reason": f"abi_mode_failed: {e}"})
            return
        # common mode
        sigs = self.cfg.get("common_signatures") or COMMON_SIGNATURES
        attempts = []
        for sig, types in sigs:
            try:
                data = _encode_signature(sig)
                values = []
                for t in types:
                    if t == "address": values.append(to_checksum_address(to_addr))
                    elif t == "uint256": values.append(1)
                    else: raise ValueError(f"Unsupported arg type: {t}")
                data += _encode_args(types, values)
                tx = {"to": to_checksum_address(contract_address), "data": data, "value": value_wei, "from": acct.address}
                tx.setdefault("maxFeePerGas", max_fee); tx.setdefault("maxPriorityFeePerGas", prio)
                tx = fill_defaults(w3, tx, chain_id, acct.address)
                if ctx.dry_run:
                    self._record(ctx, "ok", {"action": "mint_erc721_dryrun(common)", "sig": sig}); return
                h = sign_and_send_with_retry(w3, acct, tx, wait_receipt=wait_receipt)
                self._record(ctx, "ok", {"action": "mint_erc721(common)", "sig": sig, "tx_hash": h})
                if rate_limit_sec > 0: time.sleep(rate_limit_sec)
                return
            except Exception as e:
                attempts.append(f"{sig}:{e}")
                continue
        self._record(ctx, "error", {"reason": "all_common_signatures_failed", "attempts": attempts})
