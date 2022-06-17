from selenium.webdriver import Chrome
from thread_tools import res_pool_parallel

driver = Chrome()


def open_urls_in_Chrome(url_list):
    global driver
    res_pool_parallel(
        driver.execute_script,
        [(f"window.open('{url}')",) for url in url_list]
    )


if __name__ == '__main__':
    """ test """
    # open_urls_in_Chrome(["https://vgmdb.net/artist/"+str(num) for num in range(100, 130)])
