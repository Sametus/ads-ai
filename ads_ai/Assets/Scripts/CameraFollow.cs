using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [Header("Takip Edilecek Obje")]
    public Transform target;

    [Header("Pozisyon Ayarlari")]
    public float distance = 3.5f;
    public float height = 4f;
    public float sideOffset = 2f;

    [Header("Yumusatma")]
    public float positionDamping = 15f;
    public float rotationDamping = 11f;

    [Header("Bakis Ayari")]
    public Vector3 lookOffset = new Vector3(0f, 0f, 0f);

    void LateUpdate()
    {
        if (target == null) return;

        Vector3 desiredPosition =
            target.position
            - target.forward * distance
            + target.up * sideOffset
            + Vector3.up * height;

        transform.position = Vector3.Lerp(
            transform.position,
            desiredPosition,
            Time.deltaTime * positionDamping
        );

        Vector3 lookTarget = target.position + lookOffset;
        Quaternion desiredRotation = Quaternion.LookRotation(lookTarget - transform.position);

        transform.rotation = Quaternion.Slerp(
            transform.rotation,
            desiredRotation,
            Time.deltaTime * rotationDamping
        );
    }
}