using System;
using UnityEngine;

[Serializable]
public class IncomingPacket
{
    public int episode_id;
    public int step_id;
    public string type;     // "reset" veya "action"
    public float[] values;  // reset: [px, py, pz, ry, rz] | action: [thrust, pitch, yaw]
}

[Serializable]
public class OutgoingStateData
{
    public float[] target_dir = new float[3];
    public float[] rel_vel = new float[3];
    public float[] roc_vel = new float[3];
    public float[] roc_ang_vel = new float[3];

    public float roc_h;
    public float target_h;

    public float[] g = new float[3];

    public float distance;
    public float closing_rate;
    public float blend_w;
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

    [Header("Scene References (Sürükle-Bırak)")]
    public Transform rocket;
    public Transform rocketPoint;
    public Transform target;
    public Transform targetPoint;

    [Header("Rigidbodies (Sürükle-Bırak, boşsa otomatik aranır)")]
    public Rigidbody rocketRb;
    public Rigidbody targetRb;

    [Header("Debug Lines (Opsiyonel)")]
    public LineRenderer distanceLine;
    public LineRenderer forwardLine;
    public float forwardLineLength = 20f;

    [Header("Particle FX (Opsiyonel)")]
    public ParticleSystem rocketExhaustFx;
    public ParticleSystem targetExhaustFx;

    [Header("Rocket Reset Pose")]
    public Vector3 rocketResetPosition = new Vector3(-0.492f, 2.5f, 0.022f);
    public Vector3 rocketResetEuler = new Vector3(-90f, 0f, 0f);

    [Header("Action Scales")]
    public float thrustScale = 1f;
    public float torqueScale = 1f;

    [Header("State Options")]
    public bool useLocalFrame = true;
    public float blendW = 0f;

    [Header("Target Reset Constraints")]
    public bool keepTargetYFixed = true;
    public bool keepTargetRotXFixed = true;

    [Header("Target Motion")]
    public float targetSpeed = 25f;
    public bool moveTargetOnlyAfterReset = true;

    private Connector connector;

    private int currentEpisodeId = 0;
    private int currentStepId = 0;

    private float currentThrust = 0f;
    private float currentPitch = 0f;
    private float currentYaw = 0f;

    private bool pendingAction = false;
    private bool targetMotionEnabled = false;

    private float prevDistance = -1f;

    private float fixedTargetY;
    private float fixedTargetRotX;

    // Target için sabit yatay hareket yönü
    private Vector3 targetMoveDir = Vector3.zero;

    private void Start()
    {
        ValidateAndBindReferences();

        fixedTargetY = target.position.y;
        fixedTargetRotX = target.eulerAngles.x;

        targetMotionEnabled = !moveTargetOnlyAfterReset;

        connector = new Connector();
        connector.StartServer(ip, port);

        prevDistance = Vector3.Distance(rocketPoint.position, targetPoint.position);

        // Target exhaust başlat
        if (targetExhaustFx != null && !targetExhaustFx.isPlaying)
        {
            targetExhaustFx.Play();
        }

        // Rocket exhaust başlangıçta kapalı olsun
        if (rocketExhaustFx != null && rocketExhaustFx.isPlaying)
        {
            rocketExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
        }

        Debug.Log($"[Env] Başladı | fixedTargetY={fixedTargetY:F2} | fixedTargetRotX={fixedTargetRotX:F2}");
    }

    private void Update()
    {
        UpdateDebugLines();
        UpdateParticleFX();

        if (connector == null) return;
        if (!connector.IsConnected) return;
        if (!connector.HasData) return;

        string jsonMsg = connector.ReadPacket();

        if (!string.IsNullOrEmpty(jsonMsg))
        {
            ProcessIncomingPacket(jsonMsg);
        }
    }

    private void FixedUpdate()
    {
        if (targetMotionEnabled)
        {
            MoveTarget();
        }

        if (!pendingAction) return;
        if (rocketRb == null) return;

        ApplyAction();
        SendStateToPython();

        pendingAction = false;
    }

