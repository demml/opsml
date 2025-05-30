SELECT 
    space,
    description
FROM opsml_space
WHERE space = $1;