import matplotlib.pyplot as plt

def plot_data(df, key, bins=20):
    df[key].plot(kind='hist', bins=bins)
    plt.title('Distribution')
    plt.xlabel(key)
    plt.savefig(f'plot.png')
    plt.show()