import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn


def check_eventor_id(person_id):
    conn = create_connection('gmok-utils.db')
    cursor = conn.cursor()
    cursor.execute("select count(id) from users where eventor_id = ?", (person_id,))
    records = cursor.fetchall()
    return records[0][0] > 0


def save_user(eventor_id, wordpress_id):
    conn = create_connection('gmok-utils.db')
    cursor = conn.cursor()
    sql = '''insert into users(eventor_id, wordpress_id, created, deleted) values (?, ?, datetime('now'), 0);'''
    cursor.execute(sql, (eventor_id, wordpress_id))
    conn.commit()
    conn.close()
