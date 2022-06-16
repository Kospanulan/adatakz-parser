import urllib3
import pandas as pd
from bs4 import BeautifulSoup


def get_all_links(main_page_, http_):
    pages = [main_page_]
    links = set()

    for page in pages:
        r = http_.request('GET', page)
        soup = BeautifulSoup(r.data.decode('utf-8'), features='html.parser')
        for a in soup.find_all('a', href=True):
            link = a['href']
            if "page=" in link and link not in pages:
                pages.append(link)
            elif "show_supplier" in link:
                links.add(link)
            else:
                continue
    return links


def get_all_datas(links):

    df_data = pd.DataFrame({'Наименование на рус. языке': [],
                        'БИН участника': [],
                        'ФИО': [],
                        'ИИН': [],
                        'Полный адрес': []})

    df_keys = ['Наименование на рус. языке', 'БИН участника', 'ФИО', 'ИИН', 'Полный адрес']
    for link in links:

        r = http.request('GET', link)
        soup = BeautifulSoup(r.data.decode('utf-8'), features='html.parser')

        data = dict()
        for a in soup.find_all('tr'):
            try:
                x, y = filter(None, a.text.split('\n'))
            except:
                x = a.text.split('\n')[1]
                y = ''
            finally:
                if x in df_keys:
                    data[x] = y.strip()

        data["Полный адрес"] = list(filter(None, a.text.split('\n')))[2].strip()

        df_data = df_data.append(data, ignore_index=True, sort=False)

    return df_data


retries = urllib3.Retry(total=10,connect=5, read=2, redirect=5)
http = urllib3.PoolManager(retries=retries)

main_page = 'https://www.goszakup.gov.kz/ru/registry/rqc'
links = get_all_links(main_page, http)

writer = pd.ExcelWriter('result_set.xlsx', engine='xlsxwriter')
df_data = get_all_datas(links)

df_data = df_data.drop_duplicates(subset='ИИН', keep='first')

df_data.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()

