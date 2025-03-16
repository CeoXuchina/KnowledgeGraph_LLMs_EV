# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
#
# # 设置 ChromeDriver 路径
# chrome_driver_path = "F:\\chromedriver\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
# service = Service(executable_path=chrome_driver_path)
#
# # 启动浏览器设置
# options = Options()
# options.add_argument("--headless")  # 设置为无头模式（可选）
# driver = webdriver.Chrome(service=service, options=options)
#
# # 定义要爬取的网址
# url = "https://ev-database.org/car/1782/BYD-ATTO-3"
#
# # 打开网页
# driver.get(url)
# time.sleep(3)  # 等待页面初始加载
#
# # 滚动页面以触发所有内容加载
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# time.sleep(3)  # 等待内容加载
#
# # 抓取数据函数
# def extract_data():
#     data = {}
#
#     # 1. 基本信息
#     try:
#         data["Model"] = driver.execute_script("return document.querySelector('.sub-header h1').innerText;")
#         data["Available_Since"] = driver.execute_script("return document.querySelector('.sub-header span').innerText;")
#     except Exception as e:
#         print(f"Error retrieving model or availability: {e}")
#
#     # 2. 价格信息
#     try:
#         price_info_script = driver.execute_script("return document.querySelector('#pricing').innerText;")
#         data["Price"] = price_info_script if price_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving price data: {e}")
#
#     # 3. 电池信息
#     try:
#         battery_info_script = driver.execute_script("return document.querySelector('#battery').innerText;")
#         data["Battery"] = battery_info_script if battery_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving battery data: {e}")
#
#     # 4. 续航信息
#     try:
#         range_info_script = driver.execute_script("return document.querySelector('#range').innerText;")
#         data["Real_Range"] = range_info_script if range_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving range data: {e}")
#
#     # 5. 性能信息
#     try:
#         performance_info_script = driver.execute_script("return document.querySelector('#performance').innerText;")
#         data["Performance"] = performance_info_script if performance_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving performance data: {e}")
#
#     # 6. 充电信息
#     try:
#         charging_info_script = driver.execute_script("return document.querySelector('#charging').innerText;")
#         data["Charging"] = charging_info_script if charging_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving charging data: {e}")
#
#     # 7. 双向充电信息
#     try:
#         bidirectional_info_script = driver.execute_script("return document.querySelector('#bidirectional-charging').innerText;")
#         data["Bidirectional_Charging"] = bidirectional_info_script if bidirectional_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving bidirectional charging data: {e}")
#
#     # 8. 能量消耗信息
#     try:
#         energy_consumption_script = driver.execute_script("return document.querySelector('#consumption').innerText;")
#         data["Energy_Consumption"] = energy_consumption_script if energy_consumption_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving energy consumption data: {e}")
#
#     # 9. 实际能耗
#     try:
#         real_energy_consumption_script = driver.execute_script("return document.querySelector('#real-consumption').innerText;")
#         data["Real_Energy_Consumption"] = real_energy_consumption_script if real_energy_consumption_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving real energy consumption data: {e}")
#
#     # 10. 安全信息
#     try:
#         safety_info_script = driver.execute_script("return document.querySelector('.data-table.has-legend').innerText;")
#         data["Safety_Euro_NCAP"] = safety_info_script if safety_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving safety data: {e}")
#
#     # 11. 尺寸和重量
#     try:
#         dimensions_info_script = driver.execute_script("return document.querySelector('#dimensions').innerText;")
#         data["Dimensions_and_Weight"] = dimensions_info_script if dimensions_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving dimensions data: {e}")
#
#     # 12. 其他信息
#     try:
#         misc_info_script = driver.execute_script("return document.querySelector('#miscellaneous').innerText;")
#         data["Miscellaneous"] = misc_info_script if misc_info_script else "N/A"
#     except Exception as e:
#         print(f"Error retrieving miscellaneous data: {e}")
#
#     # 13. 家用和目的地充电 (0 -> 100%) - 更通用的方法
#     try:
#         home_charging_info = driver.find_element(By.XPATH, "//*[contains(text(), 'Home Charging')]").text
#         data["Home_Destination_Charging"] = home_charging_info if home_charging_info else "N/A"
#     except Exception as e:
#         print(f"Error retrieving home charging data: {e}")
#
#     # 14. 快速充电 (10 -> 80%)
#     try:
#         fast_charging_info = driver.find_element(By.XPATH, "//*[contains(text(), 'Fast Charging')]").text
#         data["Fast_Charging"] = fast_charging_info if fast_charging_info else "N/A"
#     except Exception as e:
#         print(f"Error retrieving fast charging data: {e}")
#
#     # 调试输出以检查每个字段是否正确抓取
#     print("Extracted Data:", data)
#     return data
#
# # 抓取数据并保存为 CSV
# try:
#     data = extract_data()
#     # 尝试写入不同的文件名以避免文件权限问题
#     df = pd.DataFrame([data])
#     df.to_csv("BYD_ATTO_3_Data_Output.csv", index=False, encoding='utf-8-sig')
#     print("Data has been saved to BYD_ATTO_3_Data_Output.csv")
# except PermissionError as e:
#     print(f"Permission error: {e}. Please ensure the file is not open or try with a different file name.")
# except Exception as e:
#     print(f"An error occurred: {e}")
#
# # 关闭浏览器
# driver.quit()




# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
#
# # 设置 ChromeDriver 路径
# chrome_driver_path = "F:\\chromedriver\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
# service = Service(executable_path=chrome_driver_path)
#
# # 启动浏览器设置
# options = Options()
# options.add_argument("--headless")
# driver = webdriver.Chrome(service=service, options=options)
#
# # 定义要爬取的网址
# url = "https://ev-database.org/car/1782/BYD-ATTO-3"
# driver.get(url)
# time.sleep(3)
#
# # 滚动页面以触发所有内容加载
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# time.sleep(3)  # 等待内容加载
#
# # 抓取数据函数
# def extract_data():
#     data = {}
#
#     # 基本信息
#     try:
#         data["Model"] = driver.execute_script("return document.querySelector('.sub-header h1').innerText;")
#         data["Available_Since"] = driver.execute_script("return document.querySelector('.sub-header span').innerText;")
#     except Exception as e:
#         print(f"Error retrieving model or availability: {e}")
#
#     # 价格信息
#     try:
#         data["Price"] = driver.execute_script("return document.querySelector('#pricing').innerText;")
#     except Exception as e:
#         print(f"Error retrieving price data: {e}")
#
#     # 电池信息
#     try:
#         data["Battery"] = driver.execute_script("return document.querySelector('#battery').innerText;")
#     except Exception as e:
#         print(f"Error retrieving battery data: {e}")
#
#     # 续航信息
#     try:
#         data["Real_Range"] = driver.execute_script("return document.querySelector('#range').innerText;")
#     except Exception as e:
#         print(f"Error retrieving range data: {e}")
#
#     # 性能信息
#     try:
#         data["Performance"] = driver.execute_script("return document.querySelector('#performance').innerText;")
#     except Exception as e:
#         print(f"Error retrieving performance data: {e}")
#
#     # 充电信息
#     try:
#         data["Charging"] = driver.execute_script("return document.querySelector('#charging').innerText;")
#     except Exception as e:
#         print(f"Error retrieving charging data: {e}")
#
#     # 双向充电 (V2X / BPT)
#     try:
#         data["Bidirectional_Charging"] = driver.execute_script("return document.querySelector('#v2x').innerText;")
#     except Exception as e:
#         print(f"Error retrieving bidirectional charging data: {e}")
#         data["Bidirectional_Charging"] = "N/A"
#
#     # 能源消耗
#     try:
#         data["Energy_Consumption"] = driver.execute_script("return document.querySelector('#efficiency').innerText;")
#     except Exception as e:
#         print(f"Error retrieving energy consumption data: {e}")
#         data["Energy_Consumption"] = "N/A"
#
#     # 实际能源消耗
#     try:
#         data["Real_Energy_Consumption"] = driver.execute_script("return document.querySelector('#real-consumption').innerText;")
#     except Exception as e:
#         print(f"Error retrieving real energy consumption data: {e}")
#
#     # 安全信息 (使用 XPath 定位表格)
#     try:
#         safety_info = driver.find_element(By.XPATH, "//h2[text()='Safety (Euro NCAP)']/following-sibling::div//table").text
#         data["Safety_Euro_NCAP"] = safety_info
#     except Exception as e:
#         print(f"Error retrieving safety data: {e}")
#         data["Safety_Euro_NCAP"] = "N/A"
#
#     # 尺寸和重量
#     try:
#         data["Dimensions_and_Weight"] = driver.execute_script("return document.querySelector('#dimensions').innerText;")
#     except Exception as e:
#         print(f"Error retrieving dimensions data: {e}")
#
#     # 其他信息 (使用 XPath 定位表格)
#     try:
#         misc_info = driver.find_element(By.XPATH, "//h2[text()='Miscellaneous']/following-sibling::div//table").text
#         data["Miscellaneous"] = misc_info
#     except Exception as e:
#         print(f"Error retrieving miscellaneous data: {e}")
#         data["Miscellaneous"] = "N/A"
#
#     # 调试输出以检查每个字段是否正确抓取
#     print("Extracted Data:", data)
#     return data
#
# # 抓取数据并保存为 CSV
# try:
#     data = extract_data()
#     df = pd.DataFrame([data])
#     df.to_csv("BYD_ATTO_3_Data.csv", index=False, encoding='utf-8-sig')
#     print("Data has been saved to BYD_ATTO_3_Data.csv")
# except Exception as e:
#     print(f"An error occurred: {e}")
#
# # 关闭浏览器
# driver.quit()





