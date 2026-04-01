# v7.1 surum ailesi

> ## v7.1.0 - Phase 1.1 Archive Snapshot
>
> - **Phase 1.1 Freeze Point**: Faz 1.1 egitimi `up340` modelinde donduruldu ve Phase 1.2 warm-start noktasi olarak secildi.
> - **Artifact Archiving**: `archives/phase_1_1/` altina `ppo_model_up340`, agent state, `episode_log.csv`, `update_log.csv`, success rate grafigi ve buyuk `step_log.csv` dosyasinin sikistirilmis/parcalanmis arsivi eklendi.
> - **Documentation Update**: README ve changelog, Phase 1.1 sonuc ozeti ve sonraki Phase 1.2 gecis niyeti ile guncellendi.
> - **Observed Outcome**: Phase 1.1 kosusunda `1640` episode icinde `161` success (%9.817) goruldu; baskin failure modu `high_altitude` olarak kaldigi icin bir sonraki adim reward ince ayari olarak planlandi.

# v7.0 surum ailesi

> ## v7.0.0 - Full Telemetry Step Logging
>
> - **Unified Step Trace**: Unity tarafindan gelen ham geometri ve fizik telemetry verileri ile Python tarafinda uretilen action, value, logp, reward breakdown ve cumulative return bilgileri tek `step_log.csv` satirinda birlestirildi.
> - **Packet Contract Expansion**: Unity -> Python JSON sozlesmesine `telemetry` bolumu eklendi. Roket, hedef ve roket-hedef ciftine ait world/local konum, rotasyon, hiz, acisal hiz, relative vector ve gravity alanlari artik state disi debug verisi olarak tasiniyor.
> - **Reward Auditability**: Step log artik `reward_step_penalty`, `reward_distance`, `reward_alignment`, `reward_closing`, `reward_angular_penalty`, `reward_altitude`, `reward_soft_floor_penalty` ve `reward_terminal` kolonlarini ayri ayri sakliyor.
> - **Training Introspection**: Python tarafinda `action_norm_*`, `action_logp`, `value_pred`, `episode_return_so_far`, `phase_id`, `phase_name` ve `max_step` alanlari da step bazinda kaydediliyor.
> - **Schema-Safe Logging**: `log.py`, yeni baslik ile mevcut CSV basligi farkliysa eski loglari `.bak_YYYYMMDD_HHMMSS.csv` olarak arsivleyip temiz V7 dosyalari aciyor.
> - **State/Telemetry Separation**: RL observation 14 boyutlu sade guidance state olarak korundu; genis debug verisi ise ayri telemetry kanalina tasinarak analiz kolaylastirildi.

# v6.0 surum ailesi

> ## v6.0.0 - Guidance-First State Overhaul ve Repo Temizligi
>
> - **Observation Contract Break**: RL state yapisi 20 boyuttan 18 boyutlu guidance-first observation setine gecirildi.
> - **Unity -> Python Senkron Revizyonu**: JSON paket sozlesmesi yeni state alanlarina gore tekrar tasarlandi.
> - **Reward Refactor**: Reward mantigi mesafe ilerlemesi, LOS alignment, pozitif kapanma hizi, acisal hiz cezasi ve irtifa hizalama sinyalleri ile yeniden kuruldu.
> - **Loglama / Analiz Guncellemesi**: `log.py`, `test.py`, `reward_test.py` ve `docs/analiz.py` yeni V6 alanlari uzerinden calisacak sekilde guncellendi.
> - **Repo Temizligi**: Pre-V6 log ve model artefaktlari once arsivlendi, ardindan repo kokundeki runtime ciktilari gitten cikarildi.

Not: Daha eski v1-v5 kayitlari eski belge surumlerinde korunmustur. Bu dosya V6 ve sonrasi aktif degisimleri sade bir formatta tasir.
