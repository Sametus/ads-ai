using System;
using UnityEngine;

// =============================================================================
// PYTHON STATE VEKTORI SOZLESMESI  (env.py - parse_state + normalize_state)
// =============================================================================
// Unity tarafinin gonderecegi alanlar ile Python'da kurulan V9 clock-guidance state:
//
//  Index  | Python state adi | JSON alani
//  -------|------------------|--------------------------------------
//   0     | distance             | states.distance
//   1     | theta_rad            | states.theta_rad
//   2     | alpha_rad            | states.alpha_rad
//   3     | beta_rad             | states.beta_rad
//   4-7   | target_clock_*       | states.target_clock[0..3] (12,6,3,9)
//   8     | closing_speed        | states.closing_speed
//   9-12  | rel_vel_clock_*      | states.rel_vel_clock[0..3] (12,6,3,9)
//   13    | rel_vel_forward      | states.rel_vel_forward
//   14-17 | turn_rate_clock_*    | states.turn_rate_clock[0..3] (12,6,3,9)
//   18    | turn_rate_roll       | states.turn_rate_roll
//   19    | clock_validity       | states.clock_validity
//   20    | forward_up_dot       | states.forward_up_dot
//   21    | agl                  | states.agl
//   22    | alt_error            | states.alt_error
//
// NOT: beta_rad, roket burnu gravity-up eksenine cok yaklastiginda
//      kararlilik icin fade edilir.
// NOT: grounded_flag state vektorune dahil DEGILDIR.
//      Reward ve terminal logic icin ham JSON icinde gonderilir.
// =============================================================================

[Serializable]
public class IncomingPacket
{
    public int episode_id;
    public int step_id;
    public string type;
    public float[] values;
}

[Serializable]
public class OutgoingStateData
{
    public float distance;
    public float theta_rad;
    public float alpha_rad;
    public float beta_rad;
    public float closing_speed;

    public float[] target_clock = new float[4];
    public float[] rel_vel_clock = new float[4];
    public float rel_vel_forward;
    public float[] turn_rate_clock = new float[4];
    public float turn_rate_roll;
    public float clock_validity;

    public float[] rel_vel_ref = new float[3];
    public float[] turn_rate_ref = new float[3];

    public float forward_up_dot;
    public float agl;
    public float alt_error;
    public float grounded_flag;
}

[Serializable]
public class OutgoingTelemetryData
{
    public float[] rocket_pos_world = new float[3];
    public float[] rocket_euler_world = new float[3];
    public float[] rocket_rot_world = new float[4];
    public float[] rocket_point_pos_world = new float[3];
    public float[] rocket_point_forward_world = new float[3];
    public float[] rocket_point_up_world = new float[3];
    public float[] rocket_point_right_world = new float[3];
    public float[] rocket_body_forward_world = new float[3];
    public float[] rocket_body_up_world = new float[3];
    public float[] rocket_body_right_world = new float[3];
    public float[] rocket_vel_world = new float[3];
    public float[] rocket_vel_local = new float[3];
    public float[] rocket_ang_vel_world = new float[3];
    public float[] rocket_ang_vel_local = new float[3];

    public float[] target_pos_world = new float[3];
    public float[] target_euler_world = new float[3];
    public float[] target_rot_world = new float[4];
    public float[] target_point_pos_world = new float[3];
    public float[] target_point_forward_world = new float[3];
    public float[] target_point_up_world = new float[3];
    public float[] target_vel_world = new float[3];
    public float[] target_vel_in_rocket_local = new float[3];
    public float[] target_ang_vel_world = new float[3];
    public float[] target_ang_vel_in_rocket_local = new float[3];

    public float[] rel_pos_world = new float[3];
    public float[] rel_pos_local = new float[3];
    public float[] rel_dir_world = new float[3];
    public float[] rel_dir_local = new float[3];
    public float[] rel_vel_world = new float[3];
    public float[] rel_vel_local = new float[3];
    public float[] gravity_world = new float[3];
    public float[] gravity_local = new float[3];
    public float[] guidance_up_world = new float[3];
    public float[] guidance_right_world = new float[3];
    public float[] guidance_forward_world = new float[3];
    public float[] guidance_up_local = new float[3];
    public float[] guidance_right_local = new float[3];
    public float[] guidance_forward_local = new float[3];
    public float[] clock_12_world = new float[3];
    public float[] clock_3_world = new float[3];
    public float[] clock_forward_world = new float[3];
    public float[] clock_12_local = new float[3];
    public float[] clock_3_local = new float[3];
    public float[] clock_forward_local = new float[3];
    public float[] rel_vel_guidance = new float[3];
    public float[] rel_vel_clock_signed = new float[3];
    public float[] rocket_ang_vel_guidance = new float[3];
    public float[] rocket_turn_clock_signed = new float[3];
    public float[] thrust_world = new float[3];
    public float[] desired_clock_turn_world = new float[3];
    public float[] command_turn_world = new float[3];
    public float[] command_turn_local = new float[3];
    public float[] torque_command_local = new float[3];
    public float[] torque_command_world = new float[3];
    public float[] applied_turn_world = new float[3];
    public float[] applied_turn_local = new float[3];

    public float target_speed;
    public float roll_error_deg;
    public float beta_validity;
    public float clock_validity;
    public float target_clock_angle_deg;
    public float action_clock_angle_deg;
    public float action_clock_mag;
    public float action_clock12_raw;
    public float action_clock3_raw;
    public float action_clock12_net;
    public float action_clock3_net;
    public float low_altitude_turn_scale;
    public float clock12_scale;
    public float clock3_scale;
    public float beta_validity_applied;
    public float roll_control_scale;
    public float roll_correction_cmd;
    public float roll_correction_limit;
    public float roll_torque_limit;
    public float suppressed_roll_rate;
    public float rocket_point_body_forward_dot;
    public float rocket_point_body_up_dot;
    public float rocket_point_body_right_dot;
}

[Serializable]
public class OutgoingPacket
{
    public int episode_id;
    public int step_id;
    public OutgoingStateData states;
    public OutgoingTelemetryData telemetry;
}

public class Env : MonoBehaviour
{
    [Header("Network")]
    public string ip = "127.0.0.1";
    public int port = 5005;

    [Header("Scene References (Surukle-Birak)")]
    public Transform rocket;
    public Transform rocketPoint;
    public Transform target;
    public Transform targetPoint;

    [Header("Rigidbodies (Surukle-Birak, bossa otomatik aranir)")]
    public Rigidbody rocketRb;
    public Rigidbody targetRb;

    [Header("Debug Lines (Opsiyonel)")]
    public LineRenderer distanceLine;
    public LineRenderer forwardLine;
    public float forwardLineLength = 20f;
    public bool drawActionAuditRays = true;
    public float actionAuditRayLength = 8f;
    [Range(0.05f, 1f)] public float actionAuditRayAlpha = 0.22f;
    public float actionAuditRayDuration = 0.01f;

    [Header("Rocket Reset Pose")]
    public Vector3 rocketResetPosition = new Vector3(-0.492f, 0.8375f, 0.022f);
    public Vector3 rocketResetEuler = new Vector3(-90f, 0f, 0f);

    [Header("Action Scales")]
    public float thrustScale = 1f;
    public float torqueScale = 1.8f;
    public float rollTorqueScale = 3.6f;
    public float lowAltitudeTurnDampStartAgl = 0.5f;
    public float lowAltitudeTurnDampFullAgl = 10f;
    public float lowAltitudeMinTurnScale = 0.35f;
    public float lowAltitudeUpTurnMinScale = 0.90f;
    public float clockTurnRateTarget = 2.8f;
    public float clockTurnRateControllerGain = 1.8f;
    public float maxPitchYawTorqueCommand = 6.0f;

    [Header("Direct Guidance Test (Sadece klasik baseline)")]
    public float directActionMarker = -7777f;
    public float guidanceAccelActionMarker = -5555f;
    public float bodyAccelActionMarker = -6666f;
    public float directAccelLimit = 90f;
    public float directMaxSpeed = 140f;
    public float directLookRateDeg = 720f;
    public bool directZeroAngularVelocity = true;
    public float directVelocityAlignBlend = 0.18f;
    public float directBackwardVelocityDamp = 0.55f;

