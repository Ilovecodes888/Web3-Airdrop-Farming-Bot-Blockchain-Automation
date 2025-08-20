import json, os, time
from web3 import Web3
from ..core.task import BaseTask, TaskContext
from ..core.logger import get_logger
from ..utils.tx_helper import fill_defaults, sign_and_send_with_retry
from ..utils.strategy import get_profile, choose_gas
log = get_logger(__name__)
class StakeERC20(BaseTask):
    kind = "stake_erc20"
    def run(self, ctx: TaskContext):
        w3 = ctx.w3; acct = ctx.wallet.account; chain_id = ctx.network.get("chain_id")
        staking_contract = self.cfg.get("staking_contract")
        token_address = self.cfg.get("token_address")
        amount_wei = int(self.cfg.get("amount_wei", "0"))
        rate_limit_sec = int(self.cfg.get("rate_limit_sec", "0"))
        wait_receipt = bool(self.cfg.get("wait_receipt", False))
        if not all([staking_contract, token_address]) or amount_wei <= 0:
            self._record(ctx, "error", {"reason": "missing token/staking/amount"}); return
        abi20_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "erc20_min_abi.json")
        with open(abi20_path, "r") as f: erc20_abi = json.load(f)
        abi_path = self.cfg.get("abi_path"); method = self.cfg.get("method_name", "stake")
        if abi_path and os.path.exists(abi_path):
            with open(abi_path, "r") as f: staking_abi = json.load(f)
        else:
            staking_abi = [{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"stake","outputs":[],"stateMutability":"nonpayable","type":"function"}]
        token = w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
        staking = w3.eth.contract(address=Web3.to_checksum_address(staking_contract), abi=staking_abi)
        # Strategy gas
        profile = get_profile(ctx.network.get("strategy", "balanced"))
        max_fee, prio = choose_gas(w3, profile)
        # 1) Allowance
        try:
            allowance = token.functions.allowance(acct.address, staking.address).call()
        except Exception:
            allowance = 0
        # 2) Approve
        if allowance < amount_wei:
            try:
                tx = token.functions.approve(staking.address, amount_wei).build_transaction({"from": acct.address})
                tx.setdefault("maxFeePerGas", max_fee); tx.setdefault("maxPriorityFeePerGas", prio)
                tx = fill_defaults(w3, tx, chain_id, acct.address)
                if ctx.dry_run:
                    self._record(ctx, "ok", {"action": "approve_dryrun", "spender": staking.address, "amount": amount_wei})
                else:
                    h = sign_and_send_with_retry(w3, acct, tx, wait_receipt=wait_receipt)
                    self._record(ctx, "ok", {"action": "approve", "tx_hash": h})
                    if rate_limit_sec > 0: time.sleep(rate_limit_sec)
            except Exception as e:
                self._record(ctx, "error", {"reason": f"approve_failed: {e}"}); return
        # 3) Stake
        try:
            func = getattr(staking.functions, method)
            tx = func(amount_wei).build_transaction({"from": acct.address})
            tx.setdefault("maxFeePerGas", max_fee); tx.setdefault("maxPriorityFeePerGas", prio)
            tx = fill_defaults(w3, tx, chain_id, acct.address)
            if ctx.dry_run:
                self._record(ctx, "ok", {"action": "stake_dryrun", "amount": amount_wei})
            else:
                h = sign_and_send_with_retry(w3, acct, tx, wait_receipt=wait_receipt)
                self._record(ctx, "ok", {"action": "stake", "tx_hash": h, "amount": amount_wei})
                if rate_limit_sec > 0: time.sleep(rate_limit_sec)
        except Exception as e:
            self._record(ctx, "error", {"reason": f"stake_failed: {e}"})
