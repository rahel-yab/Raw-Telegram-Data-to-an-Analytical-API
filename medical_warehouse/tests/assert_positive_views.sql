-- View counts cannot be less than zero
SELECT *
FROM {{ ref('fct_messages') }}
WHERE view_count < 0