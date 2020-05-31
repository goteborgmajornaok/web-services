from app.members import fetch_members


def ids_in_club():
    members = fetch_members()
    return [int(m.find('PersonId').text) for m in members]


def delete_users_not_in_club():
    pass
