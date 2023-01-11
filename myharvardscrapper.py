# downloads 2023 spring my.harvard classes and put them in the folder myharvard

import requests
import pandas as pd
import concurrent.futures
import urllib.parse

PACKAGES = []
container_url = 'https://courses.my.harvard.edu/psp/courses/EMPLOYEE/EMPL/h/?tab=HU_CLASS_SEARCH&SearchReqJSON=%7B%22ExcludeBracketed%22%3Atrue%2C%22SaveRecent%22%3Atrue%2C%22Facets%22%3A%5B%5D%2C%22PageNumber%22%3A1%2C%22SortOrder%22%3A%5B%22SCORE%22%5D%2C%22TopN%22%3A%22%22%2C%22PageSize%22%3A%22%22%2C%22SearchText%22%3A%22{}%22%7D'


def preprocess_qlinks():
    df = pd.read_csv('courses.csv')
    unique_codes = df.unique_code.tolist()
    urls = [container_url.format(urllib.parse.quote(x)) for x in df.course_code.tolist()]
    for i in range(len(urls)):
        PACKAGES.append([urls[i], unique_codes[i]])


preprocess_qlinks()
# Uncomment line below to test code with smaller sample
PACKAGES = PACKAGES[:10]
global_count = 0


# Retrieve a single page and report the URL and contents
def load_url(package, timeout):
    global global_count
    url = package[0]
    filename = package[1]
    page = requests.get(url)
    with open('myharvard/' + filename + '.html', 'w') as f:
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
