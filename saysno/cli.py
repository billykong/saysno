"""Interactive REPL: saysno [--model haiku|opus] [--dir PATH] [--off FEATURE ...] [--bare] [task]"""

import argparse
from datetime import datetime
from pathlib import Path

from .loop import FEATURES, MODELS, Agent, make_client


def main():
    parser = argparse.ArgumentParser(prog="saysno")
    parser.add_argument("--model", choices=MODELS, default="haiku")
    parser.add_argument("--dir", default=".", help="project directory the agent works in")
    parser.add_argument("--off", action="append", default=[], choices=FEATURES, help="switch a feature off")
    parser.add_argument("--bare", action="store_true", help="every feature off: the M1 loop")
    parser.add_argument("task", nargs="?")
    args = parser.parse_args()

    Path("transcripts").mkdir(exist_ok=True)
    transcript = f"transcripts/{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    features = set() if args.bare else set(FEATURES) - set(args.off)
    agent = Agent(make_client(args.model), args.dir, args.model, transcript=transcript, features=features)
    print(f"saysno: {MODELS[args.model]['model']} in {agent.tools.root}; transcript {transcript}")
    task = args.task
    try:
        while task or (task := input("> ").strip()):
            reply = agent.send(task)
            if reply.stop_reason != "end_turn":
                print(f"(stopped: {reply.stop_reason})")
            task = None
    except (EOFError, KeyboardInterrupt):
        print()


if __name__ == "__main__":
    main()
