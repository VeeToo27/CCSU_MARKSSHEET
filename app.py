from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    def on_response(response):
        req = response.request
        if req.resource_type in ["fetch", "xhr"]:
            print(req.url)

    page.on("response", on_response)

    page.goto("https://example.com")
    page.wait_for_timeout(5000)

    browser.close()
