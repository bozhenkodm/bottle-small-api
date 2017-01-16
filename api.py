import json
import base64
import dbm
from functools import wraps
from bottle import route, request, response, run, put, delete

from settings import DB_NAME, AUTH, HOST, PORT


def login_check(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        username, password = None, None
        if "Authorization" in request.headers:
            auth = request.headers.get("Authorization").split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                auth = base64.b64decode(auth[1].encode())
                username, password = auth.decode().split(':')
        if (username, password) != AUTH:
            response.status = 401
            return {'status': 'error', 'message': 'authentication failed'}
        return method(*args, **kwargs)

    return wrapper


@route('/api/users')
@login_check
def users_list():
    result = {'users': []}
    with dbm.open(DB_NAME) as db:
        k = db.firstkey()
        while k is not None:
            result['users'].append({'id': [k], 'user': db[k]})
            k = db.nextkey(k)
        response.content_type = 'application/json'
        return result


@route('/api/users/<user>')
@login_check
def name_search(user):
    with dbm.open(DB_NAME) as db:
        k = db.firstkey()
        response.content_type = 'application/json'
        while k is not None:
            if db[k].decode('utf-8') == user:
                return {'id': [k], 'user': db[k]}
            k = db.nextkey(k)
        response.status = 404
        return {'status': 'error', 'message': 'User not found'}


@route('/api/id/<_id>')
@login_check
def id_search(_id):
    with dbm.open(DB_NAME) as db:
        response.content_type = 'application/json'
        if db.get(_id, False):
            return {'id': _id, 'user': db[_id].decode('utf-8')}
        response.status = 404
        return {'status': 'error', 'message': 'User not found'}


@delete('/api/id/<_id>')
@login_check
def id_delete(_id):
    with dbm.open(DB_NAME, 'c') as db:
        response.content_type = 'application/json'
        if db.get(_id, False):
            del db[_id.encode()]
            return {'status': 'success', 'message': 'User has been deleted'}
        response.status = 404
        return {'status': 'error', 'message': 'User not found'}


@put('/api/id/<_id>')
@login_check
def id_update(_id):
    """
    body format: {'user': '<user>'}
    """
    user = json.loads(request.body.read().decode())['user']
    with dbm.open(DB_NAME, 'c') as db:
        response.content_type = 'application/json'
        if db.get(_id, False):
            db[_id] = user
            return {'status': 'success', 'message': 'User has been updated'}
        response.status = 404
        return {'status': 'error', 'message': 'User not found'}


run(host=HOST, port=PORT, debug=True)
