import sys

import checkpoint_sweep_test


SELECTED_PREFIX = "sac_v16_0_7_forward_speed_y100"
SELECTED_STEP = 675000
VIDEO_OFFSET = 5
VIDEO_SPAWN_THETA_DEG = 0


def main():
    sys.argv = [
        "test_selected_checkpoint.py",
        "--prefix",
        SELECTED_PREFIX,
        "--steps",
        str(SELECTED_STEP),
        f"--offsets={VIDEO_OFFSET}",
        "--spawn-theta-deg",
        str(VIDEO_SPAWN_THETA_DEG),
        "--no-stop-on-valid",
        "--checkpoint-pause",
        "0",
        "--pre-test-pause",
        "8",
        "--episode-pause",
        "6",
        "--output",
        "logs/selected_checkpoint_test.csv",
    ]
    return checkpoint_sweep_test.main()


if __name__ == "__main__":
    raise SystemExit(main())
