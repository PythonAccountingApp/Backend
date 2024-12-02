import json
import datetime
import requests
from cryptography.fernet import Fernet

# 定義 API 基本 URL
URL = "http://127.0.0.1:8000/"

# 建立 Session 以保存登入狀態
session = requests.Session()

# ! 需要 cryptography 套件
from cryptography.fernet import Fernet


# ! 需要 cryptography 套件
# 第一次使用時，生成加密金鑰並保存
def generate_and_save_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)


# ! 需要 cryptography 套件
# 加載加密金鑰
def load_key():
    with open("key.key", "rb") as key_file:
        return key_file.read()


# ! 需要 cryptography 套件
# 初始化加密器
def initialize_cipher():
    key = load_key()
    return Fernet(key)


# ! 需要 cryptography 套件
# 保存加密的 Token
def save_token_encrypted(token: str):
    cipher = initialize_cipher()  # 初始化加密器
    encrypted_token = cipher.encrypt(token.encode())  # 加密 Token
    with open("token.enc", "wb") as file:
        file.write(encrypted_token)


# ! 需要 cryptography 套件
# 讀取並解密 Token
def load_token_encrypted() -> str:
    try:
        cipher = initialize_cipher()  # 初始化加密器
        with open("token.enc", "rb") as file:
            encrypted_token = file.read()
        return cipher.decrypt(encrypted_token).decode()  # 解密 Token
    except (FileNotFoundError, Exception):
        return None


"""
註冊
register(username: str, password: str, email: str) -> {message: str, username: str}
"""


def register(username: str, password: str, email: str) -> json:
    register_url = f"{URL}auth/register/"
    new_user_data = {
        "username": username,
        "password": password,
        "email": email,
    }
    response = session.post(register_url, json=new_user_data)
    if response.status_code == 201:
        print("註冊成功:", response.json())
        return response.json()
    else:
        print("註冊失敗:", response.json())
        return response.json()


"""
登入
login(username: str, password) -> {token: str, user_id: int, username: "str", email: str}
"""


def login(username: str, password) -> json:
    login_url = f"{URL}auth/login/"
    response = session.post(
        login_url, json={"username": username, "password": password}
    )
    if response.status_code == 200:
        print("登入成功:", response.json())
        return response.json()
    else:
        print("登入失敗:", response.json())
        return response.json()


"""
登出
logout(token: str) -> {message: str}
"""


def logout(token: str) -> json:
    logout_url = f"{URL}auth/logout/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.post(logout_url, headers=header)  # ! need to add headers(token)
    if response.status_code == 200:
        print("登出成功:", response.json())
        return response.json()
    else:
        print("登出失敗:", response.json())
        return response.json()


"""
取得所有使用者
get_all_users(token: str) -> [
    {
        id: int,
        username: str,
        email: str,
    }
]
"""


def get_all_users(token: str) -> json:
    users_url = f"{URL}users/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.get(users_url, headers=header)  # ! need to add headers(token)
    if response.status_code == 200:
        print("取得所有使用者成功:", response.json())
        return response.json()
    else:
        print("取得所有使用者失敗:", response.json())
        return response.json()


"""
取得記帳資料
get_all_expense(token: str) -> [
    {
        id: int,
        transaction_type: "expense" or "income",
        category: int,
        amount: float,
        discount: float,
        description: str,
        store: str,
        date: date,
        time: time,
        detail: str,
    }
]
"""


def get_all_expense(token: str) -> json:
    expense_url = f"{URL}transactions/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.get(expense_url, headers=header)  # ! need to add headers(token)
    if response.status_code == 200:
        print("取得記帳資料成功:", response.json())
        return response.json()
    else:
        print("取得記帳資料失敗:", response.json())
        return response.json()


"""
取得特定記帳資料（使用 id 或 params）
get_expense(
    token: str,
    id: int,
    params: {category: id, start_date: date, end_date: date}
) -> [
        {
            id: int,
            transaction_type: "expense" or "income",
            category: int,
            amount: float,
            discount: float,
            description: str,
            store: str,
            date: date,
            time: time,
            detail: str,
        }
    ]
"""


def get_expense(token: str, id: int, params: json = None) -> json:
    expense_url = f"{URL}transactions/{id}/" if id else f"{URL}transactions/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.get(
        expense_url,
        params=params,
        headers=header,
    )  # ! need to add headers(token)
    if response.status_code == 200:
        print("取得特定記帳資料成功:", response.json())
        return response.json()
    else:
        print("取得特定記帳資料失敗:", response.json())
        return response.json()


"""
新增記帳資料
create_expense(
    token: str,
    transaction_type: str,
    category: int,
    description: str,
    store: str,
    amount: float = 0,
    discount: float = 0,
    date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
    time: str = datetime.datetime.now().strftime("%H:%M:%S"),
    detail: str = ""
) -> {
        id: int,
        transaction_type: "expense" or "income",
        category: int,
        amount: float,
        discount: float,
        description: str,
        store: str,
        date: str,
        time: time,
        detail: str,
    }
"""


