import mysql.connector
from mysql.connector import pooling
import threading

# Centralized database configuration matching your precise original credentials
db_config = {
    'host': 'localhost',
    'user': 'root',          
    'password': 'root',       # Restored your correct password from your original config
    'database': 'ammp_db',   
    'raise_on_warnings': True
}

# Thread-safe initialization of the connection pool
try:
    db_pool = pooling.MySQLConnectionPool(
        pool_name="ammp_pool",
        pool_size=15,  # Accommodates concurrent fetches from supervisor and allocation dashboards
        **db_config
    )
    print("MySQL Thread Connection Pool initialized successfully.")
except mysql.connector.Error as err:
    print(f"Failed to initialize MySQL Pool: {err}")
    raise err

# Thread-local storage to keep database connections distinct per HTTP request context
_local_storage = threading.local()

class ThreadSafeCursorProxy:
    """
    A permanent proxy class that mimics a global cursor object.
    It automatically leases, executes, and cleans up pool connections 
    dynamically behind the scenes for any Flask thread accessing it.
    """
    def _get_connection_and_cursor(self):
        # If the current request thread doesn't have an active connection, lease one
        if not getattr(_local_storage, 'conn', None) or not _local_storage.conn.is_connected():
            _local_storage.conn = db_pool.get_connection()
            # Keeps the autocommit behavior your app relies on for inserts/updates
            _local_storage.conn.autocommit = True 
            # ADDED: buffered=True to cleanly solve "Unread result found" errors project-wide
            _local_storage.cursor = _local_storage.conn.cursor(dictionary=True, buffered=True)
        return _local_storage.cursor

    def execute(self, query, params=None):
        cursor = self._get_connection_and_cursor()
        try:
            if params:
                return cursor.execute(query, params)
            return cursor.execute(query)
        except mysql.connector.errors.OperationalError as e:
            # Re-verify and retry once if a pipe drops unexpectedly
            if "Lost connection" in str(e) or "MySQL server has gone away" in str(e):
                self.close_current()
                cursor = self._get_connection_and_cursor()
                if params:
                    return cursor.execute(query, params)
                return cursor.execute(query)
            raise e

    def fetchall(self):
        cursor = getattr(_local_storage, 'cursor', None)
        if cursor is None:
            cursor = self._get_connection_and_cursor()
        return cursor.fetchall()

    def fetchone(self):
        cursor = getattr(_local_storage, 'cursor', None)
        if cursor is None:
            cursor = self._get_connection_and_cursor()
        return cursor.fetchone()

    @property
    def lastrowid(self):
        cursor = getattr(_local_storage, 'cursor', None)
        if cursor:
            return cursor.lastrowid
        return None

    def close_current(self):
        """Safely returns the connection used by this thread back to the pool."""
        cursor = getattr(_local_storage, 'cursor', None)
        conn = getattr(_local_storage, 'conn', None)
        if cursor:
            try: cursor.close()
            except: pass
        if conn:
            try: conn.close()
            except: pass
        _local_storage.cursor = None
        _local_storage.conn = None

# Global targets imported by app.py
cursor = ThreadSafeCursorProxy()

class DatabaseCommitProxy:
    """Redirects legacy global config.db.commit() calls safely to active local connection threads"""
    def commit(self):
        conn = getattr(_local_storage, 'conn', None)
        if conn and conn.is_connected():
            conn.commit()

# Real functional link replacing the broken "db = None" setup
db = DatabaseCommitProxy()

def connect_db():
    """Kept as a dummy function to prevent crashes if app.py calls it on startup"""
    pass

def reconnect_db():
    """Kept as a dummy function to prevent crashes if app.py relies on manual pings"""
    pass

def commit():
    """Commits transactions manually if explicit calls exist inside app.py"""
    db.commit()

def close_request_connection():
    """Cleans up and releases the connection back to the pool at request end."""
    cursor.close_current()