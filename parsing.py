import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from db import insert_items, check_uniq_id
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from send_message import send_msg
from urllib.parse import urlparse


searchTags = ['труба', 'швеллер', 'арматура', 'двутавр', 'пруток', 'лента', 'лист', 'отвод', 'уголок',
              'фланец', 'шестигранник', 'рельсы']
stopwords = ['пэ ', 'полиэтилен', 'полипропилен', 'отруб', 'пластмасс', 'сантех', 'канализ', 'полимер', 'канцеляр',
             'медиц']
goodwords = {'алюмин': 'алюминиевая', 'стал': 'стальная', 'мед': 'медная', 'латун': 'латунная', 'бронз': 'бронзовая',
             'титан': 'титановая', 'профильн': 'профильная', 'желез': 'железная'}


currency_dict = {'₽': 'RUB', '€': 'EURO', '$': 'USD'}
sortBy = 'Дате+размещения'
uniq = 0

options = webdriver.FirefoxOptions()
options.set_preference("dom.webdriver.enabled", False)
options.headless = True

driver = webdriver.Firefox(executable_path=r"C:\Users\qwert\PycharmProjects\selenium\geckodriver.exe",
                           options=options)

wait = WebDriverWait(driver, 10)


def check_exists_by_xpath(fromdriver, xpath):
    # Проверка на наличие элемента
    try:
        fromdriver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def parse_item(items, searchtag, page=1):
    global uniq
    print(f"Результатов поиска на странице {page}: {len(items)}")
    for i in items:
        item_link = i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__number']/a").get_attribute(
            "href")
        item_domen = urlparse(item_link).scheme + "://" + urlparse(item_link).netloc
        item_link_short = item_link[len(item_domen):]
        print(item_link)

        item_id = (i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__number']/a").text)[2:]
        if check_uniq_id(item_id) == True:
            uniq += 1
            print(f"Нашел в добавленных в БД: {uniq}")
            if uniq >= 5:
                return
            continue
        item_tags = [searchtag]
        item_law = i.find_element(By.XPATH, ".//div[@class='col-9 p-0 registry-entry__header-top__title text-truncate']").text
        item_law_short = str(item_law[:item_law.find('-ФЗ')]) + '-ФЗ'
        item_status = i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__title text-normal']").text
        item_object = i.find_element(By.XPATH, ".//div[@class='registry-entry__body-value']").text
        item_organization = i.find_element(By.XPATH, ".//div[@class='registry-entry__body-href']/a").text.capitalize()
        if check_exists_by_xpath(i, ".//div[@class='price-block__title' and contains(text(),'Начальная цена')]"):
            item_price_full = i.find_element(By.XPATH,
                                             ".//div[@class='price-block__title' and contains(text(),'Начальная цена')]/following-sibling::div[@class='price-block__value']").text
            item_price_int = float(item_price_full[:-2].replace(' ', '').replace(',', '.'))
            item_price_cur = item_price_full[-1:]
            for c in currency_dict:
                item_price_cur = item_price_cur.replace(c, currency_dict[c])
        else:
            item_price_int = None
            item_price_cur = None
        item_start_date = i.find_element(By.XPATH,
                                         ".//div[@class='data-block__title' and contains(text(),'Размещено')]/following-sibling::div[@class='data-block__value']").text
        item_start_date_obj = datetime.datetime.strptime(str(item_start_date), '%d.%m.%Y')
        if check_exists_by_xpath(i, ".//div[contains(text(),'Окончание подачи заявок')]/following-sibling::div"):
            item_finish_date = i.find_element(By.XPATH,
                                              ".//div[@class='data-block__title' and contains(text(),'Окончание подачи заявок')]/following-sibling::div[@class='data-block__value']").text
            item_finish_date_obj = datetime.datetime.strptime(str(item_finish_date), '%d.%m.%Y')
        else:
            item_finish_date_obj = None
        # переключение на вкладку с тендером
        original_window = driver.current_window_handle
        i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__number']/a").click()
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                time.sleep(2)
                break
        if check_exists_by_xpath(driver,
                                 ".//span[@class='section__title' and contains(text(),'Регион')]"):
            item_region = driver.find_element(By.XPATH,
                                              ".//span[@class='section__title' and contains(text(),'Регион')]/following-sibling::span[@class='section__info']").text.capitalize()
        elif check_exists_by_xpath(driver, ".//div[contains(text(),'Почтовый адрес')]"):
            item_region = driver.find_element(By.XPATH,
                                              ".//div[contains(text(),'Почтовый адрес')]/following-sibling::div").text.capitalize()
        else:
            item_region = None

        have_stopword = False
        have_goodword = False

        # Проверка на наличие вкладки "Список лотов" и "Информация об объекте закупки"
        spisok_lotov_tab = check_exists_by_xpath(driver, '//a[contains(text(),"Список лотов")]')
        information_about_object = check_exists_by_xpath(driver,
                                                         '//h2[contains(text(),"Информация об объекте закупки")]')
        if information_about_object:
            information_about_object_table = driver.find_element(By.XPATH, "//h2[contains(text(),'Информация об "
                                                                           "объекте закупки')]/following-sibling::div")
            for goodword in goodwords.keys():
                if goodword in information_about_object_table.text.lower():
                    have_goodword = True
                    item_tags.append(goodwords[goodword])
            for stopword in stopwords:
                if stopword in information_about_object_table.text.lower():
                    have_stopword = True
                    break

        elif spisok_lotov_tab:
            driver.find_element(By.XPATH, "//a[contains(text(),'Список лотов')]").click()
            table_spisok_lotov = driver.find_element(By.XPATH, "//div[@class='card-common-content']")
            for goodword in goodwords.keys():
                if goodword in table_spisok_lotov.text.lower():
                    have_goodword = True
                    item_tags.append(goodwords[goodword])
            for stopword in stopwords:
                if stopword in table_spisok_lotov.text.lower():
                    have_stopword = True
                    break
        else:
            item_object_low = item_object.lower()
            for goodword in goodwords.keys():
                if goodword in item_object_low:
                    item_tags.append(goodwords[goodword])
                    have_stopword = True
            for stopword in stopwords:
                if stopword in item_object_low:
                    have_stopword = True
                    break

        if have_stopword:
            driver.close()
            driver.switch_to.window(original_window)
            continue
        elif have_goodword:
            # Отправка в БД
            item_publication_date = datetime.datetime.now()
            insert_items(item_id, item_status, item_object, item_organization, item_price_int, item_price_int,
                         item_price_cur, item_start_date_obj, item_finish_date_obj, item_link_short, item_tags,
                         item_region, item_publication_date, item_domen, item_law_short)
            # Отправка в Telegram
            print("Отправка")

            tg_msg = f"<b>Тендер:</b> № {item_id}\n" \
                     f"<b>Закон:</b> {item_law_short}"
            try:
                tg_msg += '\n<b>Начальная цена:</b> {:,.2f} {}'.format(item_price_int, item_price_full[-1:]).replace(',', ' ')
            except:
                pass
            # if 'item_price_full' in locals():
            #     tg_msg += '\n<b>Начальная цена:</b> {:,.2f} {}'.format(item_price_int, item_price_full[-1:]).replace(',', ' ')
            tg_msg += f"\n<b>Объект закупки:</b> {item_object if len(item_object)<100 else item_object[:100] + '...'}"
            # if 'item_finish_date' in locals():
            #     tg_msg += f"\n<b>Окончание подачи заявок:</b> {item_finish_date}"
            try:
                tg_msg += f"\n<b>Окончание подачи заявок:</b> {item_finish_date}"
            except:
                pass
            tg_msg += f"\n<a href='https://metalmarket.pro/tenders'>Ссылка на тендеры</a>"

            # send_msg(tg_msg)

            driver.close()
            driver.switch_to.window(original_window)
        else:
            print("Ничего не нашел")
            driver.close()
            driver.switch_to.window(original_window)
            continue


def parse_page():
    for goodword in goodwords:
        for searchtag in searchTags:
            url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=поставка+{searchtag}+{goodword}" \
                  f"&morphology=on&search-filter={sortBy}&sortDirection=false&recordsPerPage=_50&af=on&ca=on"

            try:
                driver.get(url)
                print(f"Ищем: {searchtag}")
                if check_exists_by_xpath(driver, "//div[@class='paginator align-self-center m-0']/ul/li/a"):
                    pages = driver.find_elements(By.XPATH, "//div[@class='paginator align-self-center m-0']/ul/li/a")
                    last_page_num = int(pages[-1].get_attribute("data-pagenumber"))
                else:
                    last_page_num = 1
                print(f"Всего страниц: {last_page_num}")

                for page in range(1, last_page_num + 1):
                    print(f'Переход на страницу {url}&pageNumber={page}')
                    if page == 1:
                        items = driver.find_elements(By.XPATH, "//div[@class='search-registry-entrys-block']/div")
                        parse_item(items, searchtag)
                    else:
                        driver.get(f"{url}&pageNumber={page}")
                        time.sleep(5)
                        items = driver.find_elements(By.XPATH, "//div[@class='search-registry-entrys-block']/div")
                        parse_item(items, searchtag, page)
                    if uniq >= 5:
                        break
            except Exception as ex:
                print(ex)
            finally:
                print(20 * '-')
                print(f'Парсинг ключа {searchtag} завершен')
                print(20 * '-')
    print(f'Парсинг завершен')
    driver.close()
    driver.quit()
