import argparse
from .core.logger import get_logger
from .scheduler import Scheduler
from .core.config import load_env_config, load_yaml
log = get_logger(__name__)
def main(argv=None):
    parser = argparse.ArgumentParser(prog="bot", description="Airdrop Farming Bot CLI")
    sub = parser.add_subparsers(dest="cmd")
    run = sub.add_parser("run", help="Run playbook")
    run.add_argument("--plan", required=True, help="Path to playbook YAML")
    run.add_argument("--dry-run", action="store_true", help="Do not broadcast txs")
    run.add_argument("--report", default="run_report.csv", help="CSV report path")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        env = load_env_config(); plan = load_yaml(args.plan)
        Scheduler(env=env, plan=plan, dry_run=args.dry_run, report_path=args.report).execute()
        log.info("Done. Report: %s", args.report)
    else:
        parser.print_help()
if __name__ == "__main__":
    main()
