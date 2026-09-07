import sqlite3
import threading
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from config.config import DATABASE_PATH


class Database:
    """
    Thread-safe, hardened SQLite connection manager for SentinelAI.
    Enforces WAL journal mode, proper timeouts, and foreign key constraints.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else Path(DATABASE_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        
        self.connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=30.0,
        )
        self.connection.row_factory = sqlite3.Row
        self._configure_pragmas()

    def _configure_pragmas(self) -> None:
        """Enable performance and concurrency optimizations."""
        with self._lock:
            cur = self.connection.cursor()
            cur.execute("PRAGMA journal_mode = WAL;")
            cur.execute("PRAGMA synchronous = NORMAL;")
            cur.execute("PRAGMA foreign_keys = ON;")
            cur.execute("PRAGMA busy_timeout = 30000;")
            cur.close()

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> sqlite3.Cursor:
        """Thread-safe query execution with auto-commit."""
        with self._lock:
            cur = self.connection.cursor()
            try:
                cur.execute(query, params)
                self.connection.commit()
                return cur
            except Exception:
                self.connection.rollback()
                raise

    def executemany(self, query: str, seq_of_params: List[Tuple[Any, ...]]) -> sqlite3.Cursor:
        """Thread-safe batch query execution."""
        with self._lock:
            cur = self.connection.cursor()
            try:
                cur.executemany(query, seq_of_params)
                self.connection.commit()
                return cur
            except Exception:
                self.connection.rollback()
                raise

    def fetchall(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Thread-safe fetch all rows."""
        with self._lock:
            cur = self.connection.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            return rows

    def fetchone(self, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        """Thread-safe fetch single row."""
        with self._lock:
            cur = self.connection.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            cur.close()
            return row

    def close(self) -> None:
        """Close database connection."""
        with self._lock:
            try:
                self.connection.close()
            except Exception:
                pass