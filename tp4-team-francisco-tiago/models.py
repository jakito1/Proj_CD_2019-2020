"""
 Implements a simple database of users.

"""

import sqlite3


class Database:
    """Database connectivity."""

    def __init__(self, filename, schema):
        self.filename = filename
        self.schema = schema
        self.conn = sqlite3.connect(filename, check_same_thread=False)

        def dict_factory(cursor, row):
            """Converts table row to dictionary."""
            res = {}
            for idx, col in enumerate(cursor.description):
                res[col[0]] = row[idx]
            return res

        self.conn.row_factory = dict_factory

    def recreate(self):
        """Recreates the database from the schema file."""
        with open(self.schema) as fin:
            self.conn.cursor().executescript(fin.read())

    def execute_query(self, stmt, args=()):
        """Executes a query."""
        res = self.conn.cursor().execute(stmt, args)
        return res

    def execute_update(self, stmt, args=()):
        """Executes an insert or update and returns the last row id."""
        temp_cursor = self.conn.cursor()
        temp_cursor.execute(stmt, args)
        self.conn.commit()
        return temp_cursor.lastrowid

    def get_user(self, primary_key):
        """Returns a single user."""
        res = self.conn.cursor().execute('SELECT * FROM user WHERE id=%s' % primary_key)
        return res.fetchall()

    def add_user(self, new_user):
        """Adds a new user."""
        stmt = "INSERT INTO user VALUES (null, '%s', '%s', '%s', '%s')" % \
               (new_user['name'], new_user['email'],
                new_user['username'], new_user['password'])
        return self.get_user(self.execute_update(stmt))

    def update_user(self, user, data):
        """Updates a user with the given data."""
        stmt = "UPDATE user SET name='%s', email='%s', username='%s', password='%s' WHERE id=%s" % \
               (data['name'], data['email'], data['username'], data['password'], user['id'])
        self.execute_update(stmt)
        return self.get_user(user['id'])

    def get_project(self, primary_key, foreign_key):
        """Get project with PK."""
        res = self.conn.cursor().execute('SELECT * FROM project WHERE id=? AND user_id=?',
                                         (primary_key, foreign_key))
        return res.fetchone()

    def add_project(self, new_project, user):
        """Adds a new project to user."""
        stmt = "INSERT INTO project VALUES (null, '%d', '%s', '%s', '%s')" % \
               (user['id'],
                new_project['title'],
                new_project['creation_date'],
                new_project['last_updated'])
        return self.get_project(self.execute_update(stmt), user['id'])

    def update_project(self, primary_key, data, user):
        """Updates a project with the given data."""
        if self.get_project(primary_key, user['id']) is not None:
            stmt = "UPDATE project SET title='%s', last_updated='%s' WHERE id=%s" % \
                (data['title'], data['last_updated'], primary_key)
            self.execute_update(stmt)
            return self.get_project(primary_key, user['id'])
        return None

    def remove_project(self, primary_key, user):
        """Remove project with project PK and user PK."""
        if self.get_project(primary_key, user['id']) is not None:
            removed_project = self.get_project(primary_key, user['id'])
            stmt = "DELETE from project WHERE id=%s AND user_id=%s" % \
                (primary_key, user['id'])
            self.execute_update(stmt)
            return removed_project
        return None

    def get_task(self, primary_key, foreign_key, user):
        """Get task with PK."""
        if self.get_project(foreign_key, user['id']) is not None:
            res = self.conn.cursor().execute('SELECT * FROM task WHERE id=? AND project_id=?',
                                             (primary_key, foreign_key))
            return res.fetchone()
        return None

    def add_task(self, new_task, foreign_key, user):
        """Adds a new task to user."""
        stmt = "INSERT INTO task VALUES (null, '%s', '%s', '%s', '%s')" % \
               (foreign_key,
                new_task['title'],
                new_task['creation_date'],
                new_task['completed'])
        return self.get_task(self.execute_update(stmt), foreign_key, user)

    def update_task(self, data, primary_key, foreign_key, user):
        """Updates a task with the given data."""
        if self.get_task(primary_key, foreign_key, user) is not None:
            stmt = "UPDATE task SET title='%s', completed='%s' WHERE id=%s" % \
                (data['title'], data['completed'], primary_key)
            self.execute_update(stmt)
            return self.get_task(primary_key, foreign_key, user)
        return None

    def remove_task(self, primary_key, foreign_key, user):
        """Remove task with project PK and user PK."""
        if self.get_task(primary_key, foreign_key, user) is not None:
            removed_task = self.get_task(primary_key, foreign_key, user)
            stmt = "DELETE from task WHERE id=%s AND project_id=%s" % \
                (primary_key, foreign_key)
            self.execute_update(stmt)
            return removed_task
        return None
