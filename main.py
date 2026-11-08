import os
import json
import re
import subprocess
from datetime import datetime, timedelta

DATA_FILE = "accounts_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def check_and_update_bans(data):
    now = datetime.now()
    updated = False
    for acc in data:
        if "unban_at" in acc and acc["unban_at"]:
            unban_dt = datetime.strptime(acc["unban_at"], "%Y-%m-%d %H:%M:%S")
            if now >= unban_dt:
                acc["status"] = "Не забанен"
                acc["unban_at"] = None
                updated = True
    if updated:
        save_data(data)

def show_accounts(data):
    os.system('cls' if os.name == 'nt' else 'clear')
    check_and_update_bans(data)
    max_name_len = max(max(len(acc['name']) for acc in data), 15)
    print("\n=== СПИСОК АККАУНТОВ ", "=" * (max_name_len - 6))
    if not data:
        print("(список пуст, добавь первый аккаунт)")
    else:
        for idx, acc in enumerate(data, start=1):
            aligned_name = acc['name'].ljust(max_name_len)
            print(f"[{idx:02}] Никнейм: {aligned_name} | Статус: {acc['status']}")
    print("=" * max_name_len + ("=" * 16), "\n")

def parse_duration(time_str):
    time_str = time_str.strip().lower()
    match = re.match(r"^(\d+)\s*([a-zа-я]+)$", time_str)
    if not match:
        return None
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    if unit in ['h', 'ч']:
        return timedelta(hours=amount)
    elif unit in ['d', 'д']:
        return timedelta(days=amount)
    elif unit in ['m', 'м']:
        return timedelta(days=amount * 31)
    elif unit in ['min', 'мин']:
        return timedelta(minutes=amount)
    else:
        return None

def main():
    data = load_data()
    
    while True:
        show_accounts(data)
        print("1. Забанить")
        print("2. Добавить новый аккаунт")
        print("3. Разбанить")
        print("4. Удалить аккаунт")
        print("5. Посмотреть / Изменить данные")
        print("6. Выйти")
        
        choice = input("\nВыбери действие: ").strip()
        
        if choice == "2":
            acc_name = input("Введи никнейм аккаунта: ").strip()
            if not acc_name:
                print("Никнейм не может быть пустым.")
                input("\nНажми Enter, чтобы продолжить...")
                continue
            if any(acc['name'] == acc_name for acc in data):
                print("Аккаунт с таким именем уже есть!")
            else:
                steam_user = input("Введи логин аккаунта: ").strip()
                steam_passwd = input("Введи пароль аккаунта: ").strip()
                data.append({
                    "name": acc_name, 
                    "username": steam_user, 
                    "status": "Не забанен", 
                    "unban_at": None, 
                    "password": steam_passwd
                })
                save_data(data)
                print(f"Аккаунт '{acc_name}' успешно добавлен.")
            input("\nНажми Enter, чтобы продолжить...")
                
        elif choice == "1":
            id_str = input("Введи номер аккаунта для бана: ").strip()
            if not id_str.isdigit():
                print("Нужно ввести цифру.")
                input("\nНажми Enter, чтобы продолжить...")
                continue
                
            idx = int(id_str) - 1
            if 0 <= idx < len(data):
                duration_str = input("Введи время бана (например: 20h, 7d, 3m): ").strip()
                delta = parse_duration(duration_str)
                
                if delta is None:
                    print("Неверный формат времени!")
                    input("\nНажми Enter, чтобы продолжить...")
                    continue
                
                now = datetime.now()
                unban_time = now + delta
                
                data[idx]["status"] = f"Бан до {unban_time.strftime('%d.%m.%Y %H:%M')}"
                data[idx]["unban_at"] = unban_time.strftime("%Y-%m-%d %H:%M:%S")
                save_data(data)
                print(f"Успешно! Аккаунт [{id_str}] заблокирован.")
            else:
                print("Аккаунт с таким номером не найден.")
            input("\nНажми Enter, чтобы продолжить...")
                
        elif choice == "3":
            id_str = input("Введи номер аккаунта, который стоит разбанить: ").strip()
            if not id_str.isdigit():
                print("Нужно ввести номер.")
                input("\nНажми Enter, чтобы продолжить...")
                continue
                
            idx = int(id_str) - 1
            if 0 <= idx < len(data):
                data[idx]["status"] = "Не забанен"
                data[idx]["unban_at"] = None
                save_data(data)
                print(f"С аккаунта [{id_str}] снят бан.")
            else:
                print("Аккаунт не найден.")
            input("\nНажми Enter, чтобы продолжить...")
                
        elif choice == "4":
            id_str = input("Введи номер аккаунта для удаления: ").strip()
            if not id_str.isdigit():
                print("Нужно ввести номер.")
                input("\nНажми Enter, чтобы продолжить...")
                continue
                
            idx = int(id_str) - 1
            if 0 <= idx < len(data):
                removed = data.pop(idx)
                save_data(data)
                print(f"Аккаунт '{removed['name']}' удален из базы.")
            else:
                print("Аккаунт не найден.")
            input("\nНажми Enter, чтобы продолжить...")
            
        elif choice == "5":
            id_str = input("Введи номер аккаунта: ").strip()
            if not id_str.isdigit():
                print("Нужно ввести номер.")
                input("\nНажми Enter, чтобы продолжить...")
                continue
                
            idx = int(id_str) - 1
            if 0 <= idx < len(data):
                acc = data[idx]
                current_user = acc.get("username", "")
                current_pwd = acc.get("password", "")
                
                print(f"\n--- Данные аккаунта {acc['name']} ---")
                print(f"Логин Steam: {current_user if current_user else '(не указан)'}")
                print(f"Пароль Steam: {current_pwd if current_pwd else '(не указан)'}")
                print("---------------------------------------")
                
                new_user = input("Введи новый логин (или Enter, чтобы оставить старый): ").strip()
                if new_user:
                    acc["username"] = new_user
                    
                new_pwd = input("Введи новый пароль (или Enter, чтобы оставить старый): ").strip()
                if new_pwd:
                    acc["password"] = new_pwd
                    
                if new_user or new_pwd:
                    save_data(data)
                    print("Данные успешно обновлены!")
            else:
                print("Аккаунт с таким номером не найден.")
            input("\nНажми Enter, чтобы продолжить...")
            
        elif choice == "6":
            break
            
        else:
            print("Неизвестная команда.")
            input("\nНажми Enter, чтобы продолжить...")

if __name__ == "__main__":
    main()