def create_expense(
    token: str,
    transaction_type: str,
    category: int,
    description: str,
    store: str,
    amount: float = 0,
    discount: float = 0,
    date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
    time: str = datetime.datetime.now().strftime("%H:%M:%S"),
    detail: str = "",
) -> json:
    create_expense_url = f"{URL}transactions/"
    new_expense_data = {
        "transaction_type": transaction_type,
        "category": category,
        "description": description,
        "store": store,
        "amount": amount,
        "discount": discount,
        "date": date,
        "time": time,
        "detail": detail,
    }
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.post(
        create_expense_url, json=new_expense_data, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 201:
        print("新增記帳資料成功:", response.json())
        return response.json()
    else:
        print("新增記帳資料失敗:", response.json())
        return response.json()


"""
更新記帳資料
update_expense(
    token: str,
    transaction_type: str,
    category: int,
    description: str,
    store: str,
    amount: float = 0,
    discount: float = 0,
    date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
    time: str = datetime.datetime.now().strftime("%H:%M:%S"),
    detail: str = ""
) -> {
        id: int,
        transaction_type: "expense" or "income",
        category: int,
        amount: float,
        discount: float,
        description: str,
        store: str,
        date: date,
        time: time,
        detail: str,
    }
"""


def update_expense(
    token: str,
    id: int,
    transaction_type: str,
    category: int,
    description: str,
    store: str,
    amount: float = 0,
    discount: float = 0,
    date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
    time: str = datetime.datetime.now().strftime("%H:%M:%S"),
    detail: str = "",
) -> json:
    update_expense_url = f"{URL}transactions/{id}/"
    updated_expense_data = {
        "transaction_type": transaction_type,
        "category": category,
        "description": description,
        "store": store,
        "amount": amount,
        "discount": discount,
        "date": date,
        "time": time,
        "detail": detail,
    }
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.put(
        update_expense_url, json=updated_expense_data, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 200:
        print("更新記帳資料成功:", response.json())
        return response.json()
    else:
        print("更新記帳資料失敗:", response.json())
        return response.json()


"""
刪除記帳資料
delete_expense(token:str, id: int) -> {"message": str}
"""


def delete_expense(token: str, id: int) -> json:
    delete_expense_url = f"{URL}transactions/{id}/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.delete(
        delete_expense_url, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 204:
        print("刪除記帳資料成功")
        return {"message": "刪除記帳資料成功"}
    else:
        print("刪除記帳資料失敗:", response.json())
        return response.json()


"""
取得所有分類
get_all_categories(token: str) -> [
    {
        id: int,
        name: str,
        category_type: "expense" or "income",
    }
]
"""


def get_all_categories(token: str) -> json:
    categories_url = f"{URL}categories/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.get(
        categories_url, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 200:
        print("取得所有分類成功:", response.json())
        return response.json()
    else:
        print("取得所有分類失敗:", response.json())
        return response.json()


"""
取得特定分類
get_category(token:str, id: int, params: {"category_type": "expense" or "income"}) -> [
    {
        id: int,
        name: str,
        category_type: "expense" or "income",
    }
]
"""


def get_category(token: str, id: int = None, params: json = None) -> json:
    category_url = f"{URL}categories/{id}/" if id else f"{URL}categories/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.get(
        category_url, params=params, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 200:
        print("取得特定分類成功:", response.json())
        return response.json()
    else:
        print("取得特定分類失敗:", response.json())
        return response.json()


"""
新增分類
create_category(token:str, name: str, category_type: str) -> {
    id: int,
    name: str,
    category_type: "expense" or "income",
}
"""


def create_category(token: str, name: str, category_type: str) -> json:
    create_category_url = f"{URL}categories/"
    new_category_data = {
        "name": name,
        "category_type": category_type,
    }
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.post(
        create_category_url, json=new_category_data, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 201:
        print("新增分類成功:", response.json())
        return response.json()
    else:
        print("新增分類失敗:", response.json())
        return response.json()


"""
更新分類
update_category(token:str, id: int, name: str, category_type: str) -> {
    id: int,
    name: str,
    category_type: "expense" or "income",
}
"""


def update_category(token: str, id: int, name: str, category_type: str) -> json:
    update_category_url = f"{URL}categories/{id}/"
    updated_category_data = {
        "name": name,
        "category_type": category_type,
    }
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.put(
        update_category_url, json=updated_category_data, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 200:
        print("更新分類成功:", response.json())
        return response.json()
    else:
        print("更新分類失敗:", response.json())
        return response.json()


"""
刪除分類
delete_category(token: str, id: int) -> {"message": str}
"""


def delete_category(token: str, id: int) -> json:
    delete_category_url = f"{URL}categories/{id}/"
    header = {"Authorization": f"Token {token}"}  # token is from login()
    response = session.delete(
        delete_category_url, headers=header
    )  # ! need to add headers(token)
    if response.status_code == 204:
        print("刪除分類成功")
        return {"message": "刪除分類成功"}
    else:
        print("刪除分類失敗:", response.json())
        return response.json()


if __name__ == "__main__":
    generate_and_save_key() #! 第一次運行時需要生成金鑰
    register("test", "123", "test.gmail.com")
    token = login("test", "123")["token"]
    save_token_encrypted(token) # 登入成功後保存 Token
    token = load_token_encrypted() # 讀取 Token
    # get_all_users(token)
    # get_all_expense(token)
    # update_expense(token, 1, "expense", 2, "晚餐", "肯德基", 299, 0)
    # get_expense(token, 15)
    # get_expense(
    #     token, None, {"category": 1, "start_date": "2021-01-01", "end_date": "2021-12-31"}
    # )
    # create_expense(token, "expense", 1, "午餐", "麥當勞", 100, 0)
    # delete_expense(token, 14)
    # get_all_categories(token)
    # get_category(token, 1)
    # get_category(token, None, {"category_type": "income"})
    # create_category(token, "測試", "income")
    # update_category(token, 24, "測試", "expense")
    # delete_category(token, 24)
    logout(token)
