UPDATE opsml_user
SET
active = ?,
password_hash = ?,
hashed_recovery_codes = ?,
permissions = ?,
group_permissions = ?,
favorite_spaces = ?,
refresh_token = ?,
email = ?,
authentication_type = ?,
theme_preference = ?,
updated_at = CURRENT_TIMESTAMP
WHERE username = ? and authentication_type = ?;