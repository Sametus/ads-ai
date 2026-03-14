using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [Header("Takip Edilecek Obje")]
    public Transform target;

    [Header("Pozisyon Ayarlari")]
    public float distance = 3.5f;
    public float height = 4f;
    public float sideOffset = 2f;

    [Header("Bakis Ayari")]
    public Vector3 lookOffset = Vector3.zero;

    void LateUpdate()
    {
        if (target == null) return;

        Vector3 desiredPosition =
            target.position
            - target.forward * distance
            + target.up * sideOffset
            + Vector3.up * height;

        transform.position = desiredPosition;

        Vector3 lookTarget = target.position + lookOffset;
        transform.rotation = Quaternion.LookRotation(lookTarget - transform.position);
    }
}