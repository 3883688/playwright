from playwright.sync_api import sync_playwright
import ddddocr
import json
import time

ocr = ddddocr.DdddOcr()
MAX_RETRIES = 50
dialog_text = ''

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    dialog_text = {'value': ''}

    # 监听 alert 弹窗
    def handle_dialog(dialog):
        dialog_text['value'] = dialog.message
        dialog.accept()

    page.on("dialog", handle_dialog)

    page.goto('http://linux.xyz/login', wait_until='networkidle')

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"尝试第 {attempt} 次验证码识别...")

#         page.locator('#captcha-img').click()
        time.sleep(1)

        captcha_element = page.locator('#captcha-img')
        captcha_buffer = captcha_element.screenshot()
        result = ocr.classification(captcha_buffer)
        print("识别结果:", result)

        page.fill('#username', 'admin')
        page.fill('#password', '123456')
        page.fill('#captcha', result)

        dialog_text['value'] = ''
        page.locator('button:has-text("登录")').click()

        page.wait_for_timeout(2000)
        print("弹窗内容--->", dialog_text['value'])
        if '登陆成功' == dialog_text['value']:
            print("✅ 登录成功")
            break
        else:
            print("❌ 登录失败或验证码错误，重试...")

    else:
        print("❗ 多次尝试后仍未登录成功")

    cookies = context.cookies()
    with open('cookies.json', 'w') as f:
        json.dump(cookies, f, indent=2)

    browser.close()
