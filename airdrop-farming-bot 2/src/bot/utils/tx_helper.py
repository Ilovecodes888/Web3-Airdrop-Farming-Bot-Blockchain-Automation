from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..core.logger import get_logger
log = get_logger(__name__)
class BroadcastError(Exception): pass
def fill_defaults(w3, tx, chain_id, from_addr):
    tx.setdefault("nonce", w3.eth.get_transaction_count(from_addr))
    tx.setdefault("chainId", chain_id)
    tx.setdefault("gas", tx.get("gas", 300000))
    tx.setdefault("maxFeePerGas", w3.to_wei("2", "gwei"))
    tx.setdefault("maxPriorityFeePerGas", w3.to_wei("1", "gwei"))
    return tx
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=6),
       retry=retry_if_exception_type(BroadcastError))
def sign_and_send_with_retry(w3, acct, tx, wait_receipt=False, timeout=60):
    signed = acct.sign_transaction(tx)
    try:
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction).hex()
        log.info("[SENT] %s", tx_hash)
    except Exception as e:
        log.warning("broadcast failed, will retry: %s", e)
        raise BroadcastError(str(e))
    if wait_receipt:
        try:
            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        except Exception as e:
            log.warning("wait_for_receipt failed (non-fatal): %s", e)
    return tx_hash
