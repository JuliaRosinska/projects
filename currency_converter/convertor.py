import requests
from key import *

api_key = key
url = "https://currency-converter5.p.rapidapi.com/currency/convert"
url_list = "https://currency-converter5.p.rapidapi.com/currency/list"

def get_available_curr():
    headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "currency-converter5.p.rapidapi.com"
            }

    response = requests.request("GET", url_list, headers=headers)
    available_curr = response.json()
    return list(available_curr["currencies"].keys())

def currency_convert(from_currency, to_currency, amount):
    querystring = {"format":"json","from":from_currency,"to":to_currency,"amount":amount}

    headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "currency-converter5.p.rapidapi.com"
            }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data["rates"][to_currency]["rate_for_amount"]


def input_currency(available_curr):
    print("Welcome! Enter your currency:")
    from_currency = input().upper()

    print("Enter the currency you want to convert:")
    to_currency = input().upper()

    for value in (from_currency, to_currency):
        if value == "" or None:
            print("There is empty string! Please try again.")
            return input_currency(available_curr)
        if not value.isalpha():
            print("There is incorect currency! Please try again.")
            return input_currency(available_curr)
        if len(value) != 3:
            print("There is incorect currency! Please try again.")
            return input_currency(available_curr)
        if value not in available_curr:
            print("This currency doesn't available! Please try again.")
            return input_currency(available_curr)

    return from_currency, to_currency


def input_amount():
    print("Enter the amount:")
    amount = input()
    if amount == "" or None:
        print("There is empty string. Please try again!")
        return input_amount()
    if not amount.isdigit():
        print("Amount can contains only digits. Please try again!")
        return input_amount()
    if len(amount) > 50:
        print("Amount can contains max 50 digits. Please try again!")
        return input_amount()
    if amount[0] == "0":
        print("Amount can't start with 0. Please try again!")
        return input_amount()
    return amount


def main():
    available_curr = get_available_curr()
    from_currency, to_currency = input_currency(available_curr)
    amount = input_amount()

    rate_for_amount = currency_convert(from_currency, to_currency, amount)

    print("-----------------------")
    print(f"{amount} {from_currency} -> {round(float(rate_for_amount), 2)} {to_currency}")

if __name__ == "__main__":
    main()