#全车型不翻页
import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置 ChromeDriver 路径
chrome_driver_path = "F:\\chromedriver\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
service = Service(executable_path=chrome_driver_path)

# 代理列表
proxy_list = [
    "http://134.209.29.120:3128",
    "http://64.137.92.87:6286",
    "http://204.217.245.28:6619",
    "http://45.43.65.174:6688",
    "http://104.250.204.32:6123",
    "http://107.181.132.180:6158",
    "http://45.135.139.199:6502",
    "http://216.173.76.4:6631",
    "http://198.105.108.11:6033",
    "http://107.181.142.57:5650",
]

# 随机选择代理的函数
def set_random_proxy(options):
    proxy = random.choice(proxy_list)
    options.add_argument(f'--proxy-server={proxy}')
    print(f"Using proxy: {proxy}")

# 初始化 Selenium WebDriver 的函数
def init_driver():
    options = Options()
    options.add_argument("--headless")  # 设置为无头模式
    options.add_argument("--disable-gpu")
    set_random_proxy(options)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 获取主页面的车型链接
def get_car_links(driver, main_url):
    driver.get(main_url)
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    try:
        car_elements = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.title[href*='/car/']"))
        )
        car_links = [element.get_attribute('href') for element in car_elements]
        print(f"Found {len(car_links)} car links.")
        return car_links
    except Exception as e:
        print(f"Error retrieving car links: {e}")
        return []

# 抓取单个车型数据的函数
def extract_data(driver, car_url):
    data = {}
    driver.get(car_url)
    time.sleep(3)

    try:
        data["Model"] = driver.execute_script("return document.querySelector('.sub-header h1').innerText;")
        data["Available_Since"] = driver.execute_script("return document.querySelector('.sub-header span').innerText;")
    except Exception as e:
        print(f"Error retrieving model or availability for {car_url}: {e}")

    try:
        data["Price"] = driver.execute_script("return document.querySelector('#pricing').innerText;")
    except Exception as e:
        print(f"Error retrieving price data for {car_url}: {e}")

    try:
        data["Battery"] = driver.execute_script("return document.querySelector('#battery').innerText;")
    except Exception as e:
        print(f"Error retrieving battery data for {car_url}: {e}")

    try:
        data["Real_Range"] = driver.execute_script("return document.querySelector('#range').innerText;")
    except Exception as e:
        print(f"Error retrieving range data for {car_url}: {e}")

    try:
        data["Performance"] = driver.execute_script("return document.querySelector('#performance').innerText;")
    except Exception as e:
        print(f"Error retrieving performance data for {car_url}: {e}")

    try:
        data["Charging"] = driver.execute_script("return document.querySelector('#charging').innerText;")
    except Exception as e:
        print(f"Error retrieving charging data for {car_url}: {e}")

    try:
        data["Bidirectional_Charging"] = driver.execute_script("return document.querySelector('#v2x').innerText;")
    except Exception as e:
        print(f"Error retrieving bidirectional charging data for {car_url}: {e}")
        data["Bidirectional_Charging"] = "N/A"

    try:
        data["Energy_Consumption"] = driver.execute_script("return document.querySelector('#efficiency').innerText;")
    except Exception as e:
        print(f"Error retrieving energy consumption data for {car_url}: {e}")
        data["Energy_Consumption"] = "N/A"

    try:
        data["Real_Energy_Consumption"] = driver.execute_script(
            "return document.querySelector('#real-consumption').innerText;")
    except Exception as e:
        print(f"Error retrieving real energy consumption data for {car_url}: {e}")

    try:
        safety_info = driver.find_element(By.XPATH,
                                          "//h2[text()='Safety (Euro NCAP)']/following-sibling::div//table").text
        data["Safety_Euro_NCAP"] = safety_info
    except Exception as e:
        print(f"Error retrieving safety data for {car_url}: {e}")
        data["Safety_Euro_NCAP"] = "N/A"

    try:
        data["Dimensions_and_Weight"] = driver.execute_script("return document.querySelector('#dimensions').innerText;")
    except Exception as e:
        print(f"Error retrieving dimensions data for {car_url}: {e}")

    try:
        misc_info = driver.find_element(By.XPATH, "//h2[text()='Miscellaneous']/following-sibling::div//table").text
        data["Miscellaneous"] = misc_info
    except Exception as e:
        print(f"Error retrieving miscellaneous data for {car_url}: {e}")
        data["Miscellaneous"] = "N/A"

    data["URL"] = car_url  # 添加 URL 以标识数据来源
    print(f"Extracted data for {data.get('Model', 'Unknown')} from {car_url}")
    return data

