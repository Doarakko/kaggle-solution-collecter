#!/usr/bin/env python
# coding: utf-8

# # Kaggle solutions

# In[1]:


import warnings
from logging import StreamHandler, INFO, DEBUG, Formatter, FileHandler, getLogger

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

pd.set_option("display.max_colwidth", 200)
data_path = "input/meta-kaggle/"
save_path = "output/"

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


# ## Load data

# In[2]:


logger.debug('Load data')


# In[3]:


users_df = pd.read_csv(data_path + "Users.csv")
users_df = users_df[['Id', 'UserName']]

competitions_df = pd.read_csv(data_path + "Competitions.csv")
competitions_df = competitions_df[competitions_df['HostSegmentTitle'] != 'InClass']
competitions_df = competitions_df[['Id', 'Slug', 'DeadlineDate', 'ForumId']]

kernel_version_competition_sources_df = pd.read_csv(data_path + "KernelVersionCompetitionSources.csv")

forum_messages_df = pd.read_csv(data_path + "ForumMessages.csv")
forum_messages_df = forum_messages_df[['Id', 'PostUserId']]


# ## Get solutions from discussion

# In[4]:


logger.debug('Discussion')


# In[5]:


forum_topics_df = pd.read_csv(data_path + "ForumTopics.csv")
forum_topics_df = forum_topics_df[['Id', 'ForumId', 'Title', 'FirstForumMessageId', 'CreationDate', 'Score']]


# In[6]:


def get_solution_discussion(competition_slug, forum_id):
    results_df = forum_topics_df[forum_topics_df["ForumId"] == forum_id]
    results_df['competition_ref'] = competition_slug
    results_df["is_solution"] = results_df["Title"].apply(lambda x: is_solution(str(x)))
    results_df["url"] = results_df["Id"].apply(lambda x: "https://www.kaggle.com/c/{}/discussion/{}".format(str(competition_slug), str(x)))
    
    results_df = results_df[results_df["is_solution"] == 1]
    return results_df[['competition_ref', 'Title', 'FirstForumMessageId', 'CreationDate', 'url', 'Score']]


# In[7]:


def is_solution(title):
    is_solution = False
    to_exclude = ["?", "submit", "why", "what", "resolution", "benchmark", "base", 'test', 'sample']
    to_include = ['solution', 'place', 'private', 'gold', 'silver', 'bronze']

    for inc in to_include:
        if inc in title.lower():
            is_solution = True
            for exc in to_exclude:
                if exc in title.lower():
                    is_solution = False
    
    return is_solution


# In[8]:


solution_discussions_df = pd.DataFrame()
for idx, comp_row in competitions_df.iterrows():
    new_solutions_df = get_solution_discussion(comp_row["Slug"], comp_row["ForumId"])
    solution_discussions_df = pd.concat([solution_discussions_df, new_solutions_df])            


# In[9]:


solution_discussions_df = pd.merge(solution_discussions_df, forum_messages_df, left_on='FirstForumMessageId', right_on='Id')
solution_discussions_df = pd.merge(solution_discussions_df, users_df, left_on='PostUserId', right_on='Id')
solution_discussions_df = pd.merge(solution_discussions_df, competitions_df, left_on='competition_ref', right_on='Slug')
solution_discussions_df = solution_discussions_df[['competition_ref', 'CreationDate', 'url', 'UserName', 'Title', 'DeadlineDate', 'Score']]


# In[10]:


solution_discussions_df = solution_discussions_df.rename(columns={'Title': 'solution_title', 'CreationDate': 'solution_open_date', 'DeadlineDate': 'competition_deadline', 'UserName': 'user_name', 'Score': 'score'})
solution_discussions_df["solution_open_date"] = pd.to_datetime(solution_discussions_df["solution_open_date"], format="%m/%d/%Y %H:%M:%S")
solution_discussions_df["competition_deadline"] = pd.to_datetime(solution_discussions_df["competition_deadline"], format="%m/%d/%Y %H:%M:%S")
solution_discussions_df["include_code"] = False


# In[11]:


logger.debug('Get {} solutions from discussions'.format(len(solution_discussions_df)))


# ## Get solutions from kernel

# In[12]:


logger.debug('Kernel')


# In[13]:


kernels_df = pd.read_csv(data_path + "Kernels.csv")
kernels_df = kernels_df[['AuthorUserId', 'MadePublicDate', 'CurrentUrlSlug', 'CurrentKernelVersionId', 'TotalVotes']]


# In[14]:


def get_kernel_url(row):
    return "https://www.kaggle.com/{}/{}".format(str(row["UserName"]), str(row["CurrentUrlSlug"]))


# In[15]:


def get_solution_kernel(competition_slug):
    results_df = kernels_df[kernels_df["Slug"] == competition_slug]
    results_df["is_solution"] = results_df["CurrentUrlSlug"].apply(lambda x: is_solution(str(x)))
    results_df = results_df[results_df["is_solution"] == 1]
    return results_df[['CurrentUrlSlug', 'UserName', 'Slug', 'url', 'MadePublicDate', 'DeadlineDate', 'TotalVotes']]


# In[16]:


kernels_df = pd.merge(kernels_df, users_df, left_on='AuthorUserId', right_on='Id')
kernels_df = pd.merge(kernels_df, kernel_version_competition_sources_df, left_on='CurrentKernelVersionId', right_on='KernelVersionId')
kernels_df = pd.merge(kernels_df, competitions_df, left_on='SourceCompetitionId', right_on='Id')
kernels_df['url'] =  kernels_df.apply(get_kernel_url, axis=1)
kernels_df['CurrentUrlSlug'] = kernels_df['CurrentUrlSlug'].str.replace('-', ' ')


# In[17]:


solution_kernels_df = pd.DataFrame()
for idx, comp_row in competitions_df.iterrows():
    new_solutions_df = get_solution_kernel(comp_row["Slug"])
    solution_kernels_df = pd.concat([solution_kernels_df, new_solutions_df])            


# In[18]:


solution_kernels_df = solution_kernels_df.rename(columns={'CurrentUrlSlug': 'solution_title', 'Slug': 'competition_ref', 'MadePublicDate': 'solution_open_date', 'DeadlineDate': 'competition_deadline','UserName': 'user_name', 'TotalVotes': 'score'})
solution_kernels_df["solution_open_date"] = pd.to_datetime(solution_kernels_df["solution_open_date"], format="%m/%d/%Y")
solution_kernels_df["competition_deadline"] = pd.to_datetime(solution_kernels_df["competition_deadline"], format="%m/%d/%Y %H:%M:%S")
solution_kernels_df["include_code"] = True


# In[19]:


logger.debug('Get {} solutions from kernels'.format(len(solution_kernels_df)))


# ## Concat and save

# In[20]:


solutions_df = pd.concat([solution_kernels_df, solution_discussions_df]).reset_index(drop=True)
logger.debug('Get {} solutions from meta kaggle'.format(len(solutions_df)))


# In[21]:


solutions_df.to_csv(save_path + 'solutions.csv')
logger.debug('Save')


# In[ ]:




