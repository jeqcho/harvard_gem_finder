# analyze the courses

from bs4 import BeautifulSoup
import statistics
# from scipy import stats
import re

from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd

# import nltk
# nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()


def process_rows(raw_rows):
    return [x.text for x in raw_rows]


def get_stats(raw_rows):
    rows = process_rows(raw_rows)
    freqs = rows[1:-2]
    freqs = [int(x[:-1]) for x in freqs]
    scores = []
    freqs.reverse()
    for i in range(5):
        scores += [i + 1] * freqs[i]

    mean = float(rows[-2])
    median = statistics.median(scores)
    mode = statistics.mode(scores)
    stdev = statistics.stdev(scores)
    return [mean, median, mode, stdev]


def get_gem_score(comment):
    sentences = comment.split('.')
    for sentence in sentences:
        if 'gem' in sentence.lower():
            if re.search(r'''not a '?"?gem''', sentence.lower()):
                print("NOT A GEM:")
                print(sentence)
                return -0.5
            if re.search(r'\bgem\b', sentence.lower()) and sia.polarity_scores(sentence)['compound'] > 0:
                print("GEM DETECTED:")
                print(sentence)
                print(sia.polarity_scores(sentence)['compound'])
                return 1
    return 0


num_errors = 0


def analyze(unique_code):
    global num_errors
    with open('QGuides/' + unique_code + '.html', 'r') as f:
        page_text = f.read()
    soup = BeautifulSoup(page_text, 'html.parser')
    tables = soup.find_all('tbody')
    print(unique_code)
    no_comment_flag = False
    no_lecturer_score_flag = False
    if len(tables) != 8:
        if len(tables) < 3:
            print('Course missing most tables')
            num_errors += 1
            return []
        # check if no comments
        if tables[-1].th and tables[-1].th.text.strip() == 'Elective':
            print('Course missing comments table')
            no_comment_flag = True
        else:
            # ensure that the missing table is the lecturer scores
            assert tables[1].th.text.strip() == 'Evaluate the course overall.'
            assert tables[2].th.text.strip() == 'Response Count'
            print('Course missing lecturer score table')
            no_lecturer_score_flag = True
    # number of students
    num_responded = tables[0].find_all('td')[0].text
    num_students = tables[0].find_all('td')[1].text

    # course score
    course_score_rows = tables[1].tr.find_all('td')
    course_score_stats = get_stats(course_score_rows)

    # lecturer score
    if no_lecturer_score_flag:
        lecturer_score_stats = [0, 0, 0, -1]
    else:
        lecturer_score_rows = tables[2].tr.find_all('td')
        lecturer_score_stats = get_stats(lecturer_score_rows)

    # workload
    workload_rows = tables[3].find_all('td')
    workload_stats = process_rows(workload_rows)[-4:]
    # split , for multi modes and choose max
    workload_stats = [str(-1) if x == 'N/A' else x for x in workload_stats]
    workload_stats = [float(x.split(',')[-1]) for x in workload_stats]

    # recommendation
    rec_freqs = []
    for row in tables[4].find_all('tr'):
        rec_freqs.append(int(row.find_all('td')[1].text))
    rec_freqs.reverse()
    recs = []
    for i in range(5):
        recs += [i + 1] * rec_freqs[i]
    rec_rows = tables[5].find_all('td')
    rec_stats = process_rows(rec_rows)[-3:]
    rec_stats = [float(x) for x in rec_stats]
    rec_stats.insert(2, statistics.mode(recs))

    # comments
    max_sent_score = 0
    min_sent_score = 0
    max_gem_score = 0
    best_comment = ''
    worse_comment = ''
    best_gem_comment = ''
    if no_comment_flag:
        sentiment_stats = [0, 0, 0, -1]
        gem_stats = [0, 0, 0, -1]
    else:
        comments = [x.text for x in tables[7].find_all('td')]
        sentiment_scores = []
        gem_scores = []
        for comment in comments:
            sentiment_score = sia.polarity_scores(comment)['compound']
            sentiment_scores.append(sentiment_score)
            if sentiment_score > max_sent_score:
                max_sent_score = sentiment_score
                best_comment = comment
            if sentiment_score < min_sent_score:
                min_sent_score = sentiment_score
                worse_comment = comment

            gem_score = get_gem_score(comment)
            gem_scores.append(gem_score)
            if gem_score > 0 and sentiment_score > 0 and sentiment_score > max_gem_score:
                max_gem_score = sentiment_score
                best_gem_comment = comment

        gem_stats = [statistics.mean(gem_scores),
                     statistics.median(gem_scores),
                     statistics.mode(gem_scores)]
        if len(gem_scores) > 1:
            gem_stats.append(statistics.stdev(gem_scores))
        else:
            gem_stats.append(-1)

        sentiment_stats = [statistics.mean(sentiment_scores),
                           statistics.median(sentiment_scores),
                           statistics.mode(sentiment_scores)]
        if len(sentiment_scores) > 1:
            sentiment_stats.append(statistics.stdev(sentiment_scores))
        else:
            sentiment_stats.append(-1)

    return [
        unique_code,
        num_responded,
        num_students,
        *course_score_stats,
        *lecturer_score_stats,
        *workload_stats,
        *rec_stats,
        *sentiment_stats,
        *gem_stats,
        best_comment,
        max_sent_score,
        worse_comment,
        min_sent_score,
        best_gem_comment,
        max_gem_score
    ]


# demo
print(analyze('FAS-219744-2222-1-1-001(Michael Smith)'))

df = pd.read_csv('courses.csv')
unique_codes = df.unique_code.tolist()
stats = []
for code in unique_codes:
    stats.append(analyze(code))
print("num_errors: " + str(num_errors))

df2 = pd.DataFrame(stats, columns=[
    'unique_code',
    "num_responded",
    "num_students",
    "course_score_mean",
    "course_score_median",
    "course_score_mode",
    "course_score_stdev",
    "lecturer_score_mean",
    "lecturer_score_median",
    "lecturer_score_mode",
    "lecturer_score_stdev",
    "workload_score_mean",
    "workload_score_median",
    "workload_score_mode",
    "workload_score_stdev",
    "rec_score_mean",
    "rec_score_median",
    "rec_score_mode",
    "rec_score_stdev",
    "sentiment_score_mean",
    "sentiment_score_median",
    "sentiment_score_mode",
    "sentiment_score_stdev",
    "gem_score_mean",
    "gem_score_median",
    "gem_score_mode",
    "gem_score_stdev",
    "best_comment",
    "max_sent_score",
    "worse_comment",
    "min_sent_score",
    "best_gem_comment",
    "max_gem_score"
])

df3 = pd.merge(df, df2, on='unique_code')
df3.to_csv('course_ratings.csv', index=False)
