import database

def hash_password(password):
    return database.hash_password(password)

def register_user(username, password):
    # Retorna True se cadastrado com sucesso, False se usuário já existir
    return database.add_user(username, password)

def validate_user(username, password):
    user = database.check_user(username, password)
    return user is not None

def get_user_data(username):
    # Retorna (id, username, password_hash, is_admin) ou None
    return database.get_user_details_by_username(username)
