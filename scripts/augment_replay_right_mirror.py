from datetime import datetime
import os
import shutil

import settings
from sac_agent import ReplayBuffer, SACAgent


SUCCESS_TERMINAL_REWARD_THRESHOLD = 50.0


def chronological_indices(replay):
    if replay.size < replay.capacity:
        return list(range(replay.size))
    return list(range(replay.ptr, replay.capacity)) + list(range(0, replay.ptr))


def collect_success_episode_indices(replay):
    episodes = []
    current = []

    for index in chronological_indices(replay):
        current.append(index)
        done = float(replay.dones[index, 0]) > 0.5
        reward = float(replay.rewards[index, 0])

        if done:
            if reward >= SUCCESS_TERMINAL_REWARD_THRESHOLD:
                episodes.append(list(current))
            current = []

    return episodes


def main():
    settings.setup_gpu()
    settings.ensure_model_dir()

    agent = SACAgent()
    replay = ReplayBuffer(agent.state_size, agent.action_size, settings.SAC_REPLAY_SIZE)
    replay_path = agent.replay_buffer_path()
    replay_step = replay.load(replay_path)

    if replay_step is None:
        raise FileNotFoundError(f"Replay buffer bulunamadi: {replay_path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{replay_path}.pre_mirror_{timestamp}.bak"
    shutil.copy2(replay_path, backup_path)

    success_episodes = collect_success_episode_indices(replay)
    transition_count = sum(len(indices) for indices in success_episodes)

    if transition_count == 0:
        print(
            "[MIRROR] Success episode bulunamadi; replay buffer degistirilmedi.",
            flush=True,
        )
        print(f"[MIRROR] Backup: {backup_path}", flush=True)
        return

    snapshots = []
    for episode in success_episodes:
        for index in episode:
            snapshots.append((
                replay.states[index].copy(),
                replay.actions[index].copy(),
                float(replay.rewards[index, 0]),
                replay.next_states[index].copy(),
                bool(float(replay.dones[index, 0]) > 0.5),
            ))

    for state, action, reward, next_state, done in snapshots:
        replay.add_right_mirror(state, action, reward, next_state, done)

    replay.save(replay_path, replay_step)
    print(
        "[MIRROR] Success episode'lari sag-sol aynalandi: "
        f"episodes={len(success_episodes)} transitions={transition_count} "
        f"step={replay_step} size={replay.size} ptr={replay.ptr}",
        flush=True,
    )
    print(f"[MIRROR] Backup: {backup_path}", flush=True)


if __name__ == "__main__":
    main()
