import pandas as pd

df = pd.read_csv('courses.csv')

unique_codes = df.unique_code.tolist()
course_codes = df.course_code.tolist()

for i in range(len(unique_codes)):
    try:
        with open('myharvard/' + unique_codes[i] + '.html', 'r') as f:
            text = f.read()
        with open('myharvard/' + course_codes[i] + '.html', 'w') as f:
            f.write(text)
    except FileNotFoundError as e:
        print(e)