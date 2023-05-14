import requests
from bs4 import BeautifulSoup
import json

# Ссылка на страницу поиска вакансий на HeadHunter
url = 'https://hh.ru/search/vacancy?text=Python&area=1&area=2&clusters=true&enable_snippets=true'

# Список ключевых слов для поиска в описании вакансии
keywords = ['Django', 'Flask']

# Функция для получения списка вакансий
def get_vacancies():
    vacancies = []
    session = requests.Session()
    req = session.get(url)
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, 'html.parser')
        divs = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
        for div in divs:
            title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
            href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
            employer = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
            location = div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
            salary = div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary is None:
                salargity_min = None
                salary_max = None
            else:
                salary_text = salary.getText().replace('\u202f', '').replace('-', ' ')
                salary_list = salary_text.split(' ')
                if salary_list[0] == 'до':
                    salary_min = None
                    salary_max = int(salary_list[1] + salary_list[2])
                elif salary_list[0] == 'от':
                    salary_min = int(salary_list[1] + salary_list[2])
                    salary_max = None
                else:
                    salary_min = int(salary_list[0] + salary_list[1])
                    salary_max = int(salary_list[3] + salary_list[4])
            vacancy = {'title': title, 'href': href, 'employer': employer, 'location': location, 'salary_min': salary_min, 'salary_max': salary_max}
            vacancies.append(vacancy)
    return vacancies

# Функция для фильтрации списка вакансий по ключевым словам
def filter_vacancies(vacancies):
    filtered_vacancies = []
    for vacancy in vacancies:
        req = requests.get(vacancy['href'])
        if req.status_code == 200:
            soup = BeautifulSoup(req.content, 'html.parser')
            description = soup.find('div', attrs={'class': 'vacancy-description'})
            if description is not None:
                description_text = description.getText().lower()
                if all(keyword.lower() in description_text for keyword in keywords):
                    filtered_vacancies.append(vacancy)
    return filtered_vacancies

# Получаем списокакансий и фильтруем его по ключевым словам
vacancies = get_vacancies()
filtered_vacancies = filter_vacancies(vacancies)

# Записываем результат в файл в формате json
with open('hh_vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_vacancies, f, ensure_ascii=False, indent=4)