    [Header("Guidance Stabilization")]
    public float targetHeightOffset = 0f;
    public float rollStabilizationGain = 25f;
    public float rollDampingGain = 20f;
    public float maxRollCorrection = 5.25f;
    public float activeSteeringRollScale = 0.35f;
    public float rollValidityFloor = 0.15f;
    public float maxRollTorqueCommand = 3.0f;
    public bool suppressRollRate = true;
    public float rollRateSuppressBlend = 1.0f;
    public float betaFadeStartAbsForwardUp = 0.80f;
    public float betaFadeEndAbsForwardUp = 0.95f;
    public float betaValidityFloor = 0.75f;

    [Header("State Options")]
    public bool useLocalFrame = true;

    [Header("Target Reset Constraints")]
    public bool keepTargetYFixed = true;
    public bool keepTargetRotXFixed = true;

    [Header("Target Motion")]
    public float targetSpeed = 25f;

    [Header("Ground / Collision")]
    public LayerMask groundMask = ~0;
    public float groundRayMax = 180f;
    public float groundedRayThreshold = 0.15f;
    public int lowAltitudeGraceSteps = 8;

    [Header("Particle FX (Opsiyonel)")]
    public ParticleSystem rocketExhaustFx;
    public ParticleSystem targetExhaustFx;
    public bool alignRocketExhaustToRocketPoint = true;
    public bool rocketExhaustWorldSimulation = true;
    public float rocketExhaustBackOffset = 0.42f;

    private Connector connector;

    private int currentEpisodeId = 0;
    private int currentStepId = 0;
    private int localStepCount = 0;

    private float currentThrust = 0f;
    private float currentClock12Cmd = 0f;
    private float currentClock6Cmd = 0f;
    private float currentClock3Cmd = 0f;
    private float currentClock9Cmd = 0f;
    private bool currentDirectGuidanceMode = false;
    private bool currentBodyAccelLearningMode = false;
    private bool currentGuidanceAccelLearningMode = false;
    private Vector3 currentDirectAccelWorld = Vector3.zero;
    private Vector3 currentDirectLookWorld = Vector3.forward;

    private float fixedTargetY;
    private float fixedTargetRotX;
    private Vector3 targetMoveDir = Vector3.zero;
    private Vector3 cachedGuidanceForward = Vector3.forward;
    private Vector3 lastAppliedTurnWorld = Vector3.zero;
    private Vector3 lastAppliedTurnLocal = Vector3.zero;
    private Vector3 lastThrustWorld = Vector3.zero;
    private Vector3 lastDesiredClockTurnWorld = Vector3.zero;
    private Vector3 lastCommandTurnWorld = Vector3.zero;
    private Vector3 lastCommandTurnLocal = Vector3.zero;
    private Vector3 lastTorqueCommandLocal = Vector3.zero;
    private Vector3 lastTorqueCommandWorld = Vector3.zero;
    private float lastClock12Raw = 0f;
    private float lastClock3Raw = 0f;
    private float lastClock12Net = 0f;
    private float lastClock3Net = 0f;
    private float lastLowAltitudeTurnScale = 1f;
    private float lastClock12Scale = 1f;
    private float lastClock3Scale = 1f;
    private float lastBetaValidityApplied = 1f;
    private float lastRollControlScale = 1f;
    private float lastRollCorrectionCmd = 0f;
    private float lastRollCorrectionLimit = 0f;
    private float lastRollTorqueLimit = 0f;
    private float lastSuppressedRollRate = 0f;

    private void Start()
    {
        ValidateAndBindReferences();

        fixedTargetY = target.position.y + targetHeightOffset;
        fixedTargetRotX = target.eulerAngles.x;
        ResetGuidanceCache();
        ConfigureParticleFX();

#if UNITY_6000_0_OR_NEWER
        Physics.simulationMode = SimulationMode.Script;
#else
        Physics.autoSimulation = false;
#endif

        connector = new Connector();
        connector.StartServer(ip, port);

        Debug.Log($"[Env] Basladi | fixedTargetY={fixedTargetY:F2} | fixedTargetRotX={fixedTargetRotX:F2} | manual physics step aktif");
    }

    private void Update()
    {
        if (connector == null || !connector.IsConnected || !connector.HasData)
            return;

        string jsonMsg = connector.ReadPacket();
        if (!string.IsNullOrEmpty(jsonMsg))
        {
            ProcessIncomingPacket(jsonMsg);
        }
    }

    private void FixedUpdate()
    {
        // Fizik yalnizca Python'dan action geldiginde StepOnce() icinde ilerletilir.
    }

    private void ValidateAndBindReferences()
    {
        if (rocket == null || rocketPoint == null || target == null || targetPoint == null)
        {
            Debug.LogError("[Env] Transform referanslari eksik.");
            enabled = false;
            return;
        }

        if (rocketRb == null)
            rocketRb = rocket.GetComponent<Rigidbody>();

        if (targetRb == null && target != null)
            targetRb = target.GetComponent<Rigidbody>();

        if (rocketRb == null)
        {
            Debug.LogError("[Env] Rocket Rigidbody bulunamadi.");
            enabled = false;
        }
    }

    private void ProcessIncomingPacket(string jsonMsg)
    {
        IncomingPacket packet = null;

        try
        {
            packet = JsonUtility.FromJson<IncomingPacket>(jsonMsg);
        }
        catch (Exception e)
        {
            Debug.LogError("[Env] JSON parse hatasi: " + e.Message);
            return;
        }

        if (packet == null)
        {
            Debug.LogError("[Env] Packet null parse edildi.");
            return;
        }

        currentEpisodeId = packet.episode_id;
        currentStepId = packet.step_id;

        if (packet.type == "reset")
        {
            if (packet.values == null || packet.values.Length < 5)
            {
                Debug.LogError("[Env] Reset paketi gecersiz.");
                return;
            }

            ResetEnvironment(packet.values);
            SendStateToPython();
            return;
        }

        if (packet.type == "action")
        {
            if (packet.values == null || packet.values.Length < 5)
            {
                Debug.LogError("[Env] Action paketi gecersiz.");
                return;
            }

            ReadAction(packet.values);
            StepOnce();
            return;
        }

        Debug.LogWarning("[Env] Bilinmeyen packet.type: " + packet.type);
    }

    private void ReadAction(float[] actionValues)
    {
        if (actionValues.Length >= 7 && Mathf.Abs(actionValues[0] - guidanceAccelActionMarker) <= 0.5f)
        {
            // Guidance-accel SAC: RL sadece ivme komutu secer.
            // Burun hedefe kilitlenmez; gorsel govde hiz/ivme yonune hizalanir, roll ogrenme disinda tutulur.
            currentDirectGuidanceMode = true;
            currentBodyAccelLearningMode = false;
            currentGuidanceAccelLearningMode = true;
            currentThrust = 0f;
            currentClock12Cmd = 0f;
            currentClock6Cmd = 0f;
            currentClock3Cmd = 0f;
            currentClock9Cmd = 0f;
            currentDirectAccelWorld = new Vector3(actionValues[1], actionValues[2], actionValues[3]);
            currentDirectLookWorld = new Vector3(actionValues[4], actionValues[5], actionValues[6]);
            return;
        }

        if (actionValues.Length >= 7 && Mathf.Abs(actionValues[0] - bodyAccelActionMarker) <= 0.5f)
        {
            // Body-accel SAC egitiminde Unity hedefe otomatik kilitlenmez.
            // Python sadece govde frame'inden hesaplanan ivmeyi yollar; kontrolu SAC ogrenir.
            currentDirectGuidanceMode = true;
            currentBodyAccelLearningMode = true;
            currentGuidanceAccelLearningMode = false;
            currentThrust = 0f;
            currentClock12Cmd = 0f;
            currentClock6Cmd = 0f;
            currentClock3Cmd = 0f;
            currentClock9Cmd = 0f;
            currentDirectAccelWorld = new Vector3(actionValues[1], actionValues[2], actionValues[3]);
            currentDirectLookWorld = new Vector3(actionValues[4], actionValues[5], actionValues[6]);
            return;
        }

        if (actionValues.Length >= 7 && actionValues[0] <= directActionMarker + 0.5f)
        {
            // Direct mode hem klasik baseline hem de V12 RL icin kullanilir.
            // Clock/torque zinciri yerine dunya uzayinda sinirli ivme uygulariz.
            currentDirectGuidanceMode = true;
            currentBodyAccelLearningMode = false;
            currentGuidanceAccelLearningMode = false;
            currentThrust = 0f;
            currentClock12Cmd = 0f;
            currentClock6Cmd = 0f;
            currentClock3Cmd = 0f;
            currentClock9Cmd = 0f;
            currentDirectAccelWorld = new Vector3(actionValues[1], actionValues[2], actionValues[3]);
            currentDirectLookWorld = new Vector3(actionValues[4], actionValues[5], actionValues[6]);
            return;
        }

        currentDirectGuidanceMode = false;
        currentBodyAccelLearningMode = false;
        currentGuidanceAccelLearningMode = false;
        currentDirectAccelWorld = Vector3.zero;
        currentDirectLookWorld = Vector3.forward;
        currentThrust = actionValues[0];
        currentClock12Cmd = Mathf.Max(0f, actionValues[1]);
        currentClock6Cmd = Mathf.Max(0f, actionValues[2]);
        currentClock3Cmd = Mathf.Max(0f, actionValues[3]);
        currentClock9Cmd = Mathf.Max(0f, actionValues[4]);
    }