    private void ValidateAndBindReferences()
    {
        if (rocket == null || rocketPoint == null || target == null || targetPoint == null)
        {
            Debug.LogError("[Env] Transform referansları eksik. Inspector'da rocket, rocketPoint, target, targetPoint atanmalı.");
            enabled = false;
            return;
        }

        if (rocketRb == null)
        {
            rocketRb = rocket.GetComponent<Rigidbody>();
        }

        if (targetRb == null && target != null)
        {
            targetRb = target.GetComponent<Rigidbody>();
        }

        if (rocketRb == null)
        {
            Debug.LogError("[Env] Rocket Rigidbody bulunamadı.");
            enabled = false;
            return;
        }
    }

    private void ProcessIncomingPacket(string jsonMsg)
    {
        Debug.Log("[Env] Gelen JSON: " + jsonMsg);

        IncomingPacket packet = null;

        try
        {
            packet = JsonUtility.FromJson<IncomingPacket>(jsonMsg);
        }
        catch (Exception e)
        {
            Debug.LogError("[Env] JSON parse hatası: " + e.Message);
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
                Debug.LogError("[Env] Reset paketi geçersiz. 5 elemanlı values bekleniyor.");
                return;
            }

            ResetEnvironment(packet.values);
            SendStateToPython();
        }
        else if (packet.type == "action")
        {
            if (packet.values == null || packet.values.Length < 3)
            {
                Debug.LogError("[Env] Action paketi geçersiz. 3 elemanlı values bekleniyor.");
                return;
            }

            ReadAction(packet.values);
            pendingAction = true;
        }
        else
        {
            Debug.LogWarning("[Env] Bilinmeyen packet.type: " + packet.type);
        }
    }

    private void ReadAction(float[] actionValues)
    {
        currentThrust = actionValues[0];
        currentPitch = actionValues[1];
        currentYaw = actionValues[2];
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

        // Target script-driven ilerlesin
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

        target.position = new Vector3(targetPosX, targetPosY, targetPosZ);
        target.eulerAngles = new Vector3(targetRotX, targetRotY, targetRotZ);

        if (targetRb != null)
        {
            targetRb.linearVelocity = Vector3.zero;
            targetRb.angularVelocity = Vector3.zero;
        }

        rocketRb.linearVelocity = Vector3.zero;
        rocketRb.angularVelocity = Vector3.zero;

        rocketRb.position = rocketResetPosition;
        rocketRb.rotation = Quaternion.Euler(rocketResetEuler);

        currentThrust = 0f;
        currentPitch = 0f;
        currentYaw = 0f;
        pendingAction = false;
        targetMotionEnabled = true;

        // HEADING PYTHON'DA RZ İLE TAŞINIYOR -> hareket yönünü Z rotasyonundan üret
        float headingRad = targetRotZ * Mathf.Deg2Rad;
        targetMoveDir = new Vector3(-Mathf.Sin(headingRad), 0f, -Mathf.Cos(headingRad)).normalized;

        prevDistance = Vector3.Distance(rocketPoint.position, targetPoint.position);

        // Reset sonrası rocket exhaust kapat
        if (rocketExhaustFx != null)
        {
            rocketExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
        }

        // Reset sonrası target exhaust yeniden başlat
        if (targetExhaustFx != null)
        {
            targetExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            targetExhaustFx.Play();
        }

        Debug.Log(
            $"[Env] RESET uygulandı | " +
            $"Target Pos=({target.position.x:F2}, {target.position.y:F2}, {target.position.z:F2}) | " +
            $"Target Rot=({target.eulerAngles.x:F2}, {target.eulerAngles.y:F2}, {target.eulerAngles.z:F2}) | " +
            $"MoveDir=({targetMoveDir.x:F2}, {targetMoveDir.y:F2}, {targetMoveDir.z:F2})"
        );
    }

    private void SendStateToPython()
    {
        if (connector == null || !connector.IsConnected)
        {
            Debug.LogWarning("[Env] State gönderilemedi. Connector bağlı değil.");
            return;
        }

        OutgoingStateData stateData = CollectState();

        OutgoingPacket packet = new OutgoingPacket
        {
            episode_id = currentEpisodeId,
            step_id = currentStepId,
            states = stateData
        };

        string jsonOutput = JsonUtility.ToJson(packet);
        connector.SendPacket(jsonOutput);
    }

    private OutgoingStateData CollectState()
    {
        OutgoingStateData s = new OutgoingStateData();

        Vector3 toTarget = targetPoint.position - rocketPoint.position;
        float distance = toTarget.magnitude;

        Vector3 targetDirWorld = distance > 1e-6f ? toTarget / distance : Vector3.zero;

        Vector3 targetVelWorld = Vector3.zero;
        if (targetMoveDir.sqrMagnitude > 1e-6f)
        {
            targetVelWorld = targetMoveDir * targetSpeed;
        }

        Vector3 relVelWorld = targetVelWorld - rocketRb.linearVelocity;
        Vector3 rocVelWorld = rocketRb.linearVelocity;
        Vector3 rocAngVelWorld = rocketRb.angularVelocity;
        Vector3 gravityWorld = Physics.gravity;

        Vector3 targetDirUsed = targetDirWorld;
        Vector3 relVelUsed = relVelWorld;
        Vector3 rocVelUsed = rocVelWorld;
        Vector3 rocAngVelUsed = rocAngVelWorld;
        Vector3 gravityUsed = gravityWorld;

        if (useLocalFrame)
        {
            targetDirUsed = rocketPoint.InverseTransformDirection(targetDirWorld);
            relVelUsed = rocketPoint.InverseTransformDirection(relVelWorld);
            rocVelUsed = rocketPoint.InverseTransformDirection(rocVelWorld);
            rocAngVelUsed = rocketPoint.InverseTransformDirection(rocAngVelWorld);
            gravityUsed = rocketPoint.InverseTransformDirection(gravityWorld);
        }

        s.target_dir[0] = targetDirUsed.x;
        s.target_dir[1] = targetDirUsed.y;
        s.target_dir[2] = targetDirUsed.z;

        s.rel_vel[0] = relVelUsed.x;
        s.rel_vel[1] = relVelUsed.y;
        s.rel_vel[2] = relVelUsed.z;

        s.roc_vel[0] = rocVelUsed.x;
        s.roc_vel[1] = rocVelUsed.y;
        s.roc_vel[2] = rocVelUsed.z;

        s.roc_ang_vel[0] = rocAngVelUsed.x;
        s.roc_ang_vel[1] = rocAngVelUsed.y;
        s.roc_ang_vel[2] = rocAngVelUsed.z;

        s.roc_h = rocketPoint.position.y;
        s.target_h = targetPoint.position.y;

        s.g[0] = gravityUsed.x;
        s.g[1] = gravityUsed.y;
        s.g[2] = gravityUsed.z;

        s.distance = distance;

        if (prevDistance < 0f)
        {
            prevDistance = distance;
        }

        s.closing_rate = (prevDistance - distance) / Mathf.Max(Time.fixedDeltaTime, 1e-6f);
        s.blend_w = blendW;

        prevDistance = distance;

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
            forwardLine.SetPosition(1, rocketPoint.position + rocket.forward * forwardLineLength);
        }
    }

    private void UpdateParticleFX()
    {
        if (rocketExhaustFx != null)
        {
            if (currentThrust > 0.1f)
            {
                if (!rocketExhaustFx.isPlaying)
                {
                    rocketExhaustFx.Play();
                }
            }
            else
            {
                if (rocketExhaustFx.isPlaying)
                {
                    rocketExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmitting);
                }
            }
        }

        if (targetExhaustFx != null)
        {
            if (targetMotionEnabled)
            {
                if (!targetExhaustFx.isPlaying)
                {
                    targetExhaustFx.Play();
                }
            }
            else
            {
                if (targetExhaustFx.isPlaying)
                {
                    targetExhaustFx.Stop(true, ParticleSystemStopBehavior.StopEmitting);
                }
            }
        }
    }

    private void OnApplicationQuit()
    {
        connector?.Close();
    }

    private void OnDestroy()
    {
        connector?.Close();
    }
}