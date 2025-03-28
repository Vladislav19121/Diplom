# from django import template
# import requests
# import json
# register = template.Library()

# @register.filter(name='to_usd')
# def to_usd(price, rate):
#     try:
#         usd_value = round(float(price)/float(rate), 2)
#         return f"${usd_value:,.2f}"
#     except (ValueError, TypeError):
#         return "Ошибка"
    
# @register.simple_tag
# def get_exchange_rate():
#     try:
#         url = 'https://belarusbank.by/api/kurs_deals'
#         response = requests.get(url)
#         response.raise_for_status()
        
#         data = response.json()

#         exchange_rate = data[0]['USD_OUT']
#         return float(exchange_rate)
    
#     except requests.exceptions.RequestException as e:
#         print(f"Ошибка при получении курса: {e}")
#         return None
#     except (KeyError, IndexError, TypeError) as e:
#         print(f"Ошибка при разборе JSON: {e}")
#         return None