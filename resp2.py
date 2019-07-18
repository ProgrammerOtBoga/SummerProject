import requests

# Готовим запрос.
geocoder_request = "https://us.api.blizzard.com/hearthstone/cards?locale=us_us&class=warrior&access_token=USbWNxZHXsE2yMMmu87igbrU61StUZuPfU"

# Выполняем запрос.
response = None
try:
    response = requests.get(geocoder_request)
    if response:
        # Запрос успешно выполнен, печатаем полученные данные.
        print(response.content)
    else:
        # Произошла ошибка выполнения запроса. Обрабатываем http-статус.
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
except:
    print("Запрос не удалось выполнить. Проверьте подключение к сети Интернет.")