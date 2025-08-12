import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import chardet


def get_dates(n):
    today = datetime.now()
    dates = []
    for i in range(n):
        date = today - timedelta(days=i)
        dates.append(date)
    return dates


def cbr_data(date):
    url_date = date.strftime("%d/%m/%Y")
    url = f"http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={url_date}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        encoding = chardet.detect(response.content)['encoding']
        content = response.content.decode(encoding or 'windows-1251')

        root = ET.fromstring(content)

        result = []
        for valute in root.findall('Valute'):
            name = valute.find('Name').text
            char_code = valute.find('CharCode').text
            vunit_rate = float(valute.find('VunitRate').text.replace(',', '.'))
            result.append({
                'name': name,
                'code': char_code,
                'rate': vunit_rate,
                'date': date.date()
            })
        return result

    except Exception as e:
        print(f"Ошибка при загрузке данных за {url_date}: {e}")
        return []


def main():
    all_rates = []

    dates = get_dates(90)

    for date in dates:
        data = cbr_data(date)
        if data:
            all_rates.extend(data)

    if not all_rates:
        print("Нет загруженных данных.")
        return

    max_rate = max(all_rates, key=lambda x: x['rate'])
    min_rate = min(all_rates, key=lambda x: x['rate'])
    avg_rate = sum(r['rate'] for r in all_rates) / len(all_rates)

    print("Анализ завершён:")
    print(f"Максимальный курс: {max_rate['rate']} RUB — {max_rate['name']} ({max_rate['code']}) на дату: {max_rate['date']}")
    print(f"Минимальный курс: {min_rate['rate']} RUB — {min_rate['name']} ({min_rate['code']}) на дату: {min_rate['date']}")
    print(f"Средний курс рубля за весь период: {avg_rate:.4f} RUB")


if __name__ == '__main__':
    main()