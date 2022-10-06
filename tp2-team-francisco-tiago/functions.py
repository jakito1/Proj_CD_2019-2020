"""
 Functions to be used by the server.
"""


def username(users_rooms, temp_username, user_pmsg):
    """Create new user."""
    if temp_username in users_rooms:
        return '/username taken'

    users_rooms[temp_username] = 0
    user_pmsg[temp_username] = '/pmsgs '
    return '/username ok'


def rooms(all_rooms):
    """Get all rooms from list."""
    res = '/rooms'
    for temp_room in all_rooms:
        res += ' #' + temp_room
    return res


def room(user_rooms, temp_username, temp_rooms):
    """Get user's current room."""
    return '/room #' + temp_rooms[user_rooms[temp_username]]


def check_if_room_exists(new_room, temp_rooms):
    """Check if given room exists."""
    return new_room in temp_rooms


def create_room(temp_rooms, new_room, rooms_msg_queue, queue_pos):
    """Create new room."""
    if check_if_room_exists(new_room, temp_rooms):
        return '/create room_exists'

    temp_rooms.append(new_room)
    queue_pos.append(0)
    rooms_msg_queue.append('')
    return '/create ok'


def join_room(temp_username, users_rooms, temp_rooms, temp_room):
    """Join user to new room."""
    if not check_if_room_exists(temp_room, temp_rooms):
        return '/join no_room'

    users_rooms[temp_username] = temp_rooms.index(temp_room)
    return '/join ok'


def get_room_id(users_rooms, temp_username):
    """Get room_id."""
    return users_rooms[temp_username]


def users(temp_username, users_rooms):
    """Get all users from current room."""
    return_users = '/users '
    for current_user in users_rooms:
        if users_rooms[current_user] == get_room_id(users_rooms, temp_username):
            return_users += current_user
    return return_users


def all_users(users_rooms, temp_rooms):
    """Get all users in server."""
    return_users = '/allusers '
    for current_user in users_rooms:
        room_id = users_rooms[current_user]
        return_users += current_user + '@#' + temp_rooms[room_id]
    return return_users


def msgs(users_rooms, temp_username, rooms_msg_queue, queue_pos):
    """Retrieve messages from queue."""
    room_id = get_room_id(users_rooms, temp_username)
    msg_queue = rooms_msg_queue[room_id]
    if len(msg_queue) == queue_pos[room_id]:
        return '/msgs none'

    temp_string = '/msgs ' + msg_queue[queue_pos[room_id]: None]
    queue_pos[room_id] = len(msg_queue)
    return temp_string


def msg(users_rooms, temp_username, temp_rooms, rooms_msg_queue, temp_msg):
    """Send new message to room."""
    room_id = get_room_id(users_rooms, temp_username)
    temp_string = '(' + temp_username + ' @#' + temp_rooms[room_id] + ') ' + temp_msg
    rooms_msg_queue[room_id] += temp_string
    return '/msg sent'


def pmsg(temp_username, users_pmsg, temp_pmsg, temp_sender):
    """Send new private message to user."""
    if temp_username in users_pmsg:
        users_pmsg[temp_username] += '(' + temp_sender + ' @private) ' + temp_pmsg
        return '/pmsg sent'

    return '/pmsg no_user'


def pmsgs(temp_username, users_pmsg):
    """Retrieve all private messages from queue."""
    temp_string = users_pmsg[temp_username]
    if len(temp_string) == 7:
        return '/pmsgs none'
    users_pmsg[temp_username] = '/pmsgs '
    return temp_string


def remove_user(temp_username, users_rooms, users_pmsg):
    """Remove user from lists."""
    try:
        del users_rooms[temp_username]
        del users_pmsg[temp_username]
    except KeyError:
        pass
    except AttributeError:
        pass
