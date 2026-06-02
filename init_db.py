import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def init():
    db_url = os.getenv('DATABASE_URL')
    print(f"Connecting to database: {db_url}")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Drop tables to start fresh
    print("Dropping tables...")
    cur.execute("DROP TABLE IF EXISTS prompt_audit_log CASCADE;")
    cur.execute("DROP TABLE IF EXISTS prompt_versions CASCADE;")
    cur.execute("DROP TABLE IF EXISTS prompts CASCADE;")
    
    # Create tables
    print("Creating tables...")
    cur.execute("""
    CREATE TABLE prompts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        category VARCHAR(50) NOT NULL CHECK (category IN ('debugging', 'refactoring', 'docs', 'testing', 'other')),
        target_model VARCHAR(50) NOT NULL CHECK (target_model IN ('gpt-4', 'claude', 'gemini')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cur.execute("""
    CREATE TABLE prompt_versions (
        id SERIAL PRIMARY KEY,
        prompt_id INTEGER REFERENCES prompts(id) ON DELETE CASCADE,
        version_number INTEGER,
        content TEXT NOT NULL,
        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
        ai_feedback TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cur.execute("""
    CREATE TABLE prompt_audit_log (
        id SERIAL PRIMARY KEY,
        prompt_id INTEGER,
        action VARCHAR(50) NOT NULL CHECK (action IN ('created', 'version_added', 'rated')),
        happened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create functions and triggers
    print("Creating functions and triggers...")
    
    # Version number trigger function
    cur.execute("""
    CREATE OR REPLACE FUNCTION set_prompt_version_number()
    RETURNS TRIGGER AS $$
    DECLARE
        next_ver INT;
    BEGIN
        SELECT COALESCE(MAX(version_number), 0) + 1 INTO next_ver
        FROM prompt_versions
        WHERE prompt_id = NEW.prompt_id;
        
        NEW.version_number := next_ver;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Audit log trigger function
    cur.execute("""
    CREATE OR REPLACE FUNCTION log_prompt_action()
    RETURNS TRIGGER AS $$
    BEGIN
        IF TG_OP = 'INSERT' THEN
            IF NEW.version_number = 1 THEN
                INSERT INTO prompt_audit_log (prompt_id, action, happened_at)
                VALUES (NEW.prompt_id, 'created', CURRENT_TIMESTAMP);
            ELSE
                INSERT INTO prompt_audit_log (prompt_id, action, happened_at)
                VALUES (NEW.prompt_id, 'version_added', CURRENT_TIMESTAMP);
            END IF;
        ELSIF TG_OP = 'UPDATE' THEN
            IF OLD.rating IS DISTINCT FROM NEW.rating THEN
                INSERT INTO prompt_audit_log (prompt_id, action, happened_at)
                VALUES (NEW.prompt_id, 'rated', CURRENT_TIMESTAMP);
            END IF;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    # Create triggers
    cur.execute("""
    CREATE TRIGGER trigger_set_version_number
    BEFORE INSERT ON prompt_versions
    FOR EACH ROW
    EXECUTE FUNCTION set_prompt_version_number();
    """)
    
    cur.execute("""
    CREATE TRIGGER trigger_log_prompt_action
    AFTER INSERT OR UPDATE ON prompt_versions
    FOR EACH ROW
    EXECUTE FUNCTION log_prompt_action();
    """)
    
    # Create stored procedure (function)
    print("Creating stored function...")
    cur.execute("""
    CREATE OR REPLACE FUNCTION get_best_prompt_version(p_id INT)
    RETURNS SETOF prompt_versions AS $$
    BEGIN
        RETURN QUERY
        SELECT * FROM prompt_versions
        WHERE prompt_id = p_id
        ORDER BY rating DESC NULLS LAST, version_number DESC
        LIMIT 1;
    END;
    $$ LANGUAGE plpgsql;
    """)
    
    conn.commit()
    print("Database initialized successfully!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    init()
