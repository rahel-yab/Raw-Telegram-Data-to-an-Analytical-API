SELECT
    message_id,
    MD5(channel_name) AS channel_key,
    message_date,
    message_text,
    message_length,
    view_count,
    forward_count,
    has_image
FROM {{ ref('stg_telegram_messages') }}