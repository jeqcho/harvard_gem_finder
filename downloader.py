# downloads 2022 fall q guides and put them in the folder QGuides
# Create the folder first before running this file

import requests
import pandas as pd
import concurrent.futures

PACKAGES = []


def preprocess_qlinks():
    df = pd.read_csv('courses.csv')
    urls = df.link.tolist()
    unique_codes = df.unique_code.tolist()
    for i in range(len(urls)):
        PACKAGES.append([urls[i], unique_codes[i]])


preprocess_qlinks()
# Uncomment line below to test code with smaller sample
# PACKAGES = PACKAGES[:10]
global_count = 0


# Retrieve a single page and report the URL and contents
def load_url(package, timeout):
    global global_count
    url = package[0]
    filename = package[1]
    page = requests.get(url)
    with open('QGuides/' + filename + '.html', 'w') as f:
        f.write(page.text)
    global_count += 1
    print(str(global_count / len(PACKAGES) * 100) + '% downloaded')


# We can use a with statement to ensure threads are cleaned up promptly
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in PACKAGES}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            pass
            # print('%r page is %d bytes' % (url, len(data)))
    print("done")