    private void StepOnce()
    {
        localStepCount += 1;

        MoveTarget();
        ApplyAction();
        UpdateParticleFX();

        Physics.Simulate(Time.fixedDeltaTime);
        SuppressRollRate();
        UpdateDebugLines();
        SendStateToPython();
    }

    private void ApplyAction()
    {
        if (currentDirectGuidanceMode)
        {
            ApplyDirectGuidanceAction();
            return;
        }

        // Itkiyi rocketPoint.forward ile uygulariz; state/debug tarafinda roket burnu olarak bu eksen kullaniliyor.
        // Boylece "hedefe bakma" ile fiziksel itki ekseni ayni referansa baglanir.
        lastThrustWorld = rocketPoint.forward * currentThrust * thrustScale;
        rocketRb.AddForce(lastThrustWorld, ForceMode.Force);

        BuildGuidanceFrame(targetPoint.position - rocketPoint.position, out Vector3 upRefWorld, out Vector3 rightRefWorld, out Vector3 forwardRefWorld);
        BuildClockFrame(out Vector3 clock12World, out Vector3 clock3World, out Vector3 clockForwardWorld, out float clockValidity);
        float forwardUpDot = Vector3.Dot(clockForwardWorld, upRefWorld);
        float betaValidity = ComputeBetaValidity(forwardUpDot);

        float lowAltitudeTurnScale = ComputeLowAltitudeTurnScale();
        float clock12Raw = currentClock12Cmd - currentClock6Cmd;
        float clock3Raw = currentClock3Cmd - currentClock9Cmd;

        // Dusuk irtifada yukari toparlama komutu kisilmaz; aksi halde roket yere yaklasinca kendini kurtaramaz.
        // Clock 12 gravity-up yonudur. Clock 6 ve yatay kanal ise dusuk irtifada daha dikkatli uygulanir.
        float upTurnScale = Mathf.Max(lowAltitudeTurnScale, lowAltitudeUpTurnMinScale);
        float clock12Scale = clock12Raw >= 0f ? upTurnScale : lowAltitudeTurnScale;
        float clock3Scale = lowAltitudeTurnScale;
        float clock12Net = clock12Raw * clock12Scale;
        float clock3Net = clock3Raw * clock3Scale;
        Vector3 desiredClockTurnWorld = (clock12World * clock12Net) + (clock3World * clock3Net);
        Vector3 currentNoseTurnWorld = Vector3.Cross(rocketRb.angularVelocity, clockForwardWorld);

        // Clock action artik "su yone tork bas" degil, "burnu su yonde donder" istegidir.
        // Mevcut burun donus hizi hatadan dusulur; boylece roket hedefi gectikten sonra eski acisal hizla savrulmaz.
        Vector3 desiredNoseTurnWorld = desiredClockTurnWorld * Mathf.Max(0f, clockTurnRateTarget);
        Vector3 turnRateErrorWorld = desiredNoseTurnWorld - currentNoseTurnWorld;
        Vector3 commandTurnWorld = Vector3.Cross(clockForwardWorld, turnRateErrorWorld)
            * betaValidity
            * Mathf.Max(0f, clockTurnRateControllerGain);
        Vector3 commandTurnLocal = rocketRb.transform.InverseTransformDirection(commandTurnWorld);
        Vector3 localAngVel = rocketPoint.InverseTransformDirection(rocketRb.angularVelocity);
        float rollErrorRad = ComputeRollErrorRad(upRefWorld, rocketPoint.forward);
        float steeringMag = Mathf.Clamp01(Mathf.Sqrt((clock12Net * clock12Net) + (clock3Net * clock3Net)));
        float steeringRollScale = Mathf.Lerp(1f, activeSteeringRollScale, steeringMag);
        float validityRollScale = Mathf.Lerp(rollValidityFloor, 1f, Mathf.Clamp01(clockValidity));
        float rollControlScale = Mathf.Clamp01(steeringRollScale * validityRollScale);

        // Audit icin ham/net action ve ara vektorleri sakliyoruz.
        // Bu sayede Python tarafinda "komut verildi ama burun hangi yone dondu?" sorusu sayisal incelenebilir.
        lastClock12Raw = clock12Raw;
        lastClock3Raw = clock3Raw;
        lastClock12Net = clock12Net;
        lastClock3Net = clock3Net;
        lastLowAltitudeTurnScale = lowAltitudeTurnScale;
        lastClock12Scale = clock12Scale;
        lastClock3Scale = clock3Scale;
        lastBetaValidityApplied = betaValidity;
        lastDesiredClockTurnWorld = desiredClockTurnWorld;
        lastCommandTurnWorld = commandTurnWorld;
        lastCommandTurnLocal = commandTurnLocal;

        commandTurnLocal.z = 0f;
        // Roll baskisi steering'i ezmemeli. Roket aktif donus komutu alirken ve clock frame dik konumda zayifken
        // roll duzeltmesini ikincil tutuyoruz; boylece roll kontrolu pitch/yaw manevrasini bozmuyor.
        float rawRollCorrectionCmd = ((rollErrorRad * rollStabilizationGain) - (localAngVel.z * rollDampingGain)) * rollControlScale;
        float rollLimitScale = Mathf.Lerp(1f, Mathf.Max(rollValidityFloor, rollControlScale), steeringMag);
        float rollCorrectionLimit = maxRollCorrection * Mathf.Clamp01(rollLimitScale);
        float rollCorrectionCmd = Mathf.Clamp(rawRollCorrectionCmd, -rollCorrectionLimit, rollCorrectionLimit);

        if (suppressRollRate)
        {
            // Roll'u bu projede ogrenilecek ayri bir hedef yapmiyoruz.
            // Projection aktifken z torkunu sifirlayip roll rate'i fizik adimi sonunda temizliyoruz.
            rollCorrectionCmd = 0f;
            rollCorrectionLimit = 0f;
            rollControlScale = 0f;
        }

        commandTurnLocal.z += rollCorrectionCmd;
        commandTurnLocal.z = Mathf.Clamp(commandTurnLocal.z, -maxRollCorrection, maxRollCorrection);
        lastRollControlScale = rollControlScale;
        lastRollCorrectionCmd = rollCorrectionCmd;
        lastRollCorrectionLimit = rollCorrectionLimit;

        lastAppliedTurnLocal = commandTurnLocal;
        lastAppliedTurnWorld = rocketRb.transform.TransformDirection(lastAppliedTurnLocal);

        Vector3 torqueCommand = new Vector3(
            lastAppliedTurnLocal.x,
            lastAppliedTurnLocal.y,
            lastAppliedTurnLocal.z * rollTorqueScale
        );

        // Fizige giden son roll torkunu da sinirliyoruz.
        // Onceki clamp command seviyesindeydi; rollTorqueScale ve torqueScale carpilinca kalkista buyuk z-torku dogabiliyordu.
        Vector3 scaledTorqueCommand = torqueCommand * torqueScale;
        float pitchYawTorqueLimit = Mathf.Max(0f, maxPitchYawTorqueCommand);
        scaledTorqueCommand.x = Mathf.Clamp(scaledTorqueCommand.x, -pitchYawTorqueLimit, pitchYawTorqueLimit);
        scaledTorqueCommand.y = Mathf.Clamp(scaledTorqueCommand.y, -pitchYawTorqueLimit, pitchYawTorqueLimit);
        float rollTorqueLimit = Mathf.Max(0f, maxRollTorqueCommand);
        scaledTorqueCommand.z = Mathf.Clamp(scaledTorqueCommand.z, -rollTorqueLimit, rollTorqueLimit);
        lastTorqueCommandLocal = scaledTorqueCommand;
        lastRollTorqueLimit = rollTorqueLimit;
        lastTorqueCommandWorld = rocketRb.transform.TransformDirection(lastTorqueCommandLocal);
        rocketRb.AddRelativeTorque(lastTorqueCommandLocal, ForceMode.Force);
    }

