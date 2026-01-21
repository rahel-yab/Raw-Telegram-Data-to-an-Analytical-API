SELECT
    MD5(channel_name) AS channel_key, -- Simple surrogate key
    channel_name,
    COUNT(*) AS total_posts,
    MIN(message_date) AS first_post_date,
    MAX(message_date) AS last_post_date
FROM {{ ref('stg_telegram_messages') }}
GROUP BY 1, 2