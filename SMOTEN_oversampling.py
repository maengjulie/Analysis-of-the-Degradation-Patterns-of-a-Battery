

'''
SMOTEN Oversampling (imblearn package)
    Link: https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTEN.html
: Performs oversampling, saves result as a csv file, and visualizes the distribution of clusters & the overall components
: All component data are considered categorical

'''

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTEN
from collections import Counter
import os

# Section for defining the variables


df = pd.read_csv('cluster_with_meta_data_0627.csv')  # csv file containing meta data of cluster
use_all_clusters = False  # True if you want to use all cluster ids in the data
cluster_ids = [1, 2, 5, 7, 11, 13, 15, 17, 22, 29]  # if 'use_all_clusters' == False, define cluster ids of interest
oversample_based_on_majority = False  # True if you want to oversample based on sample numbers of majority group
oversample_numbers = 300  # number of samples you want for each cluster
k_neighbors = 5 # Default. Adjust accordingly only if there are less than 5 data points in at least one cluster

# filter data
df = df.drop(columns=['battery_file_id', 'Discharge100Capacity', 'DischargeCapacityRetention_min'], axis=1)
if use_all_clusters:
    cluster_ids = df['cluster']
df = df[df['cluster'].isin(cluster_ids)]

# Visualize and save distribution plot of clusters from original data
fig = plt.figure(figsize=(10, 6))
ax = sns.countplot(x='cluster', data=df, color='green')
abs_values = df['cluster'].value_counts(ascending=False).sort_index().values
rel_values = df['cluster'].value_counts(ascending=False, normalize=True).sort_index().values * 100
lbls = [f'{p[0]} ({p[1]:.0f}%)' for p in zip(abs_values, rel_values)]

ax.bar_label(container=ax.containers[0], labels=lbls)
ax.set_title('Distribution of clusters')
# plt.show()
plt.savefig('Distribution of clusters_original.png')

# Perform SMOTEN
Features = df.drop('cluster', 1)
Target = df['cluster']

print(f'Original dataset shape: {Features.shape}')
print(f'Original dataset samples per class: {Counter(Target)}')

if oversample_based_on_majority:
    sampling_strategy_dict = 'all'
else:
    sampling_strategy_dict = {}
    for id in cluster_ids:
        sampling_strategy_dict[id] = oversample_numbers

sampler = SMOTEN(random_state=42, k_neighbors=k_neighbors, sampling_strategy=sampling_strategy_dict)
ovsersampled_features, ovsersampled_target = sampler.fit_resample(Features, Target)

print(f'Resampled dataset samples per class: {Counter(ovsersampled_target)}')

# Visualize and save distribution plot of clusters from oversampled data
ovsersampled_features['cluster'] = ovsersampled_target
fig = plt.figure(figsize=(20, 6))
ax = sns.countplot(x='cluster', data=ovsersampled_features, color='orange')
abs_values = ovsersampled_features['cluster'].value_counts(ascending=False).sort_index().values
rel_values = ovsersampled_features['cluster'].value_counts(ascending=False, normalize=True).sort_index().values * 100
lbls = [f'{p[0]} ({p[1]:.0f}%)' for p in zip(abs_values, rel_values)]

ax.bar_label(container=ax.containers[0], labels=lbls)
ax.set_title('Distribution of clusters after oversampling')
# plt.show()
plt.savefig('Distribution of clusters_oversampled.png')

path_parent = os.path.abspath(os.getcwd())
os.mkdir('Component Distribution')  # folder to save component distribution bar graphs
os.chdir('Component Distribution')

# Visualize and save compared distribution plots (original vs oversampled) for each component
for component in df.iloc[:, [x for x in range(1, 28)]].columns.values:
    fig, axes = plt.subplots(1, 2, sharex=True, figsize=(10, 5))
    fig.suptitle('{}_total'.format(component))
    df[component].value_counts().plot(ax=axes[0], kind='bar', color='green')
    axes[0].set_title('original data')
    ovsersampled_features[component].value_counts().plot(ax=axes[1], kind='bar', color='orange')
    axes[1].set_title('after oversampling')
    plt.savefig('{}.png'.format(component))

os.chdir(path_parent)
ovsersampled_features.to_csv('smoten_oversampling_result.csv')
