from flask import Blueprint, request, jsonify

from application.eventor_utils import get_membership, find_value, fetch_members
from application.wordpress_utils import get_users, update_user
from definitions import config

user_inventory_app = Blueprint('wordpress_user_inventory', __name__)

reserved_users = config['Wordpress']['reserved_users'].split(',')
member_role = config['Wordpress']['member']
guest_member_role = config['Wordpress']['guest_member']
inactive_member_role = config['Wordpress']['inactive_member']


def deactivate_user(user_id):
    update_user(user_id, {'roles': inactive_member_role})


def get_membership_dict():
    members = fetch_members()
    members_dict = dict()
    for m in members:
        id = find_value([["PersonId"]], m)
        membership = get_membership(m)
        members_dict[id] = membership
    return members_dict


def update_users_of_role(role, membership_dict, inactive_action=None):
    users = get_users(role)
    for user in users:
        if user['slug'] in reserved_users:
            continue

        username = user['slug']
        if username in membership_dict.keys():
            # Check if membership is changed
            if membership_dict[username] != role:
                # Update user with new role
                update_user(str(user['id']), {'roles': membership_dict[username]})
        else:
            # User not member anymore, deactivate user
            if inactive_action is not None:
                inactive_action(str(user['id']))


@user_inventory_app.route('/inventory', methods=['POST'])
def user_inventory():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth != config['ApiSettings']['ApiKey']:
        return jsonify({"message": "ERROR: Unauthorized"}), 401
    membership_dict = get_membership_dict()

    # Activate inactive users that are registered members again
    update_users_of_role(inactive_member_role, membership_dict)
    # Change role or deactivate members
    update_users_of_role(member_role, membership_dict, deactivate_user)
    # Change role or deactivate guest members
    update_users_of_role(guest_member_role, membership_dict, deactivate_user)

    return jsonify({"message": "User inventory performed successfully."}), 200