    private void ApplyDirectGuidanceAction()
    {
        // Direct guidance testinde action artik tork degil, dunya uzayinda istenen ivmedir.
        // ForceMode.Acceleration kullandigimiz icin kütle etkisini ayri dusunmeyiz; bu sadece baseline testidir.
        Vector3 accelWorld = Vector3.ClampMagnitude(currentDirectAccelWorld, Mathf.Max(0f, directAccelLimit));
        Vector3 velocityWorld = rocketRb.linearVelocity;
        float maxSpeed = Mathf.Max(0f, directMaxSpeed);

        if (maxSpeed > 0f && velocityWorld.magnitude > maxSpeed && accelWorld.sqrMagnitude > 1e-8f)
        {
            Vector3 speedDir = velocityWorld.normalized;
            float speedUpPart = Vector3.Dot(accelWorld, speedDir);
            if (speedUpPart > 0f)
                accelWorld -= speedDir * speedUpPart;
        }

        lastThrustWorld = accelWorld;
        lastDesiredClockTurnWorld = currentDirectLookWorld.sqrMagnitude > 1e-8f
            ? currentDirectLookWorld.normalized
            : rocketPoint.forward;
        lastCommandTurnWorld = accelWorld;
        lastCommandTurnLocal = rocketRb.transform.InverseTransformDirection(accelWorld);
        lastAppliedTurnWorld = lastDesiredClockTurnWorld;
        lastAppliedTurnLocal = rocketRb.transform.InverseTransformDirection(lastAppliedTurnWorld);
        lastTorqueCommandLocal = Vector3.zero;
        lastTorqueCommandWorld = Vector3.zero;
        lastClock12Raw = 0f;
        lastClock3Raw = 0f;
        lastClock12Net = 0f;
        lastClock3Net = 0f;
        lastLowAltitudeTurnScale = 1f;
        lastClock12Scale = 1f;
        lastClock3Scale = 1f;
        lastBetaValidityApplied = 1f;
        lastRollControlScale = 0f;
        lastRollCorrectionCmd = 0f;
        lastRollCorrectionLimit = 0f;
        lastRollTorqueLimit = 0f;

        rocketRb.AddForce(accelWorld, ForceMode.Acceleration);

        if (currentGuidanceAccelLearningMode)
        {
            AlignRocketPointToGuidanceVelocity(accelWorld);
            return;
        }

        if (!currentBodyAccelLearningMode)
        {
            AlignRocketPointToDirectLook();
            DampenDirectSideSlip();
        }
    }

    private void AlignRocketPointToGuidanceVelocity(Vector3 accelWorld)
    {
        Vector3 lookWorld = rocketRb.linearVelocity;

        if (lookWorld.sqrMagnitude <= 1e-6f)
            lookWorld = currentDirectLookWorld;

        if (lookWorld.sqrMagnitude <= 1e-6f)
            lookWorld = accelWorld;

        if (lookWorld.sqrMagnitude <= 1e-6f)
            return;

        currentDirectLookWorld = lookWorld.normalized;
        AlignRocketPointToDirectLook();
    }

    private void DampenDirectSideSlip()
    {
        Vector3 lookWorld = currentDirectLookWorld.sqrMagnitude > 1e-8f
            ? currentDirectLookWorld.normalized
            : rocketPoint.forward.normalized;

        if (lookWorld.sqrMagnitude <= 1e-8f)
            return;

        Vector3 velocityWorld = rocketRb.linearVelocity;
        float forwardSpeed = Vector3.Dot(velocityWorld, lookWorld);
        Vector3 forwardVelocity = lookWorld * Mathf.Max(0f, forwardSpeed);
        Vector3 sideVelocity = velocityWorld - (lookWorld * forwardSpeed);

        // Direct action roketi hedefe bakan bir gudum testine ceviriyor.
        // Bu nedenle burnun tersine/yanina tasinan hizlari tamamen fiziksel serbestlik olarak birakmiyoruz;
        // aksi halde roket burnu donse bile eski hizla geri geri veya yan yan kaymaya devam ediyor.
        float sideBlend = Mathf.Clamp01(directVelocityAlignBlend);
        float backwardBlend = forwardSpeed < 0f ? Mathf.Clamp01(directBackwardVelocityDamp) : sideBlend;
        Vector3 correctedVelocity = forwardVelocity + (sideVelocity * (1f - sideBlend));

        if (forwardSpeed < 0f)
            correctedVelocity += lookWorld * forwardSpeed * (1f - backwardBlend);

        rocketRb.linearVelocity = correctedVelocity;
    }

    private void AlignRocketPointToDirectLook()
    {
        Vector3 lookWorld = currentDirectLookWorld.sqrMagnitude > 1e-8f
            ? currentDirectLookWorld.normalized
            : rocketPoint.forward.normalized;

        if (lookWorld.sqrMagnitude <= 1e-8f)
            return;

        // Burnu hedefe cevirirken roll'u serbest birakmiyoruz.
        // FromToRotation sadece forward eksenini hizalar; govde roll'u keyfi kalabilir.
        // LookRotation ise forward + gravity-up referansi ile okunur, roll-free bir durus kurar.
        Quaternion desiredRotation = BuildRollStableDirectRotation(lookWorld);
        Quaternion nextRotation = Quaternion.RotateTowards(
            rocketRb.rotation,
            desiredRotation,
            Mathf.Max(0f, directLookRateDeg) * Time.fixedDeltaTime
        );

        rocketRb.MoveRotation(nextRotation);

        if (directZeroAngularVelocity)
        {
            // Direct mode'da roll/donus dinamikleri test edilmiyor; kafa karistiran roll artefaktlarini sifirlariz.
            rocketRb.angularVelocity = Vector3.zero;
            lastSuppressedRollRate = 0f;
        }
    }

    private void ConfigureParticleFX()
    {
        if (rocketExhaustFx == null)
            return;

        // Duman onceki framelerde dogdugu yerde kalmali; roket dondukce eski dumanin birlikte donmesi
        // yan/geri ucus hissini abartiyor. World simulation yeni parcaciklari emitere uydurur, eskileri dondurmez.
        ParticleSystem.MainModule main = rocketExhaustFx.main;
        main.simulationSpace = rocketExhaustWorldSimulation
            ? ParticleSystemSimulationSpace.World
            : ParticleSystemSimulationSpace.Local;
    }

    private Quaternion BuildRollStableDirectRotation(Vector3 lookWorld)
    {
        Vector3 gravityWorld = Physics.gravity;
        Vector3 upRefWorld = gravityWorld.sqrMagnitude > 1e-8f ? (-gravityWorld).normalized : Vector3.up;
        Vector3 rollStableUp = Vector3.ProjectOnPlane(upRefWorld, lookWorld);

        if (rollStableUp.sqrMagnitude <= 1e-8f)
            rollStableUp = Vector3.ProjectOnPlane(cachedGuidanceForward, lookWorld);

        if (rollStableUp.sqrMagnitude <= 1e-8f)
            rollStableUp = Vector3.ProjectOnPlane(rocketRb.transform.up, lookWorld);

        if (rollStableUp.sqrMagnitude <= 1e-8f)
            rollStableUp = Vector3.Cross(Vector3.right, lookWorld);

        if (rollStableUp.sqrMagnitude <= 1e-8f)
            rollStableUp = Vector3.Cross(Vector3.forward, lookWorld);

        Quaternion desiredPointRotation = Quaternion.LookRotation(lookWorld, rollStableUp.normalized);
        Quaternion pointToDesiredDelta = desiredPointRotation * Quaternion.Inverse(rocketPoint.rotation);
        return pointToDesiredDelta * rocketRb.rotation;
    }

    private void SuppressRollRate()
    {
        if (!suppressRollRate)
        {
            lastSuppressedRollRate = 0f;
            return;
        }

        Vector3 forwardAxis = rocketPoint.forward.sqrMagnitude > 1e-8f
            ? rocketPoint.forward.normalized
            : rocketRb.transform.forward.normalized;

        float blend = Mathf.Clamp01(rollRateSuppressBlend);
        float rollRate = Vector3.Dot(rocketRb.angularVelocity, forwardAxis);
        Vector3 rollAngularVelocity = forwardAxis * rollRate;

        // Forward ekseni etrafindaki acisal hiz roll'dur; bunu temizleyerek roketi roll-free kabul ediyoruz.
        rocketRb.angularVelocity -= rollAngularVelocity * blend;
        lastSuppressedRollRate = rollRate * blend;
    }

