import time, json, os
from web3 import Web3
from ..core.task import BaseTask, TaskContext
from ..core.logger import get_logger
from ..utils.tx_helper import fill_defaults, sign_and_send_with_retry
from ..utils.strategy import get_profile, choose_gas
log = get_logger(__name__)
class SwapUniswapV2(BaseTask):
    kind = "swap_uniswap_v2"
    def run(self, ctx: TaskContext):
        router = self.cfg.get("router_address")
        token_in = self.cfg.get("token_in")
        token_out = self.cfg.get("token_out")
        amount_in_wei = int(self.cfg.get("amount_in_wei", "0"))
        amount_out_min = int(self.cfg.get("amount_out_min", "0"))
        deadline_sec = int(self.cfg.get("deadline_sec", "600"))
        if not all([router, token_in, token_out]) or amount_in_wei <= 0:
            self._record(ctx, "error", {"reason": "missing or invalid swap params"}); return
        abi_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uniswap_v2_router_abi.min.json")
        with open(abi_file, "r") as f: abi = json.load(f)
        w3 = ctx.w3; acct = ctx.wallet.account
        router_contract = w3.eth.contract(address=Web3.to_checksum_address(router), abi=abi)
        if token_in == "ETH":
            weth = self.cfg.get("weth_address")
            if not weth:
                self._record(ctx, "error", {"reason": "weth_address required when token_in == ETH"}); return
            path = [Web3.to_checksum_address(weth), Web3.to_checksum_address(token_out)]
        else:
            path = [Web3.to_checksum_address(token_in), Web3.to_checksum_address(token_out)]
        try:
            amounts = router_contract.functions.getAmountsOut(amount_in_wei, path).call()
            expected_out = int(amounts[-1])
        except Exception as e:
            log.warning("getAmountsOut failed: %s", e); expected_out = 0
        if amount_out_min == 0:
            amount_out_min = 0
        deadline = int(time.time()) + deadline_sec
        profile = get_profile(ctx.network.get("strategy", "balanced"))
        max_fee, prio = choose_gas(w3, profile)
        if token_in == "ETH":
            func = router_contract.functions.swapExactETHForTokens(amount_out_min, path, acct.address, deadline)
            tx = func.build_transaction({
                "from": acct.address,
                "value": amount_in_wei,
                "nonce": w3.eth.get_transaction_count(acct.address),
                "chainId": ctx.network.get("chain_id"),
                "maxFeePerGas": max_fee,
                "maxPriorityFeePerGas": prio,
                "gas": 500000
            })
        else:
            self._record(ctx, "error", {"reason": "token->token not implemented in sample"}); return
        if ctx.dry_run:
            signed = acct.sign_transaction(tx); tx_hash_preview = "0x" + signed.hash.hex()
            log.info("[DRY RUN] swap tx built: %s", tx_hash_preview)
            self._record(ctx, "ok", {"action": "swap_uniswap_v2_dryrun", "tx_hash": tx_hash_preview, "expected_out": expected_out})
            return
        try:
            h = sign_and_send_with_retry(w3, acct, tx, wait_receipt=self.cfg.get("wait_receipt", False))
            self._record(ctx, "ok", {"action": "swap_uniswap_v2", "tx_hash": h, "expected_out": expected_out})
        except Exception as e:
            self._record(ctx, "error", {"reason": f"broadcast_failed: {e}"})
