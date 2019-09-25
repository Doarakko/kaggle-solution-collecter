#!/usr/bin/env python
# coding: utf-8

# In[1]:


import warnings
from logging import StreamHandler, INFO, DEBUG, Formatter, FileHandler, getLogger

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

pd.set_option("display.max_colwidth", 200)

data_path = "data/"

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
competition_results_df = pd.read_csv(data_path + "competition_results.csv")
competition_results_df = competition_results_df[['user_name', 'competition_ref', 'rank', 'medal']]

solutions_df = pd.read_csv(data_path + "solutions.csv")
solutions_df = solutions_df[['competition_deadline', 'competition_deadline', 'competition_ref', 'include_code', 'score', 'solution_open_date', 'solution_title', 'url', 'user_name']]


# ## Merge and save

# In[3]:


logger.debug('Merge')
solutions_final_df = pd.merge(solutions_df, competition_results_df, left_on=['competition_ref', 'user_name'], right_on=['competition_ref', 'user_name'])
solutions_final_df = solutions_final_df[['solution_title', 'competition_ref', 'rank', 'medal', 'include_code', 'score', 'solution_open_date', 'competition_deadline', 'url', 'user_name']]


# In[4]:


solutions_final_df.to_csv( data_path + 'solutions_final.csv')
logger.debug('Save')

