using System;
using UnityEngine;

// =============================================================================
// PYTHON STATE VEKTORI SOZLESMESI  (env.py - parse_state + normalize_state)
// =============================================================================
// Unity tarafinin gonderecegi alanlar ile Python'da kurulan 18 boyutlu state:
//
//  Index  | Python state adi | JSON alani
//  -------|------------------|--------------------------------------
//   0     | los_yaw_sin      | states.los_yaw_sin
//   1     | los_yaw_cos      | states.los_yaw_cos
//   2     | los_pitch_sin    | states.los_pitch_sin
//   3     | los_pitch_cos    | states.los_pitch_cos
//   4     | distance         | states.distance
//   5     | closing_speed    | states.closing_speed
//   6-8   | rel_vel_x/y/z    | states.rel_vel[0..2]
//   9-11  | roc_ang_vel_x/y/z| states.roc_ang_vel[0..2]
//   12-14 | gx/gy/gz         | states.g[0..2]
//   15    | agl              | states.agl
//   16    | alt_error        | states.alt_error
//   17    | time_remaining   | Python'da hesaplanir
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
    public float los_yaw_sin;
    public float los_yaw_cos;
    public float los_pitch_sin;
    public float los_pitch_cos;

    public float distance;
    public float closing_speed;

    public float[] rel_vel = new float[3];
    public float[] roc_ang_vel = new float[3];
    public float[] g = new float[3];

    public float agl;
    public float alt_error;
    public float grounded_flag;
}

[Serializable]
public class OutgoingPacket
{
    public int episode_id;
    public int step_id;
    public OutgoingStateData states;
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
    public float targetSpeed = 0f;

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

        OutgoingPacket packet = new OutgoingPacket
        {
            episode_id = currentEpisodeId,
            step_id = currentStepId,
            states = CollectState()
        };

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

    private OutgoingStateData CollectState()
    {
        OutgoingStateData s = new OutgoingStateData();

        Vector3 toTargetWorld = targetPoint.position - rocketPoint.position;
        float distance = toTargetWorld.magnitude;
        Vector3 relDirWorld = distance > 1e-6f ? toTargetWorld / distance : Vector3.zero;

        Vector3 targetVelWorld = (targetMoveDir.sqrMagnitude > 1e-6f)
            ? targetMoveDir * targetSpeed
            : Vector3.zero;

        Vector3 relVelWorld = targetVelWorld - rocketRb.linearVelocity;
        Vector3 rocAngVelWorld = rocketRb.angularVelocity;
        Vector3 gravityWorld = Physics.gravity;

        Vector3 relDirUsed = relDirWorld;
        Vector3 relVelUsed = relVelWorld;
        Vector3 rocAngVelUsed = rocAngVelWorld;
        Vector3 gravityUsed = gravityWorld;

        if (useLocalFrame)
        {
            relDirUsed = rocketPoint.InverseTransformDirection(relDirWorld);
            relVelUsed = rocketPoint.InverseTransformDirection(relVelWorld);
            rocAngVelUsed = rocketPoint.InverseTransformDirection(rocAngVelWorld);
            gravityUsed = rocketPoint.InverseTransformDirection(gravityWorld);
        }

        float planarMag = Mathf.Sqrt(relDirUsed.x * relDirUsed.x + relDirUsed.z * relDirUsed.z);
        float losYaw = Mathf.Atan2(relDirUsed.x, relDirUsed.z);
        float losPitch = Mathf.Atan2(relDirUsed.y, Mathf.Max(planarMag, 1e-6f));

        s.los_yaw_sin = Mathf.Sin(losYaw);
        s.los_yaw_cos = Mathf.Cos(losYaw);
        s.los_pitch_sin = Mathf.Sin(losPitch);
        s.los_pitch_cos = Mathf.Cos(losPitch);

        s.distance = distance;
        s.closing_speed = distance > 1e-6f ? -Vector3.Dot(relVelUsed, relDirUsed) : 0f;

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

        return s;
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
