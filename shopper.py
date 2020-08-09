from selenium import webdriver
import time,sys,json
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException,ElementNotSelectableException, TimeoutException
from win10toast import ToastNotifier
import random


def login(client,credentials):
    driver.get('https://www.enzona.net/auth/enzona')
    done = False

    wait = WebDriverWait(driver, 10, poll_frequency=1,
                         ignored_exceptions=[NoSuchElementException, ElementNotSelectableException])

    username_field = wait.until(lambda driver: client.find_element_by_id('username'))

    username_field.send_keys(credentials['username'])

    client.find_element_by_class_name('enzona-btn').click()

    password_field = wait.until(lambda driver: client.find_element_by_id('tpassword'))

    password_field.send_keys(credentials['password'])

    client.find_element_by_class_name('enzona-btn').click()

    verification_field = client.find_element_by_css_selector('input[name = token]')

    while not done:

        try:

            verificacion = input("Introduzca el codigo de verificacion\n")

            verification_field.send_keys(verificacion)
            client.find_element_by_css_selector('.enzona-btn').click()

            wait_for_ez = WebDriverWait(driver, 3, poll_frequency=1)

            password_field = wait.until(lambda driver: client.find_element_by_id('ez-perfil-label'))

            done = True

        except NoSuchElementException as e:
            print("Introdujo un codigo erroneo\n")
            continue

    driver.get('https://5tay42.enzona.net/mi-cuenta')


def pay(client,credentials):

    wait = WebDriverWait(driver, 10, poll_frequency=1,
                         ignored_exceptions=[NoSuchElementException, ElementNotSelectableException])

    driver.get('https://5tay42.enzona.net/pedido-rapido')

    try:
        client.find_element_by_css_selector('#cgv').click()

    except NoSuchElementException as e:
        print('No hay ningun producto en el carrito')
        raise e


    try:
        wait.until(lambda client: client.find_element_by_css_selector('p.payment_module a'))
        client.find_element_by_css_selector('p.payment_module a').click()

    except NoSuchElementException as e:
        print('Hubo un error al iniciar el pago, no aparecio el boton')
        raise e

    # dentro de enzona

    wait.until(lambda client: client.find_element_by_class_name('btn-lg'))
    client.find_element_by_class_name('btn-lg').click()


    wait.until(lambda client: client.find_element_by_class_name('pincode-input-container'))
    pin_modules = client.find_elements_by_css_selector('div.pincode-input-container input.pincode-input-text')

    length = len(pin_modules)
    i = 0
    while i < length:

        pin_modules[i].send_keys(credentials['pin'][i])
        i += 1

    client.find_element_by_class_name('btn-lg').click()


def add_to_cart(web_driver,product):

    try:
        product_buy_button = product.find_element_by_css_selector("a[title='Comprar']").click()

        wait = WebDriverWait(driver, 10, poll_frequency=1,
                             ignored_exceptions=[NoSuchElementException, ElementNotSelectableException])

        wait.until(lambda client: web_driver.find_element_by_css_selector('#layer_cart_product_quantity').text == '1')

    except Exception as e:
        print('El producto parece estar no disponible')
        raise e


def hunt_products(web_driver):
    done = False

    while not done:
        try:

            web_driver.get('https://5tay42.enzona.net/nuevos-productos')
            done = True

        except Exception as e:
            web_driver.close()
            raise e

    while True:

        if element_exists(web_driver,'.product_list'):
            toaster = ToastNotifier()
            toaster.show_toast("5TA", "Cambiaron los productos en existencia")

            products = driver.find_elements_by_css_selector("ul.product_list li")

            for product in products:
                if "alimento" in product.find_element_by_css_selector('div div a.product-name').text.lower() or "aseo" in product.find_element_by_css_selector('div div a.product-name').text.lower():
                    print(product.find_element_by_css_selector('div div a.product-name').text.lower())
                    # print(product.find_element_by_css_selector("a[title='Comprar']").get_attribute('title'))

                    print(product.find_element_by_css_selector("a[title='Comprar']").get_attribute('href'))

                    add_to_cart(web_driver,product)
                    return True

        wait_period = random.randint(5, 8)
        print(f'\n\n---Esperando {wait_period} segundos----')
        time.sleep(wait_period)

        try:
            driver.get('https://5tay42.enzona.net/nuevos-productos')
        except TimeoutException:
            break


def element_exists(web_driver,element_selector):

    try:
        if web_driver.find_element_by_css_selector(element_selector):
            return True

    except Exception:
        return False


user = sys.argv[1]

credentials_file = open(f'./{user}','r')
credentials = json.load(credentials_file)

opts = Options()

opts.add_argument('log-level=3')
opts.add_argument('--proxy-server=')

driver = webdriver.Chrome(executable_path='D:\\Installers\\Dev\\chromedriver_win32\\chromedriver.exe', options=opts)
driver.set_window_size(1366,768)

login(driver,credentials)

if hunt_products(driver):
    pay(driver,credentials)

print("Done")
