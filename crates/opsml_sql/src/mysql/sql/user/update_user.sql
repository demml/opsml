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
updated_at = CURRENT_TIMESTAMP
WHERE username = ?;