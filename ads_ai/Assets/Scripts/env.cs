using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public class OutgoingStateData
{
    // C#'taki dizileri doğrudan 3 elemanlı olarak başlatıyoruz ki NullReference yemeyelim.
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

[System.Serializable]
public class OutgoingPacket
{
    public int episode_id;
    public int step_id;
    public OutgoingStateData states;
}

[System.Serializable]
public class IncomingPacket
{
    public int episode_id;
    public int step_id;
    public string type;         // "reset" veya "action"
    public float[] values;      // reset için 5 len (px, py, pz, ry, rz), action için 3 len (thrust, pitch, yaw)
}

/// <summary>
/// Python tarafındaki env.py ile eşleşen, State toplayıp Connector üzerinden yollayan
/// ve Python Agent'dan gelen Action komutlarını alıp çözen genel arayüz (Interface).
/// CombatManager vb. merkez scriptler bu env.cs sınıfını kullanır.
/// </summary>
public class Env : MonoBehaviour
{
    [Header("Network Settings")]
    public string ip = "127.0.0.1";
    public int port = 5050;

    [Header("Simulation References")]
    [Tooltip("Roketin kendi Rigidbody'si")]
    public Rigidbody rocketRb;
    
    [Tooltip("Hedef Uçağın Rigidbody'si")]
    public Rigidbody targetRb;

    [Tooltip("Roketin ucu, hedefi görecek olan 'göz' ve mesafe başlangıcı")]
    public Transform nosePoint;

    [Tooltip("Uçağın merkezi, kilitlenme ve mesafe sonu")]
    public Transform targetPoint;

    [Header("Visual Debugging (Optional)")]
    public LineRenderer distanceLine;
    public LineRenderer forwardLine;
    public float forwardLineLength = 50f;

    [Header("Physics Controls")]
    [Tooltip("RL eğitimini stabilize etmek için Z (Roll) eksenini kilitler")]
    public bool lockRoll = true;

    private float _previousDistance = -1f;

    // --- Başlangıç Durumu Hafızası ---
    private Vector3 initialRocketPos;
    private Quaternion initialRocketRot;

    private Connector connector;
    public bool IsConnected => connector != null && connector.IsConnected;

    void Awake()
    {
        connector = new Connector();
    }

    void Start()
    {
        // Roketin sahnede başladığı ilk yeri kaydet (Episode Reset'te buraya dönecek)
        if (rocketRb != null)
        {
            initialRocketPos = rocketRb.position;
            initialRocketRot = rocketRb.rotation;
        }
    }

    /// <summary>
    /// TCP Sunucuyu başlatır ve Python tarafının env.py ile The Connect olmasını bekler.
    /// Uyarı: Bloklayıcı (blocking) çalışır! Python tarafı "train.py" başlatılana kadar Unity donar.
    /// RL Step-Lock simülasyonları için bu beklenen ve istenen bir durumdur.
    /// </summary>
    public void InitializeConnection()
    {
        Debug.Log($"[Env] RL Simülasyon Arayüzü başlatılıyor. Sunucu adresi: {ip}:{port}");
        // Python bağlanana kadar burada bekler...
        connector.StartServer(ip, port);
    }

    /// <summary>
    /// Roket durumunu (Unity -> Python) yansıtan OutgoingPacket'i JSON'a çevirip yollar.
    /// </summary>
    public void SendState(int episodeId, int stepId, OutgoingStateData stateData)
    {
        if (!IsConnected) return;

        OutgoingPacket packet = new OutgoingPacket
        {
            episode_id = episodeId,
            step_id = stepId,
            states = stateData
        };

        string jsonStr = JsonUtility.ToJson(packet);
        connector.SendPacket(jsonStr);
    }

    /// <summary>
    /// Python'daki env.py algoritmasının beklediği "güdüm / lokalize" (Guidance-Oriented) 
    /// durum uzayını Unity'nin sahip olduğu Transform ve Rigidbody'ler üzerinden hesaplar.
    /// </summary>
    public OutgoingStateData CollectState(float dt, float blendWeight = 1.0f)
    {
        OutgoingStateData s = new OutgoingStateData();

        if (rocketRb == null || targetRb == null || nosePoint == null || targetPoint == null)
        {
            Debug.LogError("[Env] Gerekli referanslar atanmamış! State hesabı yapılamıyor.");
            return s;
        }

        // 1. Mesafe ve Yön (Target_Dir) (Nose'dan Target'a)
        Vector3 toTarget = targetPoint.position - nosePoint.position;
        float currentDistance = toTarget.magnitude;
        Vector3 targetDirWorld = toTarget.normalized;
        
        // ÖNEMLİ: RL için yön, roketin KENDİ EKSENİNE (Local/Nose) göre olmalıdır!
        Vector3 targetDirLocal = nosePoint.InverseTransformDirection(targetDirWorld);
        
        s.target_dir[0] = targetDirLocal.x;
        s.target_dir[1] = targetDirLocal.y;
        s.target_dir[2] = targetDirLocal.z;

        // 2. Göreli Hız (Rel_Vel) : Hedef nereye kayıyor? (Yine Nose'un Local ekseninde)
        Vector3 relVelWorld = targetRb.linearVelocity - rocketRb.linearVelocity;
        Vector3 relVelLocal = nosePoint.InverseTransformDirection(relVelWorld);

        s.rel_vel[0] = relVelLocal.x;
        s.rel_vel[1] = relVelLocal.y;
        s.rel_vel[2] = relVelLocal.z;

        // 3. Roketin Kendi Hızı ve Açısal Hızı (Overshoot engellemek için)
        Vector3 rocVelLocal = nosePoint.InverseTransformDirection(rocketRb.linearVelocity);
        
        s.roc_vel[0] = rocVelLocal.x;
        s.roc_vel[1] = rocVelLocal.y;
        s.roc_vel[2] = rocVelLocal.z;

        Vector3 rocAngVelLocal = nosePoint.InverseTransformDirection(rocketRb.angularVelocity);

        s.roc_ang_vel[0] = rocAngVelLocal.x;
        s.roc_ang_vel[1] = rocAngVelLocal.y;
        s.roc_ang_vel[2] = rocAngVelLocal.z;

        // 4. İrtifalar (Çarpışma/Ödül mantığı için global Y ekseni)
        s.roc_h = rocketRb.position.y;
        s.target_h = targetRb.position.y;

        // 5. Yerçekimi İzdüşümü (Gövde Up/Down yönelimi algısı için)
        Vector3 gravityLocal = nosePoint.InverseTransformDirection(Physics.gravity);

        s.g[0] = gravityLocal.x;
        s.g[1] = gravityLocal.y;
        s.g[2] = gravityLocal.z;

        // 6. Mesafe ve Kapanma Oranı (Delta Time üzerinden türev)
        s.distance = currentDistance;

        if (_previousDistance < 0f) _previousDistance = currentDistance; // İlk frame inşası
        
        // closing_rate: hedefe ne hızla yaklaşıyoruz? (pozitif hız, yaklaşıyoruz demektir)
        float distanceDelta = _previousDistance - currentDistance;
        s.closing_rate = (dt > 0f) ? (distanceDelta / dt) : 0f;
        
        _previousDistance = currentDistance;

        // 7. Blend Weight (Fırlatmadan yatay takibe geçiş oranı)
        s.blend_w = blendWeight;

        return s;
    }

    /// <summary>
    /// RL ajanından gelen (Python -> Unity) aksiyon veya reset paketini alır ve C# nesnesine (IncomingPacket) çizer.
    /// </summary>
    public IncomingPacket ReceiveAction()
    {
        if (!IsConnected) return null;

        string jsonResponse = connector.ReadPacket();
        if (string.IsNullOrEmpty(jsonResponse)) return null;

        try
        {
            return JsonUtility.FromJson<IncomingPacket>(jsonResponse);
        }
        catch (System.Exception e)
        {
            Debug.LogError($"[Env] JSON Parse Hatası (ReceiveAction): {e.Message}");
            return null;
        }
    }

    /// <summary>
    /// Unity Fiziğinin çalıştığı her adımda çağrılarak hem vizüalizasyonları günceller
    /// hem de istenirse fiziksel Roll (Z ekseni döndürme) kilidini sağlar.
    /// </summary>
    public void UpdatePhysicsAndVisuals()
    {
        if (rocketRb == null || targetRb == null || nosePoint == null || targetPoint == null) return;

        // --- 1. Roll (Kendi Ekseninde Dönme) Kilidi ---
        if (lockRoll)
        {
            // Roketin mevcut rotasyonunu Euler açısı olarak alıyoruz
            Vector3 currentEuler = rocketRb.rotation.eulerAngles;
            // Roll (Z) eksenini sıfırlıyoruz. (X ve Y serbeste kalsın)
            Quaternion rollLockedRot = Quaternion.Euler(currentEuler.x, currentEuler.y, 0f);
            
            // Fiziksel olarak Rigidbody'i stabil hale zorla
            rocketRb.MoveRotation(rollLockedRot);
            
            // Ayrıca angularVelocity'de oluşmuş Z torkunu sönümle (sıfırla)
            Vector3 localAngVel = nosePoint.InverseTransformDirection(rocketRb.angularVelocity);
            localAngVel.z = 0f;
            rocketRb.angularVelocity = nosePoint.TransformDirection(localAngVel);
        }

        // --- 2. Görsel Çizgiler (Debug Lines) ---
        if (distanceLine != null)
        {
            distanceLine.SetPosition(0, nosePoint.position);
            distanceLine.SetPosition(1, targetPoint.position);
        }

        if (forwardLine != null)
        {
            forwardLine.SetPosition(0, nosePoint.position);
            forwardLine.SetPosition(1, nosePoint.position + (nosePoint.forward * forwardLineLength));
        }
    }

    /// <summary>
    /// Agent'dan bölüm sonu veya başlangıcı geldiğinde roketin 
    /// uzaysal konumunu sahnede ilk doğduğu yere (launchpad vb.) geri ışınlar.
    /// </summary>
    public void ResetRocketToInitialState()
    {
        if (rocketRb == null) return;

        // Fiziği durdur
        rocketRb.linearVelocity = Vector3.zero;
        rocketRb.angularVelocity = Vector3.zero;

        // Pozisyonu zorla
        rocketRb.position = initialRocketPos;
        rocketRb.rotation = initialRocketRot;
        
        // Önceki mesafe hesabını sıfırla ki closing_rate sapıtmasın
        _previousDistance = -1f;
    }

    private void OnApplicationQuit()
    {
        if (connector != null)
        {
            connector.Close();
        }
    }

    private void OnDestroy()
    {
        if (connector != null)
        {
            connector.Close();
        }
    }
}
