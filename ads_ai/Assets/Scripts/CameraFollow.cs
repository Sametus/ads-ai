using UnityEngine;

public class CameraFollow : MonoBehaviour
{
    [Header("Takip Edilecek Obje")]
    public Transform target;

    [Header("Dunya Sabit Kamera Offset")]
    public float distance = 18f;
    public float height = 10f;
    public float sideOffset = -18f;

    [Header("Bakis Ayari")]
    public Vector3 lookOffset = new Vector3(0f, 1.5f, 0f);

    [Header("Gorsel Yumusatma")]
    public float positionSmoothTime = 0.025f;
    public float lookSmoothTime = 0.06f;
    public float rotationSharpness = 18f;

    [Header("Hizli Yakalama")]
    public float catchUpDistance = 2f;
    public float fastPositionSmoothTime = 0.008f;
    public float snapDistance = 8f;

    [Header("Kadraji Koru")]
    public bool dynamicZoom = true;
    public float baseFieldOfView = 46f;
    public float fastFieldOfView = 62f;
    public float zoomSpeedForFastFov = 110f;
    public float baseOrthographicSize = 10f;
    public float fastOrthographicSize = 18f;
    public float zoomSmoothTime = 0.12f;

    private Vector3 positionVelocity = Vector3.zero;
    private Vector3 lookVelocity = Vector3.zero;
    private Vector3 smoothedLookTarget = Vector3.zero;
    private Vector3 previousTargetPosition = Vector3.zero;
    private float zoomVelocity = 0f;
    private Camera cachedCamera;
    private bool initialized = false;

    private void Awake()
    {
        cachedCamera = GetComponent<Camera>();
    }

    private void LateUpdate()
    {
        if (target == null) return;

        Vector3 targetPosition = target.position;
        Vector3 targetVelocity = Vector3.zero;
        if (initialized && Time.deltaTime > 1e-5f)
            targetVelocity = (targetPosition - previousTargetPosition) / Time.deltaTime;

        if (!initialized)
        {
            initialized = true;
            smoothedLookTarget = targetPosition + lookOffset;
            transform.position = BuildDesiredPosition(targetPosition);
        }

        previousTargetPosition = targetPosition;

        Vector3 desiredPosition = BuildDesiredPosition(targetPosition);
        float positionLag = Vector3.Distance(transform.position, desiredPosition);
        float catchUpSmoothTime = positionLag > Mathf.Max(0f, catchUpDistance)
            ? Mathf.Min(positionSmoothTime, fastPositionSmoothTime)
            : positionSmoothTime;

        if (positionLag > Mathf.Max(catchUpDistance, snapDistance))
        {
            transform.position = desiredPosition;
            positionVelocity = Vector3.zero;
        }
        else
        {
            transform.position = Vector3.SmoothDamp(
                transform.position,
                desiredPosition,
                ref positionVelocity,
                Mathf.Max(0.001f, catchUpSmoothTime)
            );
        }

        smoothedLookTarget = Vector3.SmoothDamp(
            smoothedLookTarget,
            targetPosition + lookOffset,
            ref lookVelocity,
            Mathf.Max(0.001f, lookSmoothTime)
        );

        Vector3 lookDirection = smoothedLookTarget - transform.position;
        if (lookDirection.sqrMagnitude <= 1e-8f) return;

        Quaternion desiredRotation = Quaternion.LookRotation(lookDirection.normalized, Vector3.up);
        float rotationBlend = 1f - Mathf.Exp(-Mathf.Max(0f, rotationSharpness) * Time.deltaTime);
        transform.rotation = Quaternion.Slerp(transform.rotation, desiredRotation, rotationBlend);

        UpdateZoom(targetVelocity.magnitude);
    }

    private Vector3 BuildDesiredPosition(Vector3 anchorPosition)
    {
        Vector3 desiredPosition = anchorPosition + new Vector3(sideOffset, height, -distance);

        return desiredPosition;
    }

    private void UpdateZoom(float targetSpeed)
    {
        if (!dynamicZoom || cachedCamera == null)
            return;

        float speedT = Mathf.Clamp01(targetSpeed / Mathf.Max(1f, zoomSpeedForFastFov));

        if (cachedCamera.orthographic)
        {
            float desiredSize = Mathf.Lerp(baseOrthographicSize, fastOrthographicSize, speedT);
            cachedCamera.orthographicSize = Mathf.SmoothDamp(
                cachedCamera.orthographicSize,
                desiredSize,
                ref zoomVelocity,
                Mathf.Max(0.001f, zoomSmoothTime)
            );
        }
        else
        {
            float desiredFov = Mathf.Lerp(baseFieldOfView, fastFieldOfView, speedT);
            cachedCamera.fieldOfView = Mathf.SmoothDamp(
                cachedCamera.fieldOfView,
                desiredFov,
                ref zoomVelocity,
                Mathf.Max(0.001f, zoomSmoothTime)
            );
        }
    }
}
