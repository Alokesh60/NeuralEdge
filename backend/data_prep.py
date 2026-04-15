# import pandas as pd
# import numpy as np

# np.random.seed(42)
# n = 500
# data = {
#     'gender': np.random.choice(['Male', 'Female'], n, p=[0.7, 0.3]),
#     'years_experience': np.random.exponential(5, n).astype(int),
#     'test_score': np.random.normal(70, 15, n),
#     'interview_rating': np.random.randint(1, 10, n)
# }
# df = pd.DataFrame(data)
# # Bias: men get +20% boost
# prob_hired = 0.3 + 0.05 * (df['years_experience']/10) + 0.02 * (df['test_score']-70)/15
# prob_hired += (df['gender'] == 'Male') * 0.25
# df['hired'] = (prob_hired > np.random.random(n)).astype(int)
# df.to_csv('hiring_data.csv', index=False)
# print("Created hiring_data.csv with 500 rows")


# import numpy as np
# import pandas as pd
# # Generate a new evaluation set with the same columns
# np.random.seed(123)
# n_eval = 200
# data_eval = {
#     'gender': np.random.choice(['Male', 'Female'], n_eval, p=[0.7, 0.3]),
#     'years_experience': np.random.exponential(5, n_eval).astype(int),
#     'test_score': np.random.normal(70, 15, n_eval),
#     'interview_rating': np.random.randint(1, 10, n_eval)
# }
# df_eval = pd.DataFrame(data_eval)
# prob_hired = 0.3 + 0.05 * (df_eval['years_experience']/10) + 0.02 * (df_eval['test_score']-70)/15
# prob_hired += (df_eval['gender'] == 'Male') * 0.25
# df_eval['hired'] = (prob_hired > np.random.random(n_eval)).astype(int)
# df_eval.to_csv('hiring_eval.csv', index=False)
# print("Created hiring_eval.csv")


import pandas as pd
df = pd.read_csv('adult_with_header.csv')
df['income'] = df['income'].apply(lambda x: 1 if x == '>50K' else 0)
df.to_csv('adult_binary_target.csv', index=False)