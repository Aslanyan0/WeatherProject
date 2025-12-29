from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


def test_today_button_functionality():
    driver = webdriver.Firefox()
    driver.get("http://127.0.0.1:8000")
    city_input = driver.find_element(By.ID, "searchInput")
    city_input.send_keys("a1b2c3d4")
    city_input.submit()

    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "search-error"))
    )
    assert error.is_displayed()
    driver.quit()


if __name__ == "__main__":
    test_today_button_functionality()
