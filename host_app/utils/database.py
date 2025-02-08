import psycopg2
from psycopg2 import sql, OperationalError
from argon2 import PasswordHasher

pass_hash = PasswordHasher()

# Global variable to store connection
PSQL_DB_CONNECTION = None

def connect_to_psql_db(password: str, host="localhost", user="postgres", db_name="postgres"):
    """Establishes a connection to the PostgreSQL database."""
    global PSQL_DB_CONNECTION
    try:
        PSQL_DB_CONNECTION = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host
        )
        return True  # Connection successful
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        return False  # Connection failed

def get_psql_connection():
    """Returns the established database connection."""
    return PSQL_DB_CONNECTION

def create_users_table():
    global PSQL_DB_CONNECTION

    conn = PSQL_DB_CONNECTION
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'users'
        );
    """)
    exists = cursor.fetchone()[0]

    if not exists:
        # Create the users table
        create_table_query = """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE,  -- Unique, nullable until registration completes
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255),   -- Nullable until user sets a password
                is_admin BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT FALSE,  -- Becomes TRUE after registration
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'users' created successfully!")
    else:
        print("Table 'users' already exists.")

    # Close connection
    cursor.close()

def insert_user_details(username, email, password_hash=None, is_admin=False, is_active=False):
    """Inserts user details into the database."""
    
    global PSQL_DB_CONNECTION
    conn = PSQL_DB_CONNECTION
    conn.autocommit = True
    cursor = conn.cursor()

    if password_hash is not None:
        hashed_password = pass_hash.hash(password_hash)
    else:
        hashed_password = ""  # Empty password for users who will set it later
        is_active = False     # Force inactive if no password is provided

    query = sql.SQL("""
            INSERT INTO users (username, email, password_hash, is_admin, is_active)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """)

    cursor.execute(query, (username, email, hashed_password, is_admin, is_active))
    ret_id = cursor.fetchone()[0]
    cursor.close()

    return ret_id

def setup_oddm_toolkit_db(oddm_password, Admin_psql_password, superuser_email, superuser_name, superuser_password):
    """Sets up the ODDM Toolkit database."""

    global PSQL_DB_CONNECTION

    db_name = "oddm_toolkit_db"
    db_user = "oddm_admin"

    conn = PSQL_DB_CONNECTION
    conn.autocommit = True
    cursor = conn.cursor()

    # Step 1: Create the ODDM Toolkit database (if it doesn’t exist)
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
    exists = cursor.fetchone()
    if not exists:  # If database does not exist, create it
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))

    # Step 2: Create the user `oddm_admin`
    cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(db_user)), [oddm_password])

    # Step 3: Grant all privileges to `oddm_admin` on the new database
    cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(sql.Identifier(db_name), sql.Identifier(db_user)))

    cursor.close()
    conn.close()
    PSQL_DB_CONNECTION = None  # Reset the connection

    # Step 4: Connect to the new database
    connect_to_psql_db(Admin_psql_password, db_name=db_name)  # Reconnect to the new database with the Admin password
    conn = PSQL_DB_CONNECTION
    conn.autocommit = True
    cursor = conn.cursor()

    # Step 5: Grant privileges on schema
    cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON SCHEMA public TO {}").format(sql.Identifier(db_user)))
    
    # Step 6: Make the user the owner of the schema (important)
    cursor.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(db_user)))
    
    cursor.close()
    conn.close()
    PSQL_DB_CONNECTION = None  # Reset the connection

    # Step 7: Connect to the new database with the new user
    connect_to_psql_db(oddm_password, user=db_user, db_name=db_name)
    create_users_table()  # Create the users table

    # add admin user
    insert_user_details(superuser_name, superuser_email, superuser_password, is_admin=True, is_active=True)

    PSQL_DB_CONNECTION.close()  # Close the connection
    
    user_credentials = {
        "oddm_db_name": db_name,
        "oddm_db_user": db_user,
        "oddm_db_password": oddm_password
    }

    return user_credentials