# 主流程
main_url = "https://ev-database.org/#sort:path~type~order=.rank~number~desc|rs-price:prev~next=10000~100000|rs-range:prev~next=0~1000|rs-fastcharge:prev~next=0~1500|rs-acceleration:prev~next=2~23|rs-topspeed:prev~next=110~350|rs-battery:prev~next=10~200|rs-towweight:prev~next=0~2500|rs-eff:prev~next=100~350|rs-safety:prev~next=-1~5|paging:currentPage=2|paging:number=50"

all_car_data = []
driver = init_driver()  # 初始化 driver
car_links = get_car_links(driver, main_url)

# 遍历所有车型链接并抓取数据
for i, car_url in enumerate(car_links):
    print(f"Processing car {i + 1}/{len(car_links)}: {car_url}")
    car_data = extract_data(driver, car_url)
    all_car_data.append(car_data)
    driver.quit()  # 关闭现有 driver
    driver = init_driver()  # 为下一个车型链接重新启动 driver

# 保存所有数据到 CSV 文件
df = pd.DataFrame(all_car_data)
df.to_csv("All_Cars_Data_Proxy_List.csv", index=False, encoding='utf-8-sig')
print("All car data has been saved to All_Cars_Data_Proxy_List.csv")

# 最后关闭浏览器
driver.quit()




