import multiprocessing
import sys


def main() -> None:
    multiprocessing.freeze_support()
    if sys.platform != "darwin":
        raise SystemExit("VALSHOP Companion requires macOS. Run scripts/run_mac.sh on your Mac.")
    from desktop import run_desktop

    raise SystemExit(run_desktop())


if __name__ == "__main__":
    main()
