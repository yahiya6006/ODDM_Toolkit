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

def check_if_admin_exists_in_oddm_db(password: str):
    db_name = "oddm_toolkit_db"
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user="postgres",
            password=password,
            host="localhost"
        )
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        return False  # Connection failed

    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'users'
        );
    """)
    table_exists = cursor.fetchone()[0]

    if table_exists:
        cursor.execute("SELECT id FROM users WHERE is_admin = TRUE;")
        admin_exists = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin_exists:
            return True
        else:
            return False

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
    """Inserts user details into the database.
    ERROR IDS:
    ERR-USR-001: Username and Email are already in use.
    ERR-USR-002: Username is already in use.
    ERR-USR-003: Email is already in use.
    """
    
    global PSQL_DB_CONNECTION
    conn = PSQL_DB_CONNECTION
    conn.autocommit = True
    cursor = conn.cursor()

    username = username.lower()
    email = email.lower()

    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
    existing_username = cursor.fetchone()

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = %s;", (email,))
    existing_email = cursor.fetchone()

     # Return appropriate error messages
    if existing_username and existing_email:
        cursor.close()
        return {"success": False, "error": "Username and Email are already in use.", "error_id": "ERR-USR-001"}
    elif existing_username:
        cursor.close()
        return {"success": False, "error": "Username is already in use.", "error_id": "ERR-USR-002"}
    elif existing_email:
        cursor.close()
        return {"success": False, "error": "Email is already in use.", "error_id": "ERR-USR-003"}

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

    return {"success": True, "id": ret_id}

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
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
    user_exists = cursor.fetchone()
    if not user_exists: 
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
    oddm_db_connect_res = connect_to_psql_db(oddm_password, user=db_user, db_name=db_name)
    if not oddm_db_connect_res and exists:
        # Reconnecting to default database
        connect_to_psql_db(Admin_psql_password, db_name=db_name)
        return {"success": False, "error": "ODDM Toolkit database already exists. Invalid password provided.", "error_id": "ERR-ODDM-STUP-001"}

    create_users_table()  # Create the users table

    # add admin user
    res = insert_user_details(superuser_name, superuser_email, superuser_password, is_admin=True, is_active=True)
    if not res["success"]:
        return res

    PSQL_DB_CONNECTION.close()  # Close the connection
    
    user_credentials = {
        "oddm_db_name": db_name,
        "oddm_db_user": db_user,
        "oddm_db_password": oddm_password
    }

    return {"success": True, "credentials": user_credentials}