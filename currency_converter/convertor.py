import requests
from key import *

api_key = key
url = "https://currency-converter5.p.rapidapi.com/currency/convert"

def currency_convert(from_currency, to_currency, amount):
    querystring = {"format":"json","from":from_currency,"to":to_currency,"amount":amount}

    headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "currency-converter5.p.rapidapi.com"
            }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    return data["rates"][to_currency]["rate_for_amount"]

def input_check(input):
    if input == "" or None:
        print("There is empty string! Please try again.")
        return main()
    if not input.isalpha():
        print("There is incorect currency! Please try again.")

def main():
    print("Welcome! Enter your currency:")
    from_currency = input().upper()
    input_check(from_currency)

    print("Enter the currency you want to convert:")
    to_currency = input().upper()
    input_check(to_currency)

    print("Enter the amount:")
    amount = input().upper()
    input_check(amount)

    rate_for_amount = currency_convert(from_currency, to_currency, amount)

    print("-----------------------")
    print(f"{amount} {from_currency} -> {round(float(rate_for_amount), 2)} {to_currency}")

if __name__ == "__main__":
    main()
