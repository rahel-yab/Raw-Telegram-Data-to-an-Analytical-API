SELECT DISTINCT
    CAST(message_date AS DATE) AS date_key,
    EXTRACT(YEAR FROM message_date)::INT AS year,
    EXTRACT(MONTH FROM message_date)::INT AS month,
    EXTRACT(DAY FROM message_date)::INT AS day,
    EXTRACT(DOW FROM message_date)::INT AS day_of_week
FROM {{ ref('stg_telegram_messages') }}
WHERE message_date IS NOT NULL
