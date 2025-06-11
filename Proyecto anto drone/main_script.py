def run(alias):
    alias = str(alias).strip()

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://trdnetwork.sg/login")
        wait = WebDriverWait(driver, 15)

        # --- LOGIN PRINCIPAL ---
        print("🔐 Iniciando sesión en portal principal...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Please enter the name']"))).send_keys("operator01")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Please enter the password']"))).send_keys("admin@123")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.login-btn"))).click()

        # --- ENTRAR AL BOTÓN 'ONLINE' ---
        print("📡 Entrando a la sección 'ONLINE'...")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.onlineCount.siteCount"))).click()
        time.sleep(3)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.ant-table-row")))
        rows = driver.find_elements(By.CSS_SELECTOR, "tr.ant-table-row")
        found = False

        print(f"🔍 Buscando subsite '{alias}'...")

        for row in rows:
            try:
                alias_span = row.find_element(By.CSS_SELECTOR, "td.aliasName span")
                alias_text = alias_span.text.strip()

                if alias_text == alias:
                    print(f"✅ Subsite encontrado: {alias_text}")
                    row.find_element(By.CSS_SELECTOR, "div.enterSubsite").click()

                    wait.until(lambda d: len(d.window_handles) > 1)
                    original_window = driver.current_window_handle

                    for handle in driver.window_handles:
                        if handle != original_window:
                            driver.close()
                            driver.switch_to.window(handle)
                            break

                    wait.until(EC.url_contains("https://trdnetwork.sg:33022/device/"))
                    print(f"🌐 Subsite cargado: {driver.current_url}")
                    found = True
                    break

            except Exception as e:
                print(f"⚠️ Error al procesar una fila: {e}")
                continue

        if not found:
            print("❌ No se encontró el subsite deseado.")
            return

        # --- LOGIN SUBSITE ---
        print("🔐 Iniciando sesión en subsite...")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys("admin")
        wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys("trdadmin12345")

        # --- AUTOMATIZAR SLIDER ---
        print("🔄 Automatizando slider...")
        slider_handle = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.drag .btn")))
        action = ActionChains(driver).click_and_hold(slider_handle).pause(0.2)

        for _ in range(40):
            action.move_by_offset(10, 0).pause(0.05)
        action.release().perform()

        print("✅ Slider deslizado.")
        wait.until(lambda d: "Ok" in d.find_element(By.CSS_SELECTOR, "div.drag .text").text)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.lBtn"))).click()
        print("🚪 Acceso al subsite exitoso.")

        input("Presiona Enter para cerrar el navegador...")

    finally:
        driver.quit()

