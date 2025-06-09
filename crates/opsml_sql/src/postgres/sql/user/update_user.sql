UPDATE opsml_user
SET
active = $1, 
password_hash = $2, 
hashed_recovery_codes = $3,
permissions = $4, 
group_permissions = $5,
favorite_spaces = $6,
refresh_token = $7,
email = $8,
authentication_type = $9,
updated_at = CURRENT_TIMESTAMP
WHERE username = $10 and authentication_type = $9;