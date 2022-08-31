import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from db import insert_items, check_uniq_id
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from send_message import send_message, users_id_list


searchTags = ['труба', 'квадрат', 'швеллер']
stopwords = ['пэ', 'полиэтилен', 'полипропилен', 'отруб', 'пластмасс']
goodwords = ['алюмин', 'cтал', 'мед', 'латун', 'бронз', 'титан']
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
    try:
        fromdriver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def parse_item(items, searchTag, page=1):
    global uniq
    print(f"Результатов поиска на странице {page}: {len(items)}")
    for i in items:
        item_id = (i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__number']/a").text)[2:]
        if check_uniq_id(item_id) == True:
            uniq += 1
            print(f"Подряд нашел добавленных в БД: {uniq}")
            if uniq >= 5:
                return
            continue
        uniq = 0
        item_link = i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__number']/a").get_attribute(
            "href")
        item_link_short = item_link[22:]
        item_status = i.find_element(By.XPATH, ".//div[@class='registry-entry__header-mid__title text-normal']").text
        item_object = i.find_element(By.XPATH, ".//div[@class='registry-entry__body-value']").text
        item_organization = i.find_element(By.XPATH, ".//div[@class='registry-entry__body-href']/a").text
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

        print(item_link)

        if check_exists_by_xpath(driver,
                                 ".//span[@class='section__title' and contains(text(),'Регион')]"):
            item_region = driver.find_element(By.XPATH,
                                              ".//span[@class='section__title' and contains(text(),'Регион')]/following-sibling::span[@class='section__info']").text
        elif check_exists_by_xpath(driver, ".//div[contains(text(),'Почтовый адрес')]"):
            item_region = driver.find_element(By.XPATH,
                                              ".//div[contains(text(),'Почтовый адрес')]/following-sibling::div").text
        else:
            item_region = None

        have_stopword = False
        have_goodword = False
        spisok_lotov_tab = check_exists_by_xpath(driver, '//a[contains(text(),"Список лотов")]')
        information_about_object = check_exists_by_xpath(driver,
                                                         '//h2[contains(text(),"Информация об объекте закупки")]')

        if spisok_lotov_tab:
            print("Есть вкладка 'Список лотов'")
            driver.find_element(By.XPATH, "//a[contains(text(),'Список лотов')]").click()
            time.sleep(0.5)
            table_spisok_lotov = driver.find_element(By.XPATH, "//div[@class='card-common-content']")
            for goodword in goodwords:
                if str(table_spisok_lotov.text).find(goodword):
                    print("Нашел гудслово1")
                    have_goodword = True
                    break
            for stopword in stopwords:
                if check_exists_by_xpath(table_spisok_lotov, ".//*[contains(text(),'" + stopword + "')]"):
                    print("Нашел стопслово1")
                    have_stopword = True
                    break

        elif information_about_object:
            print("Есть таблица 'Информация об объекте закупки'")
            information_about_object_table = driver.find_element(By.XPATH, "//h2[contains(text(),'Информация об "
                                                                           "объекте закупки')]/following-sibling::div")
            for goodword in goodwords:
                if str(information_about_object_table.text).find(goodword):
                    print("Нашел гудслово2")
                    have_goodword = True
                    break
            for stopword in stopwords:
                if check_exists_by_xpath(information_about_object_table, ".//*[contains(text(),'" + stopword + "')]"):
                    print("Нашел стопслово2")
                    have_stopword = True
                    break
        else:
            print("Нет спец блоков")
            for goodword in goodwords:
                if str(item_object).find(goodword):
                    print("Нашел гудслово3")
                    have_goodword = True
                    break
            for stopword in stopwords:
                if str(item_object).find(stopword):
                    print("Нашел стопслово3")
                    have_stopword = True
                    break

        if have_stopword:
            driver.close()
            driver.switch_to.window(original_window)
            continue
        elif have_goodword:
            print("Отправка в БД")
            insert_items(item_id, item_status, item_object, item_organization, item_price_int, item_price_int,
                         item_price_cur, item_start_date_obj, item_finish_date_obj, item_link_short, [searchTag],
                         item_region)

            print("Отправка в телегу")
            for user in users_id_list:
                send_message(user, f"{item_link}")

            driver.close()
            driver.switch_to.window(original_window)
        else:
            print("Ничего не нашел")
            driver.close()
            driver.switch_to.window(original_window)
            continue


def parse_page():
    for searchTag in searchTags:
        url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=поставка+{searchTag}&morphology=on" \
              f"&search-filter={sortBy}&sortDirection=false&recordsPerPage=_50&af=on&ca=on"

        try:
            driver.get(url)
            print(f"Ищем: {searchTag}")

            pages = driver.find_elements(By.XPATH, "//div[@class='paginator align-self-center m-0']/ul/li/a")
            last_page_num = int(pages[-1].get_attribute("data-pagenumber"))
            print(f"Всего страниц: {last_page_num}")

            for page in range(1, last_page_num + 1):
                print(f'Переход на страницу {url}&pageNumber={page}')
                if page == 1:
                    items = driver.find_elements(By.XPATH, "//div[@class='search-registry-entrys-block']/div")
                    parse_item(items, searchTag)
                else:
                    driver.get(f"{url}&pageNumber={page}")
                    time.sleep(5)
                    items = driver.find_elements(By.XPATH, "//div[@class='search-registry-entrys-block']/div")
                    parse_item(items, searchTag, page)
                if uniq >= 5:
                    return
        except Exception as ex:
            print(ex)
        finally:
            print(20 * '-')
            print('Парсинг завершен')
            print(20 * '-')
            driver.close()
            driver.quit()
