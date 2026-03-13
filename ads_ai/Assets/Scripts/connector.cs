using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class Connector
{
    private TcpListener listener;
    private TcpClient client;
    private NetworkStream stream;

    private bool waitingForClient = false;

    public bool IsConnected
    {
        get
        {
            return client != null && client.Connected && stream != null;
        }
    }

    public bool HasData
    {
        get
        {
            return stream != null && stream.DataAvailable;
        }
    }

    public bool IsWaitingForClient
    {
        get
        {
            return waitingForClient && !IsConnected;
        }
    }

    public void StartServer(string ip, int port)
    {
        try
        {
            IPAddress ipAddress = IPAddress.Parse(ip);
            listener = new TcpListener(ipAddress, port);
            listener.Start();

            waitingForClient = true;

            Debug.Log($"[Connector] Server baþladý: {ip}:{port}");
            Debug.Log("[Connector] Python baðlantýsý arka planda bekleniyor...");

            _ = AcceptClientAsync();
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] StartServer hatasý: {e.Message}");
            Close();
        }
    }

    private async Task AcceptClientAsync()
    {
        try
        {
            client = await listener.AcceptTcpClientAsync();

            client.NoDelay = true;
            client.ReceiveTimeout = 10000;
            client.SendTimeout = 10000;

            stream = client.GetStream();
            waitingForClient = false;

            Debug.Log("[Connector] Python baðlandý.");
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] AcceptClientAsync hatasý: {e.Message}");
            waitingForClient = false;
            Close();
        }
    }

    public void SendPacket(string json)
    {
        try
        {
            if (!IsConnected)
            {
                Debug.LogWarning("[Connector] SendPacket çaðrýldý ama baðlantý yok.");
                return;
            }

            byte[] payload = Encoding.UTF8.GetBytes(json);
            byte[] header = BitConverter.GetBytes(payload.Length);

            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(header);
            }

            stream.Write(header, 0, header.Length);
            stream.Write(payload, 0, payload.Length);
            stream.Flush();
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] SendPacket hatasý: {e.Message}");
            Close();
        }
    }

    public string ReadPacket()
    {
        try
        {
            if (!IsConnected)
            {
                return null;
            }

            byte[] header = ReadExact(4);
            if (header == null) return null;

            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(header);
            }

            int msgLen = BitConverter.ToInt32(header, 0);

            if (msgLen <= 0 || msgLen > 1024 * 1024)
            {
                Debug.LogError($"[Connector] Geçersiz mesaj uzunluðu: {msgLen}");
                return null;
            }

            byte[] payload = ReadExact(msgLen);
            if (payload == null) return null;

            return Encoding.UTF8.GetString(payload);
        }
        catch (Exception e)
        {
            Debug.LogError($"[Connector] ReadPacket hatasý: {e.Message}");
            Close();
            return null;
        }
    }

    private byte[] ReadExact(int length)
    {
        if (stream == null) return null;

        byte[] buffer = new byte[length];
        int offset = 0;

        while (offset < length)
        {
            int read = stream.Read(buffer, offset, length - offset);

            if (read == 0)
            {
                Debug.LogWarning("[Connector] Karþý taraf baðlantýyý kapattý.");
                return null;
            }

            offset += read;
        }

        return buffer;
    }

    public void Close()
    {
        try { stream?.Close(); } catch { }
        try { client?.Close(); } catch { }
        try { listener?.Stop(); } catch { }

        stream = null;
        client = null;
        listener = null;
        waitingForClient = false;

        Debug.Log("[Connector] Baðlantý kapatýldý.");
    }
}