    private void MoveTarget()
    {
        if (target == null) return;
        if (targetMoveDir.sqrMagnitude <= 1e-6f) return;

        Vector3 moveDelta = targetMoveDir * targetSpeed * Time.fixedDeltaTime;
        target.position += moveDelta;

        if (keepTargetYFixed)
        {
            Vector3 p = target.position;
            p.y = fixedTargetY;
            target.position = p;
        }

        if (keepTargetRotXFixed)
        {
            Vector3 e = target.eulerAngles;
            e.x = fixedTargetRotX;
            target.eulerAngles = e;
        }
    }

    private void ResetEnvironment(float[] resetValues)
    {
        float targetPosX = resetValues[0];
        float targetPosY = resetValues[1];
        if (keepTargetYFixed)
        {
            fixedTargetY = targetPosY + targetHeightOffset;
            targetPosY = fixedTargetY;
        }
        float targetPosZ = resetValues[2];

        float targetRotX = keepTargetRotXFixed ? fixedTargetRotX : 0f;
        float targetRotY = resetValues[3];
        float targetRotZ = resetValues[4];

        localStepCount = 0;

        target.position = new Vector3(targetPosX, targetPosY, targetPosZ);
        target.eulerAngles = new Vector3(targetRotX, targetRotY, targetRotZ);

        if (targetRb != null)
        {
            // Kinematic Rigidbody uzerinde velocity set etmek Unity'de uyari basar.
            // Once non-kinematic yapip hizi temizliyor, sonra hedefi tekrar script kontrollu kinematic moda aliyoruz.
            targetRb.isKinematic = false;
            targetRb.linearVelocity = Vector3.zero;
            targetRb.angularVelocity = Vector3.zero;
            targetRb.isKinematic = true;
        }

        rocketRb.isKinematic = true;
        Quaternion resetRotation = Quaternion.Euler(rocketResetEuler);
        rocket.position = rocketResetPosition;
        rocket.rotation = resetRotation;
        rocketRb.position = rocketResetPosition;
        rocketRb.rotation = resetRotation;
        Physics.SyncTransforms();

        rocketRb.isKinematic = false;
        rocketRb.linearVelocity = Vector3.zero;
        rocketRb.angularVelocity = Vector3.zero;
        rocketRb.WakeUp();

        currentThrust = 0f;
        currentClock12Cmd = 0f;
        currentClock6Cmd = 0f;
        currentClock3Cmd = 0f;
        currentClock9Cmd = 0f;
        currentDirectGuidanceMode = false;
        currentBodyAccelLearningMode = false;
        currentGuidanceAccelLearningMode = false;
        currentDirectAccelWorld = Vector3.zero;
        currentDirectLookWorld = rocketPoint != null ? rocketPoint.forward : Vector3.forward;

        float headingRad = targetRotZ * Mathf.Deg2Rad;
        targetMoveDir = new Vector3(-Mathf.Sin(headingRad), 0f, -Mathf.Cos(headingRad)).normalized;
        ResetGuidanceCache();

        if (rocketExhaustFx != null)
            rocketExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

        if (targetExhaustFx != null)
        {
            targetExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            targetExhaustFx.Play();
        }
    }

    private void SendStateToPython()
    {
        if (connector == null || !connector.IsConnected)
            return;

        OutgoingPacket packet = CollectPacket();
        packet.episode_id = currentEpisodeId;
        packet.step_id = currentStepId;

        connector.SendPacket(JsonUtility.ToJson(packet));
    }

    private float ComputeAGL(out bool grounded)
    {
        Vector3 origin = rocketRb.worldCenterOfMass;

        if (Physics.Raycast(origin, Vector3.down, out RaycastHit hit, groundRayMax, groundMask, QueryTriggerInteraction.Ignore))
        {
            grounded = (localStepCount > lowAltitudeGraceSteps) && (hit.distance <= groundedRayThreshold);
            return hit.distance;
        }

        grounded = false;
        return groundRayMax;
    }

    private float ReadAGLForControl()
    {
        Vector3 origin = rocketRb.worldCenterOfMass;
        if (Physics.Raycast(origin, Vector3.down, out RaycastHit hit, groundRayMax, groundMask, QueryTriggerInteraction.Ignore))
            return hit.distance;

        return groundRayMax;
    }

    private float ComputeLowAltitudeTurnScale()
    {
        float agl = ReadAGLForControl();
        float fullAgl = Mathf.Max(lowAltitudeTurnDampFullAgl, lowAltitudeTurnDampStartAgl + 0.01f);
        float t = Mathf.InverseLerp(lowAltitudeTurnDampStartAgl, fullAgl, agl);
        return Mathf.Lerp(lowAltitudeMinTurnScale, 1f, Mathf.Clamp01(t));
    }

    private static float[] ToFloatArray(Vector3 value)
    {
        return new float[] { value.x, value.y, value.z };
    }

    private static float[] ToFloatArray(Quaternion value)
    {
        return new float[] { value.x, value.y, value.z, value.w };
    }

    private static Vector3 ProjectOnPlaneNormalized(Vector3 value, Vector3 planeNormal)
    {
        Vector3 projected = Vector3.ProjectOnPlane(value, planeNormal);
        if (projected.sqrMagnitude <= 1e-8f)
            return Vector3.zero;

        return projected.normalized;
    }

    private void ResetGuidanceCache()
    {
        Vector3 gravityWorld = Physics.gravity;
        Vector3 upRefWorld = gravityWorld.sqrMagnitude > 1e-8f ? (-gravityWorld).normalized : Vector3.up;
        Vector3 fallbackForward = ProjectOnPlaneNormalized(rocketPoint.forward, upRefWorld);

        if (fallbackForward.sqrMagnitude <= 1e-8f)
            fallbackForward = ProjectOnPlaneNormalized(targetPoint.position - rocketPoint.position, upRefWorld);

        if (fallbackForward.sqrMagnitude <= 1e-8f)
            fallbackForward = Vector3.forward;

        cachedGuidanceForward = fallbackForward.normalized;
        lastAppliedTurnWorld = Vector3.zero;
        lastAppliedTurnLocal = Vector3.zero;
    }

    private void BuildGuidanceFrame(Vector3 relPosWorld, out Vector3 upRefWorld, out Vector3 rightRefWorld, out Vector3 forwardRefWorld)
    {
        Vector3 gravityWorld = Physics.gravity;
        upRefWorld = gravityWorld.sqrMagnitude > 1e-8f ? (-gravityWorld).normalized : Vector3.up;

        Vector3 relDirWorld = relPosWorld.sqrMagnitude > 1e-8f ? relPosWorld.normalized : rocketPoint.forward;
        Vector3 velocityProjected = ProjectOnPlaneNormalized(rocketRb.linearVelocity, upRefWorld);
        Vector3 forwardProjected = ProjectOnPlaneNormalized(rocketPoint.forward, upRefWorld);
        Vector3 relProjected = ProjectOnPlaneNormalized(relDirWorld, upRefWorld);

        forwardRefWorld = velocityProjected;
        if (forwardRefWorld.sqrMagnitude <= 1e-8f)
            forwardRefWorld = forwardProjected;
        if (forwardRefWorld.sqrMagnitude <= 1e-8f)
            forwardRefWorld = relProjected;
        if (forwardRefWorld.sqrMagnitude <= 1e-8f)
            forwardRefWorld = cachedGuidanceForward;
        if (forwardRefWorld.sqrMagnitude <= 1e-8f)
            forwardRefWorld = Vector3.forward;

        rightRefWorld = Vector3.Cross(upRefWorld, forwardRefWorld);
        if (rightRefWorld.sqrMagnitude <= 1e-8f)
        {
            forwardRefWorld = Vector3.forward;
            rightRefWorld = Vector3.Cross(upRefWorld, forwardRefWorld);
        }

        rightRefWorld.Normalize();
        forwardRefWorld = Vector3.Cross(rightRefWorld, upRefWorld).normalized;
        cachedGuidanceForward = forwardRefWorld;
    }

