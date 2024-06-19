from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract import abi, contractadress

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contractadress, abi=abi)

def auth():
    public_key = input("Введите публичный ключ: ")
    password = input("Введите пароль: ")
    try:
        w3.geth.personal.unlock_account(public_key, password)
        print("Вы успешно авторизировались")
        return public_key
    except Exception as e:
        print(e)
        return None

def registration():
    password = input("Введите пароль: ")
    password2 = input("Повторите пароль: ")
    if password2 == password:
        address = w3.geth.personal.new_account(password)
        print(f"Адрес нового аккаунта: {address}")
    else:
        print("Пароли не совпадают, повторите попытку регистрации")

def create_estate(account: str):
    size = int(input("Введите размер недвижимости: "))
    photo = input("Введите хеш изображения: ")
    rooms = int(input("Введите количество комнат: "))
    est = int(input("Выберите тип недвижимости:\n1. Коттедж\n2. Квартира\n3. Дом\n")) - 1
    tx_hash = contract.functions.createEstate(size, photo, rooms, est).transact({
        "from": account
    })
    print(f"Недвижимость создана с хешем транзакции {tx_hash.hex()}")


def create_ad(account: str):
    est = int(input("Введите ID вашей недвижимости: "))
    price = int(input("Введите стоимость недвижимости: "))
    ad = contract.functions.createAd(est, price).transact({
        "from": account
    })
    print(f"Объявление создано с хешем транзакции {ad.hex()}")

def deposit(account: str):
    amount = int(input("Введите сумму для пополнения: "))
    try:
        tx_hash = contract.functions.depos().transact({
            "from": account,
            "value": amount
        })
        print(f"Баланс успешно пополнен. Хеш транзакции: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка при отправке эфира: {e}")

def withdraw(account: str):
    amount = int(input("Сумма для вывода: "))
    tx_hash = contract.functions.withdraw(amount).transact({
        "from": account
    })
    print(f"Успешно выведено. Хеш транзакции: {tx_hash.hex()}")

def get_balance():
    balance = contract.functions.getBalance().call()
    print(f"Баланс контракта: {balance}")


def update_estate(account: str):
    estate_id = int(input("Введите ID недвижимости для изменения статуса: "))
    is_active = input("Активировать недвижимость? (да/нет): ").lower() == "да"
    tx_hash = contract.functions.updateEstateStatus(estate_id, is_active).transact({
        "from": account
    })
    print(f"Статус недвижимости обновлен. Хеш транзакции: {tx_hash.hex()}")

def update_ad(account: str):
    ad_id = int(input("Введите ID объявления для изменения статуса: "))
    new_status = int(input("Выберите новый статус:\n1. Открыто\n2. Закрыто\n")) - 1
    tx_hash = contract.functions.UpdateAddStatus(ad_id, new_status).transact({
        "from": account
    })
    print(f"Статус объявления обновлен. Хеш транзакции: {tx_hash.hex()}")


def get_ads_count():
    try:
        ad_count = 0
        while True:
            contract.functions.ads(ad_count).call()
            ad_count += 1
    except Exception as e:
        pass
    return ad_count

def buy_estate(account: str):
    ad_count = get_ads_count()
    ads = []
    for i in range(ad_count):
        ad = contract.functions.ads(i).call()
        ads.append(ad)

    print(*ads, sep="\n")
    ad_id = int(input("Введите ID объявления для покупки: "))
    price = ads[ad_id][2]

    try:
        # Покупка недвижимости
        tx_hash = contract.functions.BuyEstate(ad_id).transact({
            "from": account,
            "value": price
        })
        print(f"Недвижимость куплена. Хеш транзакции: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка при покупке недвижимости: {e}")
def main():
    account = ""
    is_auth = False
    while True:
        try:
            if not is_auth:
                choice = input("Выберите:\n1. Авторизация\n2. Регистрация\n")
                match choice:
                    case "1":
                        account = auth()
                        if account:
                            is_auth = True
                    case "2":
                        registration()
            else:
                choice = input(
                    "Выберите:\n1. Пополнить баланс контракта\n2. Вывод денег с контракта\n3. Узнать баланс\n4. Добавить недвижимость\n5. Создать объявление\n6. Изменить статус недвижимости\n7. Изменить статус объявления\n8. Купить недвижимость\n9. Выход\n")
                match choice:
                    case "1":
                        deposit(account)
                    case "2":
                        withdraw(account)
                    case "3":
                        get_balance()
                    case "4":
                        create_estate(account)
                    case "5":
                        create_ad(account)
                    case "6":
                        update_estate(account)
                    case "7":
                        update_ad(account)
                    case "8":
                        buy_estate(account)
                    case "9":
                        is_auth = False
                    case _:
                        print("Некорректное значение")
        except Exception as e:
            print(f"Ошибка при транзакции: {e}")
            continue

if __name__ == '__main__':
    main()