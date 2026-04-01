using System;
using UnityEngine;

// =============================================================================
// PYTHON STATE VEKTORI SOZLESMESI  (env.py - parse_state + normalize_state)
// =============================================================================
// Unity tarafinin gonderecegi alanlar ile Python'da kurulan 14 boyutlu state:
//
//  Index  | Python state adi | JSON alani
//  -------|------------------|--------------------------------------
//   0     | distance         | states.distance
//   1     | look_angle_rad   | states.look_angle_rad
//   2     | closing_speed    | states.closing_speed
//   3-5   | rel_vel_x/y/z    | states.rel_vel[0..2]
//   6-8   | roc_ang_vel_x/y/z| states.roc_ang_vel[0..2]
//   9-11  | gx/gy/gz         | states.g[0..2]
//   12    | agl              | states.agl
//   13    | alt_error        | states.alt_error
//
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
    public float look_angle_rad;
    public float closing_speed;

    public float[] rel_vel = new float[3];
    public float[] roc_ang_vel = new float[3];
    public float[] g = new float[3];

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

    public float target_speed;
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

    [Header("Rocket Reset Pose")]
    public Vector3 rocketResetPosition = new Vector3(-0.492f, 0.8375f, 0.022f);
    public Vector3 rocketResetEuler = new Vector3(-90f, 0f, 0f);

    [Header("Action Scales")]
    public float thrustScale = 1f;
    public float torqueScale = 1f;

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

    private Connector connector;

    private int currentEpisodeId = 0;
    private int currentStepId = 0;
    private int localStepCount = 0;

    private float currentThrust = 0f;
    private float currentPitch = 0f;
    private float currentYaw = 0f;

    private float fixedTargetY;
    private float fixedTargetRotX;
    private Vector3 targetMoveDir = Vector3.zero;

    private void Start()
    {
        ValidateAndBindReferences();

        fixedTargetY = target.position.y;
        fixedTargetRotX = target.eulerAngles.x;

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
            if (packet.values == null || packet.values.Length < 3)
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
        currentThrust = actionValues[0];
        currentPitch = actionValues[1];
        currentYaw = actionValues[2];
    }

    private void StepOnce()
    {
        localStepCount += 1;

        MoveTarget();
        ApplyAction();
        UpdateParticleFX();

        Physics.Simulate(Time.fixedDeltaTime);
        UpdateDebugLines();
        SendStateToPython();
    }

    private void ApplyAction()
    {
        rocketRb.AddRelativeForce(Vector3.forward * currentThrust * thrustScale, ForceMode.Force);

        Vector3 torque = new Vector3(currentPitch, currentYaw, 0f) * torqueScale;
        rocketRb.AddRelativeTorque(torque, ForceMode.Force);
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
        float targetPosY = keepTargetYFixed ? fixedTargetY : resetValues[1];
        float targetPosZ = resetValues[2];

        float targetRotX = keepTargetRotXFixed ? fixedTargetRotX : 0f;
        float targetRotY = resetValues[3];
        float targetRotZ = resetValues[4];

        localStepCount = 0;

        target.position = new Vector3(targetPosX, targetPosY, targetPosZ);
        target.eulerAngles = new Vector3(targetRotX, targetRotY, targetRotZ);

        if (targetRb != null)
        {
            targetRb.linearVelocity = Vector3.zero;
            targetRb.angularVelocity = Vector3.zero;
            targetRb.isKinematic = true;
        }

        rocketRb.isKinematic = true;
        rocket.position = rocketResetPosition;
        rocket.rotation = Quaternion.Euler(rocketResetEuler);
        Physics.SyncTransforms();

        rocketRb.isKinematic = false;
        rocketRb.linearVelocity = Vector3.zero;
        rocketRb.angularVelocity = Vector3.zero;
        rocketRb.WakeUp();

        currentThrust = 0f;
        currentPitch = 0f;
        currentYaw = 0f;

        float headingRad = targetRotZ * Mathf.Deg2Rad;
        targetMoveDir = new Vector3(-Mathf.Sin(headingRad), 0f, -Mathf.Cos(headingRad)).normalized;

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

    private static float[] ToFloatArray(Vector3 value)
    {
        return new float[] { value.x, value.y, value.z };
    }

    private static float[] ToFloatArray(Quaternion value)
    {
        return new float[] { value.x, value.y, value.z, value.w };
    }

    private OutgoingPacket CollectPacket()
    {
        OutgoingStateData s = new OutgoingStateData();
        OutgoingTelemetryData telemetry = new OutgoingTelemetryData();

        Vector3 relPosWorld = targetPoint.position - rocketPoint.position;
        float distance = relPosWorld.magnitude;
        Vector3 relDirWorld = distance > 1e-6f ? relPosWorld / distance : Vector3.zero;
        Vector3 rocketForwardWorld = rocketPoint.forward.normalized;

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

        Vector3 relVelUsed = relVelWorld;
        Vector3 rocAngVelUsed = rocketAngVelWorld;
        Vector3 gravityUsed = gravityWorld;

        if (useLocalFrame)
        {
            relVelUsed = relVelLocal;
            rocAngVelUsed = rocketAngVelLocal;
            gravityUsed = gravityLocal;
        }

        s.distance = distance;
        s.look_angle_rad = distance > 1e-6f
            ? Mathf.Acos(Mathf.Clamp(Vector3.Dot(rocketForwardWorld, relDirWorld), -1f, 1f))
            : 0f;
        s.closing_speed = distance > 1e-6f ? -Vector3.Dot(relVelWorld, relDirWorld) : 0f;

        s.rel_vel[0] = relVelUsed.x;
        s.rel_vel[1] = relVelUsed.y;
        s.rel_vel[2] = relVelUsed.z;

        s.roc_ang_vel[0] = rocAngVelUsed.x;
        s.roc_ang_vel[1] = rocAngVelUsed.y;
        s.roc_ang_vel[2] = rocAngVelUsed.z;

        s.g[0] = gravityUsed.x;
        s.g[1] = gravityUsed.y;
        s.g[2] = gravityUsed.z;

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
        telemetry.target_speed = targetSpeed;

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
    }

    private void UpdateParticleFX()
    {
        if (rocketExhaustFx != null)
        {
            if (currentThrust > 0.1f)
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
