"""
 Flask REST application

"""

from flask import Flask, request, jsonify, make_response
from models import Database


# ==========
#  Settings
# ==========

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'
app.config['DEBUG'] = True


# ==========
#  Database
# ==========

# Creates an sqlite database in memory
db = Database(filename=':memory:', schema='schema.sql')
db.recreate()


def get_user_authentication():
    """
    Get user authentication
    """
    return db.execute_query('SELECT * FROM user WHERE username=? AND password=?', (
        request.authorization.username,
        request.authorization.password,
    )).fetchone()


# ===========
#  Web views
# ===========

@app.route('/')
def index():
    """
    Default page
    """
    return app.send_static_file('index.html')


# ===========
#  API views
# ===========

@app.route('/api/user/register/', methods=['POST'])
def user_register():
    """
    Registers a new user.
    Does not require authorization.

    """
    user = db.add_user(request.get_json())
    return make_response(jsonify(user), 201)


@app.route('/api/user/', methods=['GET', 'PUT'])
def user_detail():
    """
    Returns or updates current user.
    Requires authorization.

    """
    user = get_user_authentication()
    if user is None:
        return make_response(jsonify("Wrong Credentials"), 403)
    if request.method == 'GET':
        # Returns user data
        return make_response(jsonify(user))
    # Updates user data
    updated_user = db.update_user(user, request.get_json())
    return make_response(jsonify(updated_user), 202)


@app.route('/api/projects/', methods=['GET', 'POST'])
def project_list():
    """
    Project list.
    Requires authorization.

    """
    user = get_user_authentication()
    if user is None:
        return make_response(jsonify("Wrong Credentials"), 403)
    if request.method == 'GET':
        # Returns the list of projects of a user
        projects = db.execute_query('SELECT * FROM project WHERE user_id=%s' %
                                    user['id']).fetchall()
        return make_response(jsonify(projects))
    # Adds a project to the list
    project = db.add_project(request.get_json(), user)
    return make_response(jsonify(project), 201)


@app.route('/api/projects/<primary_key>/', methods=['GET', 'PUT', 'DELETE'])
def project_detail(primary_key):
    """
    Project detail.
    Requires authorization.

    """
    user = get_user_authentication()
    if user is None:
        return make_response(jsonify("Wrong Credentials"), 403)
    if request.method == 'GET':
        # Returns a project
        project = db.get_project(primary_key, user['id'])
        if project is not None:
            return make_response(jsonify(project))
    if request.method == 'PUT':
        # Updates a project
        updated_project = db.update_project(primary_key, request.get_json(), user)
        if updated_project is not None:
            return make_response(jsonify(updated_project), 202)

    # Deletes a project
    removed_project = db.remove_project(primary_key, user)
    if removed_project is not None:
        return make_response(jsonify(removed_project), 200)
    return make_response(jsonify(), 404)


@app.route('/api/projects/<foreign_key>/tasks/', methods=['GET', 'POST'])
def task_list(foreign_key):
    """
    Task list.
    Requires authorization.

    """
    user = get_user_authentication()
    if user is None:
        return make_response(jsonify("Wrong Credentials"), 403)
    if request.method == 'GET':
        # Returns the list of tasks of a project
        if db.get_project(foreign_key, user['id']) is None:
            return make_response(jsonify("Not Valid"), 404)
        tasks = db.execute_query('SELECT * FROM task WHERE project_id=?', (foreign_key,)).fetchall()
        return make_response(jsonify(tasks))
    # Adds a task to project
    if db.get_project(foreign_key, user['id']) is None:
        return make_response(jsonify("Not Valid"), 404)
    tasks = db.add_task(request.get_json(), foreign_key, user)
    return make_response(jsonify(tasks), 201)


@app.route('/api/projects/<foreign_key>/tasks/<int:task_pk>/', methods=['GET', 'PUT', 'DELETE'])
def task_detail(foreign_key, task_pk):
    """
    Task detail.
    Requires authorization.

    """
    user = get_user_authentication()
    if user is None:
        return make_response(jsonify("Wrong Credentials"), 403)
    if request.method == 'GET':
        # Returns a task
        task = db.get_task(task_pk, foreign_key, user)
        if task is not None:
            return make_response(jsonify(task))
    if request.method == 'PUT':
        # Updates a task
        updated_task = db.update_task(request.get_json(), task_pk, foreign_key, user)
        if updated_task is not None:
            return make_response(jsonify(updated_task), 202)
    # Deletes a task
    removed_task = db.remove_task(task_pk, foreign_key, user)
    if removed_task is not None:
        return make_response(jsonify(removed_task), 200)
    return make_response(jsonify(), 404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
