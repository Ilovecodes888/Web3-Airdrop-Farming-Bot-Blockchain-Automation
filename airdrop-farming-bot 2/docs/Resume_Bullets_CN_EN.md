**EN**
- Built a playbook‑driven EVM automation bot (swap / NFT mint / approve+stake), with dry‑run safety, anti‑sybil randomization, multi‑wallet orchestration, and CSV audit.
- Implemented retry + rate limiting for on‑chain broadcasts; testnet trials on Uniswap V2 (Sepolia).
- Plugin architecture: add a new protocol in ~100 LOC and one YAML playbook.

**CN**
- 设计实现 Playbook 驱动的 EVM 自动化机器人，覆盖 兑换/批量NFT/approve+stake，具备 Dry‑run、反女巫随机化、多钱包编排与 CSV 审计。
- 对交易发送实现 重试+限速，在测试网显著降低失败率（Uniswap V2 · Sepolia）。
- 插件化架构，新增协议约 100 行代码 + 一份 Playbook 即可接入。
