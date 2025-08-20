# Anti‑Sybil Strategy Presets

Use in playbooks: `strategy: {mild|balanced|strong}`

| Preset   | Jitter (s) | Priority Tip (gwei) | Base Gas Multiplier | When to use                    |
|----------|------------|---------------------|---------------------|--------------------------------|
| mild     | 2–6        | 0.5–1.2             | 1.1–1.5             | Fast testing, low disguise     |
| balanced | 6–16       | 1.0–2.5             | 1.2–1.8             | Default, daily farming         |
| strong   | 12–32      | 1.5–4.0             | 1.4–2.2             | High disguise; slower & costlier |

- **Jitter**: random delay between tasks per wallet.
- **Gas**: per‑tx EIP‑1559 maxFee/priority chosen from the preset.
- Explicit `jitter:` block in playbook overrides preset.
