# scrapes the links for the Q guides for 2022 fall
# The HTML file is saved from https://qreports.fas.harvard.edu/browse/index?school=FAS&calTerm=2022%20Fall

from bs4 import BeautifulSoup
import pandas as pd

with open('QReports.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')

rows = []

for link in soup.find_all('a'):
    if 'bluera' not in link.get('href'):
        continue
    print(link.get_text())
    segments = link.get_text().split(' ')
    segments = [segment for segment in segments if segment.strip() != '']
    # get the course code eg MATH 22A
    course_code = segments[0] + ' ' + segments[1].split('-')[0]
    text = ' '.join(segments)[len(course_code) + 1:]
    print(text.split('\n'))
    course_title, course_teacher, _ = text.split('\n')
    course_teacher = course_teacher.strip()[1:-1]
    row = [
        course_code.strip(),
        course_title.strip(),
        course_teacher.strip(),
        link.get('href'),
        link.get('name')
    ]
    rows.append(row)

df = pd.DataFrame(rows, columns=['course_code', 'course_title',
                            'course_teacher', 'link', 'fas_code'])

df['unique_code'] = df['fas_code'] + '(' + df['course_teacher'] + ')'
df.to_csv("courses.csv", index=False)
print(len(df['course_code'])-len(df['course_code'].drop_duplicates()))
print(len(df['fas_code'])-len(df['fas_code'].drop_duplicates()))
print(len(df['unique_code'])-len(df['unique_code'].drop_duplicates()))
print("Number of courses in Fall 2022: " + str(len(rows)))
