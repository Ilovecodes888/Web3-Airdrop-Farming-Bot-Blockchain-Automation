from eth_account import Account
from dataclasses import dataclass
@dataclass
class Wallet:
    private_key: str
    @property
    def account(self):
        return Account.from_key(self.private_key)
    @property
    def address(self) -> str:
        return self.account.address
