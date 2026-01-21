WITH raw_data AS (
    SELECT * FROM {{ source('raw', 'telegram_messages') }}
)

SELECT
    -- Convert IDs and handle potential nulls
    message_id::INT AS message_id,
    channel_name,
    
    -- Cast string dates to proper TIMESTAMPS
    message_date::TIMESTAMP AS message_date,
    
    -- Clean text content
    TRIM(message_text) AS message_text,
    LENGTH(message_text) AS message_length,
    
    -- Metrics with default values
    COALESCE(views, 0) AS view_count,
    COALESCE(forwards, 0) AS forward_count,
    
    -- Boolean flag for media
    COALESCE(has_media, FALSE) AS has_image

FROM raw_data
WHERE message_id IS NOT NULL