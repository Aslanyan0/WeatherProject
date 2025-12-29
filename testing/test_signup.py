from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver


def test_signup_existing_email():
    driver = webdriver.Firefox()
    driver.get("http://127.0.0.1:8000/accounts/signup/")

    # Заполняем поля
    driver.find_element(By.ID, "id_username").send_keys("aram0")
    driver.find_element(By.ID, "id_email").send_keys("aslanyancaram1@gmail.com")
    driver.find_element(By.ID, "id_password").send_keys("a1b2c3d4")

    # Отправляем форму
    driver.find_element(By.TAG_NAME, "form").submit()

    # Ждём появления ошибки
    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "flash-message"))
    )

    # Проверка текста ошибки
    assert error.is_displayed()
    assert "email is already in use" in error.text.lower()

    driver.quit()


if __name__ == "__main__":
    test_signup_existing_email()
