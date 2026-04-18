# v9.0.0 Failed Snapshot - Clock Guidance Continuous Channels

V9.0.0 was stopped after the first clock-guidance training probe and archived as a failed architecture checkpoint.

## Run Window

- Phase: `v9_0_0_phase_1_clock_guidance_140_160`.
- Update range: `1-100`.
- Episodes: `310`.
- Checkpoint: `models/ppo_v9_model_up100.keras`.
- State: `models/ppo_v9_state_up100.pkl.gz`.
- Curriculum: `140-160m` radius, heading offset `-5..-1` or `+1..+5`, success distance `10m`.

## Outcome

- Success: `0/310` (`0.0%`).
- Near miss: `70/310` (`22.58%`).
- High altitude: `240/310` (`77.42%`).
- Last 50 episodes: `12 near_miss`, `38 high_altitude`.
- Mean final distance: `92.90m`.
- Mean final theta: `137.12deg`.
- Mean final alignment: `-0.696`.
- Mean final AGL: `124.85m`.
- Mean final closing speed: `-29.34m/s`.

## Failure Diagnosis

- The rocket started reaching the target corridor more often after the heading offset was narrowed, but it did not learn to point the nose at the target.
- Near-miss episodes were mostly bad-angle passes: the rocket got within the `16m` near-miss terminal distance while theta was still around `90-120deg`.
- Clock action selection stayed close to random: dominant target/action clock-channel match remained near the four-way random baseline (`~25%`).
- Continuous four-channel clock actions allowed opposite channels to coactivate, so net maneuver direction was often diluted.
- `near_miss` behaved like a trap terminal: it ended bad-angle close passes early instead of forcing the policy to continue and learn recovery or angle closure.

## Decision

- V9.0.0 is closed as unsuccessful.
- V10.0.0 will change the action type, so it is a checkpoint-incompatible architecture version.
- V10 direction: remove `near_miss` as a terminal, keep it as diagnostic only, and replace continuous four-channel steering with hybrid action: continuous thrust plus discrete clock-direction steering.

## Artifacts

- `logs/episode_log.csv`: episode log filtered to update `<=100`.
- `logs/update_log.csv`: update log filtered to update `<=100`.
- `logs/step_log.csv.zip.part001-004`: split compressed step trace.
- `logs/*_success_rate.png`, `logs/*_success_rug.png`, `logs/*_reset_radius_*.png`, `logs/*_clock_action_alignment.png`: static analysis graphs.
- `logs/*_plotly_*.html`: interactive analysis dashboard and plots.
