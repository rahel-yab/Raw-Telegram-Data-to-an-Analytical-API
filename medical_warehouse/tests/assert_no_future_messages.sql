-- Messages should not have a timestamp in the future
SELECT *
FROM {{ ref('fct_messages') }}
WHERE message_date > CURRENT_TIMESTAMP