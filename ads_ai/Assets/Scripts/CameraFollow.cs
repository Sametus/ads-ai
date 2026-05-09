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

    [Header("Gorsel Yumusatma")]
    public float positionSmoothTime = 0.035f;
    public float lookSmoothTime = 0.04f;
    public float basisSmoothTime = 0.10f;
    public float rotationSharpness = 36f;

    [Header("Hizli Yakalama")]
    public float lookAheadTime = 0.04f;
    public float maxLookAheadDistance = 4f;
    public float catchUpDistance = 1.5f;
    public float fastPositionSmoothTime = 0.012f;
    public float snapDistance = 8f;

    private Vector3 positionVelocity = Vector3.zero;
    private Vector3 lookVelocity = Vector3.zero;
    private Vector3 forwardVelocity = Vector3.zero;
    private Vector3 upVelocity = Vector3.zero;
    private Vector3 smoothedLookTarget = Vector3.zero;
    private Vector3 smoothedForward = Vector3.forward;
    private Vector3 smoothedUp = Vector3.up;
    private Vector3 previousTargetPosition = Vector3.zero;
    private bool initialized = false;

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
            smoothedForward = target.forward;
            smoothedUp = target.up;
            smoothedLookTarget = targetPosition + lookOffset;
            transform.position = BuildDesiredPosition(targetPosition, smoothedForward, smoothedUp);
        }

        previousTargetPosition = targetPosition;

        Vector3 lookAheadOffset = Vector3.ClampMagnitude(
            targetVelocity * Mathf.Max(0f, lookAheadTime),
            Mathf.Max(0f, maxLookAheadDistance)
        );
        Vector3 followPosition = targetPosition + lookAheadOffset;

        smoothedForward = Vector3.SmoothDamp(
            smoothedForward,
            target.forward,
            ref forwardVelocity,
            Mathf.Max(0.001f, basisSmoothTime)
        ).normalized;

        smoothedUp = Vector3.SmoothDamp(
            smoothedUp,
            target.up,
            ref upVelocity,
            Mathf.Max(0.001f, basisSmoothTime)
        ).normalized;

        Vector3 desiredPosition = BuildDesiredPosition(followPosition, smoothedForward, smoothedUp);
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
            followPosition + lookOffset,
            ref lookVelocity,
            Mathf.Max(0.001f, lookSmoothTime)
        );

        Vector3 lookDirection = smoothedLookTarget - transform.position;
        if (lookDirection.sqrMagnitude <= 1e-8f) return;

        Quaternion desiredRotation = Quaternion.LookRotation(lookDirection.normalized, Vector3.up);
        float rotationBlend = 1f - Mathf.Exp(-Mathf.Max(0f, rotationSharpness) * Time.deltaTime);
        transform.rotation = Quaternion.Slerp(transform.rotation, desiredRotation, rotationBlend);
    }

    private Vector3 BuildDesiredPosition(Vector3 anchorPosition, Vector3 followForward, Vector3 followUp)
    {
        Vector3 desiredPosition =
            anchorPosition
            - followForward * distance
            + followUp * sideOffset
            + Vector3.up * height;

        return desiredPosition;
    }
}