    private void BuildClockFrame(out Vector3 clock12World, out Vector3 clock3World, out Vector3 clockForwardWorld, out float clockValidity)
    {
        Vector3 gravityWorld = Physics.gravity;
        Vector3 gravityUpWorld = gravityWorld.sqrMagnitude > 1e-8f ? (-gravityWorld).normalized : Vector3.up;

        clockForwardWorld = rocketPoint.forward.sqrMagnitude > 1e-8f
            ? rocketPoint.forward.normalized
            : Vector3.forward;

        Vector3 projectedGravityUp = Vector3.ProjectOnPlane(gravityUpWorld, clockForwardWorld);
        clockValidity = Mathf.Clamp01(projectedGravityUp.magnitude);

        if (projectedGravityUp.sqrMagnitude > 1e-8f)
        {
            clock12World = projectedGravityUp.normalized;
        }
        else
        {
            // Roket tam dikken gravity-up, burun eksenine paralel olur ve clock-12 tanimsiz kalir.
            // Bu durumda roketin roll'e bagli yan ekseni yerine hedef/cached guidance yonunu kullaniriz.
            // Boylece silindirik govde uzerindeki keyfi "saat 12" secimi hedefe gore kararlı kalir.
            Vector3 targetBearingFallback = ProjectOnPlaneNormalized(targetPoint.position - rocketPoint.position, clockForwardWorld);
            Vector3 cachedFallback = ProjectOnPlaneNormalized(cachedGuidanceForward, clockForwardWorld);
            clock12World = targetBearingFallback.sqrMagnitude > 1e-8f ? targetBearingFallback : cachedFallback;
        }

        if (clock12World.sqrMagnitude <= 1e-8f)
            clock12World = ProjectOnPlaneNormalized(Vector3.forward, clockForwardWorld);

        if (clock12World.sqrMagnitude <= 1e-8f)
            clock12World = Vector3.up;

        clock3World = Vector3.Cross(clock12World, clockForwardWorld);
        if (clock3World.sqrMagnitude <= 1e-8f)
            clock3World = rocketPoint.right;

        clock3World.Normalize();
        clock12World = Vector3.Cross(clockForwardWorld, clock3World).normalized;
    }

    private float ComputeRollErrorRad(Vector3 upRefWorld, Vector3 forwardAxisWorld)
    {
        Vector3 refUpOnPlane = Vector3.ProjectOnPlane(upRefWorld, forwardAxisWorld);
        Vector3 rocketUpOnPlane = Vector3.ProjectOnPlane(rocketPoint.up, forwardAxisWorld);

        if (refUpOnPlane.sqrMagnitude <= 1e-8f || rocketUpOnPlane.sqrMagnitude <= 1e-8f)
            return 0f;

        refUpOnPlane.Normalize();
        rocketUpOnPlane.Normalize();

        float rollErrorDeg = Vector3.SignedAngle(rocketUpOnPlane, refUpOnPlane, forwardAxisWorld);
        return rollErrorDeg * Mathf.Deg2Rad;
    }

    private float ComputeBetaValidity(float forwardUpDot)
    {
        float absForwardUpDot = Mathf.Abs(forwardUpDot);
        if (absForwardUpDot <= betaFadeStartAbsForwardUp)
            return 1f;

        if (absForwardUpDot >= betaFadeEndAbsForwardUp)
            return betaValidityFloor;

        float t = Mathf.InverseLerp(betaFadeStartAbsForwardUp, betaFadeEndAbsForwardUp, absForwardUpDot);
        t = Mathf.Clamp01(t);
        float smooth = t * t * (3f - 2f * t);
        return betaValidityFloor + ((1f - betaValidityFloor) * (1f - smooth));
    }

