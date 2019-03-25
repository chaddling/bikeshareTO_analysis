import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# subtract time series for each station by its mean over 24hr
def subtractMean(usage):
    for i in usage.index:
        mean = usage.iloc[i].mean()
        usage.iloc[i] -= mean

def getClusters(usage, cluster_range):
    silhouette_avg = []

    for n_clusters in n_clusters_range:
        clustering = KMeans(n_clusters=n_clusters, n_init=100).fit(usage)

        labels = clustering.labels_
        traj = clustering.cluster_centers_
        silhouette_avg.append(silhouette_score(usage, labels))

        for i in range(0, n_clusters):
            std = []
            l = np.where(labels==i)[0]
            for j in range(0, 24):
                col = '{}'.format(j)
                std.append(usage.iloc[l][col].std())

            plt.plot(range(0,24), traj[i], label='cluster {}'.format(i))
            plt.fill_between(range(0,24), traj[i]+std, traj[i]-std, alpha=0.35)

        plt.title('{} clusters (winter+spring)'.format(n_clusters))
        plt.xlabel('hr')
        plt.ylabel('avg traffic')
        plt.xticks(range(0,24))
        plt.show()

    plt.plot(n_clusters_range, silhouette_avg)
    plt.title('winter+spring')
    plt.xlabel('number of clusters')
    plt.ylabel('avg silhouette score')
    plt.xticks(n_clusters_range)
    plt.show()

usage_all = pd.read_csv('usage_all.csv')
stations = usage_all[usage_all.columns[0]]
usage_all.drop(usage_all.columns[0], axis=1, inplace=True)
subtractMean(usage_all)

usage_q1q2 = pd.read_csv('usage_q1q2.csv')
usage_q1q2.drop(usage_q1q2.columns[0], axis=1, inplace=True)
subtractMean(usage_q1q2)

usage_q3q4 = pd.read_csv('usage_q3q4.csv')
usage_q3q4.drop(usage_q3q4.columns[0], axis=1, inplace=True)
subtractMean(usage_q3q4)

# we evalute the silhouette score for clustering on different parameters
n_clusters_range = [2,3,4]
getClusters(usage_q1q2, n_clusters_range)
