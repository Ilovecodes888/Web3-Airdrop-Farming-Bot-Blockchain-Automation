from web3 import Web3
def get_w3(rpc_url: str) -> Web3:
    if not rpc_url:
        raise ValueError("RPC_URL not provided")
    return Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 60}))