    private OutgoingPacket CollectPacket()
    {
        OutgoingStateData s = new OutgoingStateData();
        OutgoingTelemetryData telemetry = new OutgoingTelemetryData();

        Vector3 relPosWorld = targetPoint.position - rocketPoint.position;
        float distance = relPosWorld.magnitude;
        Vector3 relDirWorld = distance > 1e-6f ? relPosWorld / distance : Vector3.zero;
        Vector3 rocketForwardWorld = rocketPoint.forward.normalized;
        Vector3 rocketRightWorld = rocketPoint.right.normalized;
        Vector3 rocketBodyForwardWorld = rocketRb.transform.forward.normalized;
        Vector3 rocketBodyUpWorld = rocketRb.transform.up.normalized;
        Vector3 rocketBodyRightWorld = rocketRb.transform.right.normalized;

        Vector3 targetVelWorld = (targetMoveDir.sqrMagnitude > 1e-6f)
            ? targetMoveDir * targetSpeed
            : Vector3.zero;

        Vector3 rocketVelWorld = rocketRb.linearVelocity;
        Vector3 relVelWorld = targetVelWorld - rocketVelWorld;
        Vector3 rocketAngVelWorld = rocketRb.angularVelocity;
        Vector3 targetAngVelWorld = targetRb != null ? targetRb.angularVelocity : Vector3.zero;
        Vector3 gravityWorld = Physics.gravity;

        Vector3 relPosLocal = rocketPoint.InverseTransformDirection(relPosWorld);
        Vector3 relDirLocal = distance > 1e-6f ? rocketPoint.InverseTransformDirection(relDirWorld) : Vector3.zero;
        Vector3 rocketVelLocal = rocketPoint.InverseTransformDirection(rocketVelWorld);
        Vector3 targetVelLocal = rocketPoint.InverseTransformDirection(targetVelWorld);
        Vector3 relVelLocal = rocketPoint.InverseTransformDirection(relVelWorld);
        Vector3 rocketAngVelLocal = rocketPoint.InverseTransformDirection(rocketAngVelWorld);
        Vector3 targetAngVelLocal = rocketPoint.InverseTransformDirection(targetAngVelWorld);
        Vector3 gravityLocal = rocketPoint.InverseTransformDirection(gravityWorld);
        BuildGuidanceFrame(relPosWorld, out Vector3 upRefWorld, out Vector3 rightRefWorld, out Vector3 forwardRefWorld);
        BuildClockFrame(out Vector3 clock12World, out Vector3 clock3World, out Vector3 clockForwardWorld, out float clockValidity);
        float forwardUpDot = Vector3.Dot(rocketForwardWorld, upRefWorld);
        float betaValidity = ComputeBetaValidity(forwardUpDot);

        Vector3 relDirClockPlane = Vector3.ProjectOnPlane(relDirWorld, clockForwardWorld);
        Vector3 lateralClockDir = relDirClockPlane.sqrMagnitude > 1e-8f ? relDirClockPlane.normalized : Vector3.zero;
        float targetClock12Signed = Vector3.Dot(lateralClockDir, clock12World);
        float targetClock3Signed = Vector3.Dot(lateralClockDir, clock3World);
        float targetClockAngleDeg = lateralClockDir.sqrMagnitude > 1e-8f
            ? Mathf.Atan2(targetClock3Signed, targetClock12Signed) * Mathf.Rad2Deg
            : 0f;

        float relVelClock12Signed = Vector3.Dot(relVelWorld, clock12World);
        float relVelClock3Signed = Vector3.Dot(relVelWorld, clock3World);
        float relVelForwardClock = Vector3.Dot(relVelWorld, clockForwardWorld);

        Vector3 noseTurnWorld = Vector3.Cross(rocketAngVelWorld, clockForwardWorld);
        float turnClock12Signed = Vector3.Dot(noseTurnWorld, clock12World);
        float turnClock3Signed = Vector3.Dot(noseTurnWorld, clock3World);
        float turnRateRoll = Vector3.Dot(rocketAngVelWorld, clockForwardWorld);

        float actionClock12Net = currentClock12Cmd - currentClock6Cmd;
        float actionClock3Net = currentClock3Cmd - currentClock9Cmd;
        float actionClockMag = Mathf.Sqrt((actionClock12Net * actionClock12Net) + (actionClock3Net * actionClock3Net));
        float actionClockAngleDeg = actionClockMag > 1e-6f
            ? Mathf.Atan2(actionClock3Net, actionClock12Net) * Mathf.Rad2Deg
            : 0f;

        Vector3 relDirTop = Vector3.ProjectOnPlane(relDirWorld, upRefWorld);
        if (relDirTop.sqrMagnitude > 1e-8f)
            relDirTop.Normalize();
        else
            relDirTop = forwardRefWorld;

        Vector3 rocketForwardTop = Vector3.ProjectOnPlane(rocketForwardWorld, upRefWorld);
        if (rocketForwardTop.sqrMagnitude > 1e-8f)
            rocketForwardTop.Normalize();
        else
            rocketForwardTop = forwardRefWorld;

        Vector3 relDirSide = Vector3.ProjectOnPlane(relDirWorld, rightRefWorld);
        if (relDirSide.sqrMagnitude > 1e-8f)
            relDirSide.Normalize();
        else
            relDirSide = forwardRefWorld;

        Vector3 rocketForwardSide = Vector3.ProjectOnPlane(rocketForwardWorld, rightRefWorld);
        if (rocketForwardSide.sqrMagnitude > 1e-8f)
            rocketForwardSide.Normalize();
        else
            rocketForwardSide = Vector3.ProjectOnPlane(forwardRefWorld, rightRefWorld);

        if (rocketForwardSide.sqrMagnitude > 1e-8f)
            rocketForwardSide.Normalize();
        else
            rocketForwardSide = relDirSide;

        float thetaRad = distance > 1e-6f
            ? Mathf.Acos(Mathf.Clamp(Vector3.Dot(rocketForwardWorld, relDirWorld), -1f, 1f))
            : 0f;
        float alphaRad = Vector3.SignedAngle(rocketForwardSide, relDirSide, rightRefWorld) * Mathf.Deg2Rad;
        float betaRawRad = Vector3.SignedAngle(rocketForwardTop, relDirTop, upRefWorld) * Mathf.Deg2Rad;
        float betaRad = betaRawRad * betaValidity;

        Vector3 relVelGuidance = new Vector3(
            Vector3.Dot(relVelWorld, rightRefWorld),
            Vector3.Dot(relVelWorld, upRefWorld),
            Vector3.Dot(relVelWorld, forwardRefWorld)
        );
        Vector3 rocketAngVelGuidance = new Vector3(
            Vector3.Dot(rocketAngVelWorld, rightRefWorld),
            Vector3.Dot(rocketAngVelWorld, upRefWorld),
            Vector3.Dot(rocketAngVelWorld, forwardRefWorld)
        );
        float rollErrorDeg = ComputeRollErrorRad(upRefWorld, rocketPoint.forward) * Mathf.Rad2Deg;
        Vector3 guidanceUpLocal = rocketRb.transform.InverseTransformDirection(upRefWorld);
        Vector3 guidanceRightLocal = rocketRb.transform.InverseTransformDirection(rightRefWorld);
        Vector3 guidanceForwardLocal = rocketRb.transform.InverseTransformDirection(forwardRefWorld);
        Vector3 clock12Local = rocketRb.transform.InverseTransformDirection(clock12World);
        Vector3 clock3Local = rocketRb.transform.InverseTransformDirection(clock3World);
        Vector3 clockForwardLocal = rocketRb.transform.InverseTransformDirection(clockForwardWorld);

        s.distance = distance;
        s.theta_rad = thetaRad;
        s.alpha_rad = alphaRad;
        s.beta_rad = betaRad;
        s.closing_speed = distance > 1e-6f ? -Vector3.Dot(relVelWorld, relDirWorld) : 0f;

        s.target_clock[0] = Mathf.Max(0f, targetClock12Signed);
        s.target_clock[1] = Mathf.Max(0f, -targetClock12Signed);
        s.target_clock[2] = Mathf.Max(0f, targetClock3Signed);
        s.target_clock[3] = Mathf.Max(0f, -targetClock3Signed);

        s.rel_vel_clock[0] = Mathf.Max(0f, relVelClock12Signed);
        s.rel_vel_clock[1] = Mathf.Max(0f, -relVelClock12Signed);
        s.rel_vel_clock[2] = Mathf.Max(0f, relVelClock3Signed);
        s.rel_vel_clock[3] = Mathf.Max(0f, -relVelClock3Signed);
        s.rel_vel_forward = relVelForwardClock;

        s.turn_rate_clock[0] = Mathf.Max(0f, turnClock12Signed);
        s.turn_rate_clock[1] = Mathf.Max(0f, -turnClock12Signed);
        s.turn_rate_clock[2] = Mathf.Max(0f, turnClock3Signed);
        s.turn_rate_clock[3] = Mathf.Max(0f, -turnClock3Signed);
        s.turn_rate_roll = turnRateRoll;
        s.clock_validity = clockValidity;

        s.rel_vel_ref[0] = relVelGuidance.x;
        s.rel_vel_ref[1] = relVelGuidance.y;
        s.rel_vel_ref[2] = relVelGuidance.z;

        s.turn_rate_ref[0] = rocketAngVelGuidance.x;
        s.turn_rate_ref[1] = rocketAngVelGuidance.y;
        s.turn_rate_ref[2] = rocketAngVelGuidance.z;

        s.forward_up_dot = forwardUpDot;
        bool grounded;
        s.agl = ComputeAGL(out grounded);
        s.alt_error = targetPoint.position.y - rocketPoint.position.y;
        s.grounded_flag = grounded ? 1f : 0f;

        telemetry.rocket_pos_world = ToFloatArray(rocket.position);
        telemetry.rocket_euler_world = ToFloatArray(rocket.eulerAngles);
        telemetry.rocket_rot_world = ToFloatArray(rocket.rotation);
        telemetry.rocket_point_pos_world = ToFloatArray(rocketPoint.position);
        telemetry.rocket_point_forward_world = ToFloatArray(rocketPoint.forward);
        telemetry.rocket_point_up_world = ToFloatArray(rocketPoint.up);
        telemetry.rocket_point_right_world = ToFloatArray(rocketRightWorld);
        telemetry.rocket_body_forward_world = ToFloatArray(rocketBodyForwardWorld);
        telemetry.rocket_body_up_world = ToFloatArray(rocketBodyUpWorld);
        telemetry.rocket_body_right_world = ToFloatArray(rocketBodyRightWorld);
        telemetry.rocket_vel_world = ToFloatArray(rocketVelWorld);
        telemetry.rocket_vel_local = ToFloatArray(rocketVelLocal);
        telemetry.rocket_ang_vel_world = ToFloatArray(rocketAngVelWorld);
        telemetry.rocket_ang_vel_local = ToFloatArray(rocketAngVelLocal);

        telemetry.target_pos_world = ToFloatArray(target.position);
        telemetry.target_euler_world = ToFloatArray(target.eulerAngles);
        telemetry.target_rot_world = ToFloatArray(target.rotation);
        telemetry.target_point_pos_world = ToFloatArray(targetPoint.position);
        telemetry.target_point_forward_world = ToFloatArray(targetPoint.forward);
        telemetry.target_point_up_world = ToFloatArray(targetPoint.up);
        telemetry.target_vel_world = ToFloatArray(targetVelWorld);
        telemetry.target_vel_in_rocket_local = ToFloatArray(targetVelLocal);
        telemetry.target_ang_vel_world = ToFloatArray(targetAngVelWorld);
        telemetry.target_ang_vel_in_rocket_local = ToFloatArray(targetAngVelLocal);

        telemetry.rel_pos_world = ToFloatArray(relPosWorld);
        telemetry.rel_pos_local = ToFloatArray(relPosLocal);
        telemetry.rel_dir_world = ToFloatArray(relDirWorld);
        telemetry.rel_dir_local = ToFloatArray(relDirLocal);
        telemetry.rel_vel_world = ToFloatArray(relVelWorld);
        telemetry.rel_vel_local = ToFloatArray(relVelLocal);
        telemetry.gravity_world = ToFloatArray(gravityWorld);
        telemetry.gravity_local = ToFloatArray(gravityLocal);
        telemetry.guidance_up_world = ToFloatArray(upRefWorld);
        telemetry.guidance_right_world = ToFloatArray(rightRefWorld);
        telemetry.guidance_forward_world = ToFloatArray(forwardRefWorld);
        telemetry.guidance_up_local = ToFloatArray(guidanceUpLocal);
        telemetry.guidance_right_local = ToFloatArray(guidanceRightLocal);
        telemetry.guidance_forward_local = ToFloatArray(guidanceForwardLocal);
        telemetry.clock_12_world = ToFloatArray(clock12World);
        telemetry.clock_3_world = ToFloatArray(clock3World);
        telemetry.clock_forward_world = ToFloatArray(clockForwardWorld);
        telemetry.clock_12_local = ToFloatArray(clock12Local);
        telemetry.clock_3_local = ToFloatArray(clock3Local);
        telemetry.clock_forward_local = ToFloatArray(clockForwardLocal);
        telemetry.rel_vel_guidance = ToFloatArray(relVelGuidance);
        telemetry.rel_vel_clock_signed = ToFloatArray(new Vector3(relVelClock12Signed, relVelClock3Signed, relVelForwardClock));
        telemetry.rocket_ang_vel_guidance = ToFloatArray(rocketAngVelGuidance);
        telemetry.rocket_turn_clock_signed = ToFloatArray(new Vector3(turnClock12Signed, turnClock3Signed, turnRateRoll));
        telemetry.thrust_world = ToFloatArray(lastThrustWorld);
        telemetry.desired_clock_turn_world = ToFloatArray(lastDesiredClockTurnWorld);
        telemetry.command_turn_world = ToFloatArray(lastCommandTurnWorld);
        telemetry.command_turn_local = ToFloatArray(lastCommandTurnLocal);
        telemetry.torque_command_local = ToFloatArray(lastTorqueCommandLocal);
        telemetry.torque_command_world = ToFloatArray(lastTorqueCommandWorld);
        telemetry.applied_turn_world = ToFloatArray(lastAppliedTurnWorld);
        telemetry.applied_turn_local = ToFloatArray(lastAppliedTurnLocal);
        telemetry.target_speed = targetSpeed;
        telemetry.roll_error_deg = rollErrorDeg;
        telemetry.beta_validity = betaValidity;
        telemetry.clock_validity = clockValidity;
        telemetry.target_clock_angle_deg = targetClockAngleDeg;
        telemetry.action_clock_angle_deg = actionClockAngleDeg;
        telemetry.action_clock_mag = actionClockMag;
        telemetry.action_clock12_raw = lastClock12Raw;
        telemetry.action_clock3_raw = lastClock3Raw;
        telemetry.action_clock12_net = lastClock12Net;
        telemetry.action_clock3_net = lastClock3Net;
        telemetry.low_altitude_turn_scale = lastLowAltitudeTurnScale;
        telemetry.clock12_scale = lastClock12Scale;
        telemetry.clock3_scale = lastClock3Scale;
        telemetry.beta_validity_applied = lastBetaValidityApplied;
        telemetry.roll_control_scale = lastRollControlScale;
        telemetry.roll_correction_cmd = lastRollCorrectionCmd;
        telemetry.roll_correction_limit = lastRollCorrectionLimit;
        telemetry.roll_torque_limit = lastRollTorqueLimit;
        telemetry.suppressed_roll_rate = lastSuppressedRollRate;
        telemetry.rocket_point_body_forward_dot = Vector3.Dot(rocketPoint.forward.normalized, rocketBodyForwardWorld);
        telemetry.rocket_point_body_up_dot = Vector3.Dot(rocketPoint.up.normalized, rocketBodyUpWorld);
        telemetry.rocket_point_body_right_dot = Vector3.Dot(rocketPoint.right.normalized, rocketBodyRightWorld);

        return new OutgoingPacket
        {
            states = s,
            telemetry = telemetry
        };
    }

