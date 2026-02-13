INSERT INTO opsml_prompt_registry (
    uid,
    app_env,
    name,
    space,
    major,
    minor,
    patch,
    version,
    tags,
    experimentcard_uid,
    auditcard_uid,
    pre_tag,
    build_tag,
    username,
    opsml_version,
    content_hash
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16);