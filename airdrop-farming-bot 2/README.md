Airdrop Farming Bot

Playbook-driven bot for testnets, featuring dry-run mode, pluggable tasks (swap, NFT batch minting, approve+stake), and anti-Sybil strategies (mild, balanced, strong).

## ⚡ Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
# Option A: run.py (no PYTHONPATH setup needed)
python run.py run --plan playbooks/sepolia_swap_eth_to_usdc.yaml --dry-run
# Option B: Advanced (editable install)
pip install -e .
python -m bot.cli run --plan playbooks/sepolia_swap_eth_to_usdc.yaml --dry-run
```

## Directory Structure
```
src/
  bot/
    core/         # Wallet, RPC, config, logger, task base classes
    tasks/        # Pluggable tasks: swap_uniswap_v2, mint_erc721, stake_erc20
    utils/        # tx_helper (retry), strategy (anti-Sybil)
    scheduler.py
    cli.py
playbooks/
  sepolia_swap_eth_to_usdc.yaml
  nft_batch_mint_common.yaml
  nft_batch_mint_with_abi.yaml
  stake_erc20_sample.yaml
data/
  uniswap_v2_router_abi.min.json
  erc20_min_abi.json
docs/
  Strategy.md
  Video_Script.md
  LinkedIn_Project.md
  Resume_Bullets_CN_EN.md
```

## 🧪 One-Click Example (Sepolia: ETH → USDC)
```bash
python run.py run --plan playbooks/sepolia_swap_eth_to_usdc.yaml --dry-run
python run.py run --plan playbooks/sepolia_swap_eth_to_usdc.yaml
```

## 🧰 NFT Batch Minting / Staking
```bash
# NFT: Common mode (no ABI required)
python run.py run --plan playbooks/nft_batch_mint_common.yaml --dry-run
# NFT: ABI mode (more robust)
python run.py run --plan playbooks/nft_batch_mint_with_abi.yaml --dry-run
# Staking: approve + stake
python run.py run --plan playbooks/stake_erc20_sample.yaml --dry-run
```

## 🛡️ Anti-Sybil Strategy Presets
Set `strategy: mild|balanced|strong` at the top of your playbook. See `docs/Strategy.md` for details. Configuring `jitter:` will override the preset interval ranges.

---

# 📸 Project Screenshots (Template)
- Dry-run terminal output, real transaction hashes, `run_report.csv` snippets, Mermaid architecture diagram, risk control checklist. See the corresponding sections in the repository README.

---

## 🧭 Push to GitHub
```bash
git init
git add .
git commit -m "feat: initial public release"
git branch -M main
git remote add origin https://github.com/<yourname>/airdrop-farming-bot.git
git push -u origin main
```

## ⚠️ Disclaimer
- For **technical learning and testnets** only; comply with laws and protocol ToS.
- Do not commit private keys/mnemonics to the repository; `.env` is ignored by default in `.gitignore`.
