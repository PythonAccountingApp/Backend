import datetime
import requests

# 定義 API 基本 URL
BASE_URL = "http://127.0.0.1:8000/"

# 使用者帳號和密碼
username = "test"
password = "123"

# 建立 Session 以保存登入狀態
session = requests.Session()


# 記帳資料 ID
expense_arg = "2024-11-14"

# 測試註冊
def test_register():
    register_url = f"{BASE_URL}auth/register/"
    new_user_data = {
        "username": username,
        "password": password,
        "email": "test@gmail.com",
    }
    headers = {"Authorization": f"Token {token}"}
    response = session.post(register_url, json=new_user_data, headers=headers)
    if response.status_code == 201:
        print("註冊成功:", response.json())
    else:
        print("註冊失敗:", response.json())


# 測試登入
def test_login(token):
    login_url = f"{BASE_URL}auth/login/"
    response = session.post(
        login_url, json={"username": username, "password": password}
    )
    if response.status_code == 200:
        print("登入成功:", response.json())
        token = response.json()["token"]
        return token
    else:
        print("登入失敗:", response.json())


# 測試取得記帳資料
def test_list_expenses():
    expenses_url = f"{BASE_URL}transactions/"
    response = session.get(expenses_url)
    if response.status_code == 200:
        print("取得記帳資料成功:", response.json())
    else:
        print("取得記帳資料失敗:", response.text)


# 測試取得特定記帳資料
def test_get_expense():
    expense_url = f"{BASE_URL}transactions/"
    response = session.get(expense_url, params={"category": 1, "start_time": "2024-09-14", "end_time": "2024-11-15"})
    if response.status_code == 200:
        print("取得特定記帳資料成功:", response.json())
    else:
        print("取得特定記帳資料失敗:", response.json())


# 測試新增記帳資料
def test_create_expense(token):
    create_expense_url = f"{BASE_URL}transactions/"
    new_expense_data = {
        "transaction_type": "expense",
        "category": 2,
        "date": "2023-11-14",
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "description": "午餐",
        "amount": "120.50",
        "store": "麥當勞",
    }
    headers = {"Authorization": f"Token {token}"}
    response = session.post(create_expense_url, json=new_expense_data, headers=headers)
    if response.status_code == 201:
        print("新增記帳資料成功:", response.json())
    else:
        print("新增記帳資料失敗:", response.json())


# 測試更新記帳資料
def test_update_expense(token):
    update_expense_url = f"{BASE_URL}transactions/{expense_arg}/"
    updated_expense_data = {
        "description": "晚餐",
        "amount": "200.00",
        "store": "肯德基",
    }
    headers = {"Authorization": f"Token {token}"}
    response = session.put(update_expense_url, json=updated_expense_data, headers=headers)
    if response.status_code == 200:
        print("更新記帳資料成功:", response.json())
    else:
        print("更新記帳資料失敗:", response.json())


# 測試刪除記帳資料
def test_delete_expense(token):
    delete_expense_url = f"{BASE_URL}transactions/{expense_arg}/"
    headers = {"Authorization": f"Token {token}"}
    response = session.delete(delete_expense_url, headers=headers)
    if response.status_code == 204:
        print("刪除記帳資料成功")
    else:
        print("刪除記帳資料失敗:", response.json())


# 測試登出
def test_logout(token):
    logout_url = f"{BASE_URL}auth/logout/"
    headers = {"Authorization": f"Token {token}"}
    response = session.post(logout_url, headers=headers)
    if response.status_code == 200:
        print("登出成功:", response.json())
    else:
        print("登出失敗:", response.json())


# 執行測試
if __name__ == "__main__":
    token = None
    # test_register()  # 測試註冊
    token = test_login(token)  # 測試登入
    response = session.get(
        f"{BASE_URL}categories/",
        params={"category_type": "income"},
        headers={"Authorization": f"Token {token}"},
    )  # 取得分類資料
    print(response.json())
    # test_create_expense()  # 測試新增記帳資料
    # test_list_expenses()  # 測試取得記帳資料
    # test_get_expense()  # 測試取得特定記帳資料
    # test_logout()  # 測試登出
