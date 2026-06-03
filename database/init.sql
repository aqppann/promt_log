-- 1. Тригерна функція — автоматично зберігає стару версію при оновленні
CREATE OR REPLACE FUNCTION create_prompt_version()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.content IS DISTINCT FROM NEW.content THEN
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
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Тригер — спрацьовує перед оновленням промпту
CREATE OR REPLACE TRIGGER prompt_version_trigger
BEFORE UPDATE ON prompts
FOR EACH ROW
EXECUTE FUNCTION create_prompt_version();

-- 3. Збережена процедура — повертає найновішу версію промпту
CREATE OR REPLACE FUNCTION get_best_version(p_id INTEGER)
RETURNS TABLE(
    version_number INT,
    content TEXT,
    change_note VARCHAR,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pv.version_number,
        pv.content,
        pv.change_note,
        pv.created_at
    FROM prompt_versions pv
    WHERE pv.prompt_id = p_id
    ORDER BY pv.version_number DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;