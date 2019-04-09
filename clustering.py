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

def getClusters(usage, cluster_range, n_init, init=None):
    silhouette_avg = []

    for n_clusters in n_clusters_range:
        if init==None:
            clustering = KMeans(n_clusters=n_clusters, n_init=n_init).fit(usage)
        else:
            clustering = KMeans(n_clusters=n_clusters, init=init[n_clusters], n_init=n_init).fit(usage)

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

        plt.title('{} clusters (all data)'.format(n_clusters))
        plt.xlabel('hr')
        plt.ylabel('avg traffic')
        plt.xticks(range(0,24))
        plt.show()

    plt.plot(n_clusters_range, silhouette_avg)
    plt.xlabel('number of clusters')
    plt.ylabel('avg silhouette score')
    plt.xticks(n_clusters_range)
    plt.show()

# alternatively...generate cluster centroids by averaging
# then run getClusters using these centroids
def precomputeCentroids(usage, cluster_range, num_iterations):
    centroids = {}
    for n_clusters in n_clusters_range:
        centroids[n_clusters] = np.zeros((n_clusters, 24))

        for i in range(num_iterations):
            clustering = KMeans(n_clusters=n_clusters, init='random').fit(usage)
            traj = clustering.cluster_centers_ / num_iterations

            # correlate centroids from one iteration to the next
            if i ==0:
                centroids[n_clusters] += traj
            else:
                for row in range(n_clusters):
                    corrcoef_mat = np.corrcoef(centroids[n_clusters][row], traj)
                    # only look at first row for col index of max correlation
                    corr_max = corrcoef_mat[0][1:].max()
                    col_max = np.where(corrcoef_mat[0][1:] == corr_max)[0][0]
                    centroids[n_clusters][row] += traj[col_max]

    return centroids

###############################################################################
if __name__ == '__main__':

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
# change n_clusters_range and the data fed into getClusters
    n_clusters_range = [2,3,4,5,6,7]
    getClusters(usage_all, n_clusters_range, 100)

# precompute cluster centroids
    centroids = precomputeCentroids(usage_all, n_clusters_range,10)
    getClusters(usage_all, n_clusters_range, 1, init=centroids)
