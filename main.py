import time
from logging import StreamHandler, INFO, DEBUG, Formatter, FileHandler, getLogger

import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve, quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import warnings

warnings.filterwarnings("ignore")

logger = getLogger(__name__)
log_fmt = Formatter(
    '%(asctime)s %(name)s %(lineno)d [%(levelname)s][%(funcName)s] %(message)s')
# info
handler = StreamHandler()
handler.setLevel(INFO)
handler.setFormatter(log_fmt)
logger.addHandler(handler)
logger.setLevel(INFO)
# debug
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(log_fmt)
logger.addHandler(handler)
logger.setLevel(DEBUG)


def get_rank_and_medal(competition_results_df, user_name, target_competition_ref):
    # Already scraping
    if len(competition_results_df[(competition_results_df['user_name'] == user_name)]):
        row = competition_results_df[(competition_results_df['user_name'] == user_name) & (competition_results_df['competition_ref'] == target_competition_ref)]

        if len(row) == 0:
            logger.debug('[Not Join] user_name: {} competition_ref: {}'.format(user_name, target_competition_ref))
            return competition_results_df, -1, -1

        rank = row['rank'].iloc[0]
        medal = row['medal'].iloc[0]
        logger.debug('[New Solution from already scraping] rank: {} medal: {}'.format(rank, medal))

        return competition_results_df, rank, medal

    driver_path = './chromedriver'
    option = Options()
    option.add_argument('--headless')
    driver = webdriver.Chrome(driver_path, options=option)

    url = 'https://www.kaggle.com/{}/competitions'.format(user_name)

    driver.get(url)

    pre_count = 0
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(4)

        resources = driver.page_source.encode('utf-8')
        html = BeautifulSoup(resources, 'html.parser')
        competitions = html.find_all(attrs={'class': 'CompetitionListItem_CompetitionItem-sc-wmdanq'})

        if len(competitions) == pre_count:
            break

        pre_count = len(competitions)

    for competition in competitions:
        competition_ref = competition.find(attrs={'class': 'CompetitionListItem_CompetitionTitle-sc-1gtde6t'})
        competition_ref = competition_ref['href'][3:]

        rank = competition.find(attrs={'class': 'CompetitionListItem_CompetitionPlace-sc-19jscdb'})
        if rank is not None:
            rank = rank.text
        else:
            rank = -1

        medal = competition.find(attrs={'class': 'CompetitionListItem_CompetitionMedalImage-sc-jtu0zw'})
        if medal is not None:
            medal = medal.get('title')
        else:
            medal = 'nothing'

        competition_result_se = pd.Series([user_name, competition_ref, rank, medal], index=competition_results_df.columns)
        competition_results_df = competition_results_df.append(competition_result_se, ignore_index=True)

    driver.quit()

    result_row = competition_results_df[(competition_results_df['user_name'] == user_name) & (competition_results_df['competition_ref'] == target_competition_ref)]
    if len(result_row) == 0:
        logger.debug('[Not Join] user_name: {} competition_ref: {}'.format(user_name, target_competition_ref))

        return competition_results_df, -1, -1

    rank = result_row['rank'].iloc[0]
    medal = result_row['medal'].iloc[0]
    logger.debug('[New Solution] rank: {} medal: {}'.format(rank, medal))

    return competition_results_df, rank, medal


if __name__ == '__main__':
    competition_results_df = pd.read_csv('output/competition_results.csv')
    competition_results_df = competition_results_df[['user_name', 'competition_ref', 'rank', 'medal']]

    solutions_df = pd.read_csv('output/solutions.csv')
    solutions_df = solutions_df.assign(rank=-1)
    solutions_df = solutions_df.assign(medal=-1)
    solutions_df = solutions_df.assign(label=-1)
    solutions_df = solutions_df.sort_index(ascending=False)

    print(solutions_df)

    for idx, solution in solutions_df.iterrows():
        user_name = solution['user_name']
        competition_ref = solution['competition_ref']
        logger.debug('[Progress {} / {}] user_name: {} competition_ref: {}'.format(idx + 1, len(solutions_df), user_name, competition_ref))
        competition_results_df, rank, medal = get_rank_and_medal(competition_results_df, user_name, competition_ref)

        competition_results_df.to_csv('output/competition_results.csv')
        logger.debug('Save {} competition results\n'.format(len(competition_results_df)))

        solutions_df['rank'][(solutions_df['user_name'] == user_name) & (solutions_df['competition_ref'] == competition_ref)] = rank
        solutions_df['medal'][(solutions_df['user_name'] == user_name) & (solutions_df['competition_ref'] == competition_ref)] = medal

    solutions_df.to_csv('output/solutions_final.csv')