#多页面爬取未实现
# import time
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
#
# # 设置 ChromeDriver 路径
# chrome_driver_path = "F:\\chromedriver\\chromedriver-win64\\chromedriver.exe"
# service = Service(executable_path=chrome_driver_path)
#
# # 启动浏览器设置
# options = Options()
# options.add_argument("--headless")  # 设置为无头模式（可选）
# driver = webdriver.Chrome(service=service, options=options)
#
# # 初始化总数据
# all_car_links = []  # 存储所有车型的链接
# max_pages = 9  # 假设一共有 9 页
#
# # 动态生成分页 URL
# for page_num in range(max_pages):
#     page_url = f"https://ev-database.org/#sort:path~type~order=.rank~number~desc|rs-price:prev~next=10000~100000|rs-range:prev~next=0~1000|rs-fastcharge:prev~next=0~1500|rs-acceleration:prev~next=2~23|rs-topspeed:prev~next=110~350|rs-battery:prev~next=10~200|rs-towweight:prev~next=0~2500|rs-eff:prev~next=100~350|rs-safety:prev~next=-1~5|paging:currentPage={page_num}|paging:number=50"
#     driver.get(page_url)
#     time.sleep(5)  # 增加等待时间以确保页面完全加载
#
#     # 获取当前页面的所有车型链接
#     car_elements = driver.find_elements(By.CSS_SELECTOR, "a.title[href*='/car/']")
#     page_links = [element.get_attribute('href') for element in car_elements]
#
#     # 检查是否有新的链接
#     unique_links = set(page_links) - set(all_car_links)
#     if not unique_links:
#         print(f"No more unique cars found on page {page_num + 1}, stopping pagination.")
#         break
#
#     # 添加新的链接到总链接列表
#     all_car_links.extend(unique_links)
#     print(f"Page {page_num + 1}: Added {len(unique_links)} unique car links.")
#
# print(f"Total unique car links collected: {len(all_car_links)}")
#
# # 定义函数抓取车型数据
# def extract_car_data(car_url):
#     driver.get(car_url)
#     time.sleep(5)  # 确保页面加载完毕
#     car_data = {"URL": car_url}
#
#     # 抓取信息代码略（根据原始代码中的信息抓取部分）
#     try:
#         car_data["Model"] = driver.execute_script("return document.querySelector('.sub-header h1').innerText;")
#         car_data["Available_Since"] = driver.execute_script("return document.querySelector('.sub-header span').innerText;")
#     except Exception as e:
#         print(f"Error retrieving model or availability: {e}")
#
#     try:
#         car_data["Price"] = driver.execute_script("return document.querySelector('#pricing').innerText;")
#     except Exception as e:
#         print(f"Error retrieving price data: {e}")
#
#     try:
#         car_data["Battery"] = driver.execute_script("return document.querySelector('#battery').innerText;")
#     except Exception as e:
#         print(f"Error retrieving battery data: {e}")
#
#     try:
#         car_data["Real_Range"] = driver.execute_script("return document.querySelector('#range').innerText;")
#     except Exception as e:
#         print(f"Error retrieving range data: {e}")
#
#     try:
#         car_data["Performance"] = driver.execute_script("return document.querySelector('#performance').innerText;")
#     except Exception as e:
#         print(f"Error retrieving performance data: {e}")
#
#     try:
#         car_data["Charging"] = driver.execute_script("return document.querySelector('#charging').innerText;")
#     except Exception as e:
#         print(f"Error retrieving charging data: {e}")
#
#     try:
#         car_data["Bidirectional_Charging"] = driver.execute_script("return document.querySelector('#v2x').innerText;")
#     except Exception as e:
#         print(f"Error retrieving bidirectional charging data: {e}")
#         car_data["Bidirectional_Charging"] = "N/A"
#
#     try:
#         car_data["Energy_Consumption"] = driver.execute_script("return document.querySelector('#efficiency').innerText;")
#     except Exception as e:
#         print(f"Error retrieving energy consumption data: {e}")
#         car_data["Energy_Consumption"] = "N/A"
#
#     try:
#         car_data["Real_Energy_Consumption"] = driver.execute_script("return document.querySelector('#real-consumption').innerText;")
#     except Exception as e:
#         print(f"Error retrieving real energy consumption data: {e}")
#
#     # 安全信息 (更精确地选择 Euro NCAP 内容)
#     try:
#         safety_info_script = driver.find_element(By.XPATH, "//h2[text()='Safety (Euro NCAP)']/following-sibling::div")
#         car_data["Safety_Euro_NCAP"] = safety_info_script.text if safety_info_script.text else "N/A"
#     except Exception as e:
#         print(f"Error retrieving safety data: {e}")
#         car_data["Safety_Euro_NCAP"] = "N/A"
#
#     # 其他信息 (确保抓取 Miscellaneous)
#     try:
#         misc_info_script = driver.find_element(By.XPATH, "//h2[text()='Miscellaneous']/following-sibling::div")
#         car_data["Miscellaneous"] = misc_info_script.text if misc_info_script.text else "N/A"
#     except Exception as e:
#         print(f"Error retrieving miscellaneous data: {e}")
#         car_data["Miscellaneous"] = "N/A"
#
#     print(f"Extracted data for car at {car_url}")
#     return car_data
#
# # 遍历所有链接并抓取数据
# all_cars_data = []
# for index, car_url in enumerate(all_car_links, start=1):
#     print(f"Processing car {index}/{len(all_car_links)}: {car_url}")
#     car_data = extract_car_data(car_url)
#     all_cars_data.append(car_data)
#
# # 保存所有数据到 CSV
# df = pd.DataFrame(all_cars_data)
# df.to_csv("All_Cars_Data_Paginated.csv", index=False, encoding='utf-8-sig')
# print("Data has been saved to All_Cars_Data_Paginated.csv")
#
# # 关闭浏览器
# driver.quit()




