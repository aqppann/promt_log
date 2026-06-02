-- 1. Збережена процедура
CREATE OR REPLACE FUNCTION create_prompt_version()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO prompt_versions (prompt_id, version_number, content, change_note, created_at)
    VALUES (
        OLD.id,
        (SELECT COALESCE(MAX(version_number), 0) + 1
         FROM prompt_versions
         WHERE prompt_id = OLD.id),
        OLD.content,
        'Auto-saved before update',
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Тригер
CREATE OR REPLACE TRIGGER prompt_version_trigger
BEFORE UPDATE OF content ON prompts
FOR EACH ROW
WHEN (OLD.content IS DISTINCT FROM NEW.content)
EXECUTE FUNCTION create_prompt_version();