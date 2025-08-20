import random
from typing import Dict, Tuple
from web3 import Web3
PROFILES: Dict[str, Dict] = {
    "mild":     {"jitter": (2, 6),  "priority_gwei": (0.5, 1.2), "fee_mult": (1.1, 1.5)},
    "balanced": {"jitter": (6, 16), "priority_gwei": (1.0, 2.5), "fee_mult": (1.2, 1.8)},
    "strong":   {"jitter": (12, 32),"priority_gwei": (1.5, 4.0), "fee_mult": (1.4, 2.2)},
}
def get_profile(name: str) -> Dict:
    return PROFILES.get(name, PROFILES["balanced"])
def pick_jitter_range(profile: Dict) -> Tuple[int, int]:
    return profile["jitter"]
def choose_gas(w3: Web3, profile: Dict) -> tuple[int, int]:
    base = w3.eth.gas_price or w3.to_wei("1", "gwei")
    mult = random.uniform(*profile["fee_mult"])
    max_fee = int(base * mult)
    prio = w3.to_wei(random.uniform(*profile["priority_gwei"]), "gwei")
    if max_fee < prio:
        max_fee = prio + w3.to_wei("0.1", "gwei")
    return max_fee, prio
