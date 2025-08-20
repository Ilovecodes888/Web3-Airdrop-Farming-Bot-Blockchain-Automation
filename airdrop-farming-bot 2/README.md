# Airdrop Farming Bot (Resume Edition)

Playbook 驱动 / Testnet 优先 / 默认 Dry‑run / 可插拔任务（swap、NFT 批量铸造、approve+stake）/ 反女巫策略（mild|balanced|strong）

## ⚡ 快速开始（新手友好）
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
# 方式A：run.py（无需设置 PYTHONPATH）
python run.py run --plan playbooks/sepolia_swap_eth_to_usdc.yaml --dry-run
# 方式B：专业用法（可编辑安装）
pip install -e .
python -m bot.cli run --plan playbooks/sepolia_swap_eth_to_usdc.yaml --dry-run
```

## 目录
```
src/
  bot/
    core/         # wallet, rpc, config, logger, task 基类
    tasks/        # 可插拔任务：swap_uniswap_v2, mint_erc721, stake_erc20
    utils/        # tx_helper(重试), strategy(反女巫策略)
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

## 🧪 一键示例（Sepolia：ETH → USDC）
```bash
python run.py run --plan playbooks/sepolia_swap_eth_to_usdc.yaml --dry-run
python run.py run --plan playbooks/sepolia_swap_eth_to_usdc.yaml
```

## 🧰 NFT 批量铸造 / Staking
```bash
# NFT：通用模式（无需 ABI）
python run.py run --plan playbooks/nft_batch_mint_common.yaml --dry-run
# NFT：ABI 模式（更稳）
python run.py run --plan playbooks/nft_batch_mint_with_abi.yaml --dry-run
# Staking：approve + stake
python run.py run --plan playbooks/stake_erc20_sample.yaml --dry-run
```

## 🛡️ 反女巫策略预设
在 playbook 顶部设置：`strategy: mild|balanced|strong`  
详见 `docs/Strategy.md`。若同时配置 `jitter:`，将覆盖预设的间隔范围。

---

# 📸 项目截图区（模板）
- 终端 dry‑run 截图、真实交易哈希、`run_report.csv` 片段、Mermaid 架构图、风控要点清单。详见仓库 README 中对应段落。

---

## 🧭 推送到 GitHub
```bash
git init
git add .
git commit -m "feat: initial public release"
git branch -M main
git remote add origin https://github.com/<yourname>/airdrop-farming-bot.git
git push -u origin main
```

## ⚠️ 安全声明
- 仅用于**技术学习与测试网**；遵守法律与协议 ToS。
- 不要把私钥/助记词提交到仓库；`.gitignore` 已默认忽略 `.env`。
