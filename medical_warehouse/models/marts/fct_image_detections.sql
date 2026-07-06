WITH detections AS (
    SELECT * FROM {{ source('raw', 'image_detections') }}
)

SELECT
    MD5(
        channel_name || '-' ||
        message_id::TEXT || '-' ||
        object_label || '-' ||
        confidence::TEXT || '-' ||
        x_min::TEXT || '-' ||
        y_min::TEXT || '-' ||
        x_max::TEXT || '-' ||
        y_max::TEXT
    ) AS detection_key,
    MD5(channel_name || '-' || message_id::TEXT) AS message_key,
    message_id::INT AS message_id,
    MD5(channel_name) AS channel_key,
    object_label,
    confidence::FLOAT AS confidence,
    x_min::FLOAT AS x_min,
    y_min::FLOAT AS y_min,
    x_max::FLOAT AS x_max,
    y_max::FLOAT AS y_max
FROM detections
WHERE message_id IS NOT NULL