    private void UpdateDebugLines()
    {
        if (distanceLine != null)
        {
            distanceLine.SetPosition(0, rocketPoint.position);
            distanceLine.SetPosition(1, targetPoint.position);
        }

        if (forwardLine != null)
        {
            forwardLine.SetPosition(0, rocketPoint.position);
            forwardLine.SetPosition(1, rocketPoint.position + rocketPoint.forward * forwardLineLength);
        }

        DrawActionAuditRays();
    }

    private void DrawActionAuditRays()
    {
        if (!drawActionAuditRays)
            return;

        Vector3 origin = rocketPoint.position;
        float rayDuration = Mathf.Max(0f, actionAuditRayDuration);

        // Scene view icin renkli eksen cizimleri:
        // Cyan burun/itki, yesil clock-12, sari clock-3, beyaz hedef, magenta istenen donus, kirmizi uygulanan tork.
        DrawSoftAuditRay(origin, rocketPoint.forward, SoftColor(0.35f, 0.85f, 1.0f), rayDuration);

        if (currentDirectGuidanceMode)
        {
            // Direct mode'da clock eksenleri bilerek cizilmez; onlar roll varmis gibi kafa karistirabiliyor.
            // Burada sadece hedef yonu, istenen look yonu ve uygulanan ivme gosterilir.
            Vector3 relToTargetDirect = targetPoint.position - rocketPoint.position;
            if (relToTargetDirect.sqrMagnitude > 1e-8f)
                DrawSoftAuditRay(origin, relToTargetDirect, SoftColor(0.92f, 0.92f, 0.92f), rayDuration);

            if (lastDesiredClockTurnWorld.sqrMagnitude > 1e-8f)
                DrawSoftAuditRay(origin, lastDesiredClockTurnWorld, SoftColor(0.86f, 0.40f, 0.88f), rayDuration);

            if (lastThrustWorld.sqrMagnitude > 1e-8f)
                DrawSoftAuditRay(origin, lastThrustWorld, SoftColor(1.0f, 0.42f, 0.34f), rayDuration);

            return;
        }

        BuildClockFrame(out Vector3 clock12World, out Vector3 clock3World, out _, out _);
        DrawSoftAuditRay(origin, clock12World, SoftColor(0.35f, 0.85f, 0.45f), rayDuration);
        DrawSoftAuditRay(origin, clock3World, SoftColor(0.95f, 0.82f, 0.35f), rayDuration);

        Vector3 relToTarget = targetPoint.position - rocketPoint.position;
        if (relToTarget.sqrMagnitude > 1e-8f)
            DrawSoftAuditRay(origin, relToTarget, SoftColor(0.92f, 0.92f, 0.92f), rayDuration);

        if (lastDesiredClockTurnWorld.sqrMagnitude > 1e-8f)
            DrawSoftAuditRay(origin, lastDesiredClockTurnWorld, SoftColor(0.86f, 0.40f, 0.88f), rayDuration);

        if (lastTorqueCommandWorld.sqrMagnitude > 1e-8f)
            DrawSoftAuditRay(origin, lastTorqueCommandWorld, SoftColor(1.0f, 0.42f, 0.34f), rayDuration);
    }

    private Color SoftColor(float r, float g, float b)
    {
        return new Color(r, g, b, Mathf.Clamp01(actionAuditRayAlpha));
    }

    private void DrawSoftAuditRay(Vector3 origin, Vector3 direction, Color color, float duration)
    {
        if (direction.sqrMagnitude <= 1e-8f)
            return;

        Debug.DrawRay(origin, direction.normalized * actionAuditRayLength, color, duration, false);
    }

    private void UpdateParticleFX()
    {
        if (rocketExhaustFx != null)
        {
            AlignRocketExhaustFX();

            bool shouldPlayRocketFx = currentThrust > 0.1f
                || (currentDirectGuidanceMode && currentDirectAccelWorld.sqrMagnitude > 0.01f);
            if (shouldPlayRocketFx)
            {
                if (!rocketExhaustFx.isPlaying) rocketExhaustFx.Play();
            }
            else
            {
                if (rocketExhaustFx.isPlaying)
                    rocketExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmitting);
            }
        }

        if (targetExhaustFx != null && !targetExhaustFx.isPlaying)
        {
            targetExhaustFx.Play();
        }
    }

    private void AlignRocketExhaustFX()
    {
        if (!alignRocketExhaustToRocketPoint || rocketExhaustFx == null || rocketPoint == null)
            return;

        Vector3 forward = rocketPoint.forward.sqrMagnitude > 1e-8f
            ? rocketPoint.forward.normalized
            : rocket.transform.forward.normalized;
        Vector3 up = rocketPoint.up.sqrMagnitude > 1e-8f
            ? rocketPoint.up.normalized
            : Vector3.up;

        // Particle sistemi local +Z yonune emis yapiyor kabul edilir; egzoz bunun tersine,
        // yani roket burnunun arkasina bakmalidir.
        Transform fxTransform = rocketExhaustFx.transform;
        fxTransform.position = rocketPoint.position - forward * Mathf.Max(0f, rocketExhaustBackOffset);
        fxTransform.rotation = Quaternion.LookRotation(-forward, up);
    }

    private void OnApplicationQuit()
    {
        connector?.Close();
#if UNITY_6000_0_OR_NEWER
        Physics.simulationMode = SimulationMode.FixedUpdate;
#else
        Physics.autoSimulation = true;
#endif
    }

    private void OnDestroy()
    {
        connector?.Close();
#if UNITY_6000_0_OR_NEWER
        Physics.simulationMode = SimulationMode.FixedUpdate;
#else
        Physics.autoSimulation = true;
#endif
    }
}
