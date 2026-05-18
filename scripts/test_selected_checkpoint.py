import sys

import checkpoint_sweep_test


SELECTED_PREFIX = "sac_v16_0_7_forward_speed_y100"
SELECTED_STEP = 675000


def main():
    sys.argv = [
        "test_selected_checkpoint.py",
        "--prefix",
        SELECTED_PREFIX,
        "--steps",
        str(SELECTED_STEP),
        "--offsets=-5,-3,3,5",
        "--no-stop-on-valid",
        "--checkpoint-pause",
        "0",
        "--episode-pause",
        "6",
        "--output",
        "logs/selected_checkpoint_test.csv",
    ]
    return checkpoint_sweep_test.main()


if __name__ == "__main__":
    raise SystemExit(main())
