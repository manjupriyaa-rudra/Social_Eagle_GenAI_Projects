from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import traceback

driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 25)

# Generate random number for password uniqueness
unique_number = random.randint(1000, 9999)
new_password = f"mnju@{unique_number}"

try:
    # 1. Go to URL
    driver.get("https://opensource-demo.orangehrmlive.com/")
    print("[SUCCESS] Opened OrangeHRM site")

    # 2. Login
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_field = driver.find_element(By.NAME, "password")

    username_field.send_keys("Admin")
    password_field.send_keys("admin123")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    print("[SUCCESS] Logged in successfully")

    # 3. Handle popup if any
    time.sleep(2)
    try:
        popup = driver.find_element(By.XPATH, "//button[text()='Accept']")
        popup.click()
        print("[INFO] Popup closed")
    except:
        print("[INFO] No popup found")

    # 4. Click Admin menu
    admin_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Admin']")))
    admin_btn.click()
    print("[SUCCESS] Clicked Admin menu")

    # 5. Wait for Admin page to load (heading + table)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h5[text()='System Users']")))
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-table-body")))
    time.sleep(1)  # small buffer

    # 6. Search for "Admin" user
    # Use retry to handle dynamic loading issues
    for attempt in range(3):
        try:
            search_username_input = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[1]/div[2]/form/div[1]/div/div[1]/div/div[2]/input')))
                
            search_username_input.clear()
            search_username_input.send_keys("Admin")

            driver.find_element(By.XPATH, "//button[.=' Search ']").click()
            print("[SUCCESS] Search button clicked")
            break
        except:
            print("[INFO] Retry locating Username field...")
            time.sleep(2)
    else:
        raise Exception("Could not locate Username search field after multiple attempts")

    # 7. Click Edit on first row
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-table-body")))
    time.sleep(1)
    edit_button = wait.until(EC.element_to_be_clickable(
        #(By.XPATH, "(//div[@class='oxd-table-body']//button[contains(@class,'edit')])[1]")))
        (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div[2]/div[3]/div/div[2]/div[1]/div/div[6]/div/button[2]')))
    edit_button.click()
    print("[SUCCESS] Edit button clicked")

    # 8. Wait for Edit User page to load
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h6[text()='Edit User']")))
    print("[INFO] Edit User page loaded")

    # 9. Enable Change Password
    change_pwd_checkbox = wait.until(EC.element_to_be_clickable(
        #(By.XPATH, "//label[text()='Change Password?']/following::span/input[1]")))
        #(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div/form/div[1]/div/div[5]/div/div[2]/div/label/span/i')))
        (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/div/div/form/div[1]/div/div[5]/div/div[2]/div/label/span')))
    change_pwd_checkbox.click()
    print("[INFO] Change Password enabled")

    # 10. Set new password
    pwd_field = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//label[text()='Password']/following::input[1]")))
    confirm_pwd_field = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//label[text()='Confirm Password']/following::input[1]")))

    pwd_field.clear()
    pwd_field.send_keys(new_password)
    confirm_pwd_field.clear()
    confirm_pwd_field.send_keys(new_password)
    print(f"[SUCCESS] Password set to: {new_password}")

    # 11. Save
    save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.=' Save ']")))
    save_button.click()
    print("[SUCCESS] Save button clicked")

    # 12. Capture success message
    success_msg = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//p[contains(@class,'oxd-toast-content-text')]")))
    print("[SUCCESS MESSAGE]:", success_msg.text)

except Exception as e:
    print("[FAILURE] Automation failed")
    traceback.print_exc()

finally:
    time.sleep(5)
    driver.quit()
