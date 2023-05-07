from contextlib import contextmanager
import logging
import sqlite3

CSS_DATABASE = 'db/css.db'
log = logging.getLogger(__name__)

@contextmanager
def css_cursor():
    conn = sqlite3.connect(CSS_DATABASE)
    cur = conn.cursor()
    try:
        yield cur
    finally:
        conn.commit()
        cur.close()
        conn.close()

@contextmanager
def css_connection():
    conn = sqlite3.connect(CSS_DATABASE)
    try:
        yield conn
    finally:
        conn.close()


def execute_sql(sql, cur, runtime_values=None, verbose=False):
    log_msg = f"Executing SQL: {sql}"
    if runtime_values:
        log_msg += f" with bindings {runtime_values}"
    if verbose:
        log.info(log_msg)
    if runtime_values:
        cur.execute(sql, runtime_values)
    else:
        cur.execute(sql)
