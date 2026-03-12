using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

/// <summary>
/// Python (RL Agent) tarafındaki connector.py ile %100 uyumlu (Big-Endian JSON Framing) 
/// TCP Sunucu (Server) sınıfıdır. Unity tarafı sunucu rolünü, Python tarafı istemci (client) rolünü üstlenir.
/// </summary>
public class Connector
{
    private TcpListener listener;
    private TcpClient client;
    private NetworkStream stream;
    
    public bool IsConnected => client != null && client.Connected;

    public void StartServer(string ip, int port)
    {
        try
        {
            IPAddress localAddr = IPAddress.Parse(ip);
            listener = new TcpListener(localAddr, port);
            listener.Start();
            Debug.Log($"[Connector] TCP Server başlatıldı. {ip}:{port} üzerinde Python ajanı bekleniyor...");
            
            // Unity ana thread'ini meşgul etmemek için asenkron dinleme eklenebilir ancak
            // RL eğitim döngüsü (step-lock) için senkron kabul edilebilir.
            // AcceptTcpClient bloklayıcıdır, Python bağlanana kadar Unity donar.
            client = listener.AcceptTcpClient();
            client.NoDelay = true; // Python tarafındaki TCP_NODELAY eşleşmesi
            
            stream = client.GetStream();
            Debug.Log("[Connector] Python İstemcisi başarıyla bağlandı!");
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] Sunucu başlatma hatası: {e.Message}");
        }
    }

    /// <summary>
    /// Python tarafına 4-byte uzunluk başlığı (Big-Endian) ile JSON verisini gönderir.
    /// </summary>
    public void SendPacket(string jsonStr)
    {
        if (!IsConnected)
        {
            Debug.LogWarning("[Connector] Bağlantı yok, paket gönderilemedi.");
            return;
        }

        try
        {
            byte[] payload = Encoding.UTF8.GetBytes(jsonStr);
            
            // 4-byte Header (Uzunluk) oluşturma
            int payloadLength = payload.Length;
            byte[] header = BitConverter.GetBytes(payloadLength);
            
            // Python >I (Big-Endian) formatına uyum sağlama (Windows Little-Endian çalışır, ters çeviririz)
            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(header);
            }

            // TCP Akışına başlığı ve mesajı yazma
            stream.Write(header, 0, header.Length);
            stream.Write(payload, 0, payload.Length);
            stream.Flush();
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] Paket gönderme hatası: {e.Message}");
            Close();
        }
    }

    /// <summary>
    /// Python'dan gelen 4-byte uzunluk başlığını okuyup tam olarak mesaj gövdesini alır ve string olarak döndürür.
    /// </summary>
    public string ReadPacket()
    {
        if (!IsConnected) return null;

        try
        {
            // 1. Önce 4 baytlık başlığı (uzunluk bilgisini) oku
            byte[] header = ReadExact(4);
            if (header == null) return null;

            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(header);
            }
            int msgLen = BitConverter.ToInt32(header, 0);

            // 2. Belirtilen uzunluk kadar mesaj gövdesini oku
            byte[] payload = ReadExact(msgLen);
            if (payload == null) return null;

            return Encoding.UTF8.GetString(payload);
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] Paket okuma hatası: {e.Message}");
            Close();
            return null;
        }
    }

    /// <summary>
    /// Ağ üzerinden tam n byte gelene kadar bekleyerek eksiksiz okuma yapar. (Python _recv_exact eşdeğeri)
    /// </summary>
    private byte[] ReadExact(int length)
    {
        byte[] buffer = new byte[length];
        int received = 0;
        
        while (received < length)
        {
            int read = stream.Read(buffer, received, length - received);
            
            if (read == 0) // Eğer 0 dönüyorsa bağlantı kopmuştur
            {
                Debug.LogWarning("[Connector] Karşı tarafla bağlantı koptu.");
                Close();
                return null;
            }
            
            received += read;
        }
        
        return buffer;
    }

    /// <summary>
    /// Bağlantıyı temiz bir şekilde sonlandırır.
    /// </summary>
    public void Close()
    {
        if (stream != null)
        {
            stream.Close();
            stream = null;
        }
        if (client != null)
        {
            client.Close();
            client = null;
        }
        if (listener != null)
        {
            listener.Stop();
            listener = null;
        }
        Debug.Log("[Connector] Soket bağlantıları kapatıldı.");
    }
}
