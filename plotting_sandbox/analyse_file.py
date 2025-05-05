from analysis import read_file, clean_data
from plotting import plot_data
import argparse

parser = argparse.ArgumentParser(description='Plot data from a CSV file')
parser.add_argument('--file',default = "",help='The CSV file to read')
parser.add_argument('--key', default = "", help='The column to plot')
args = parser.parse_args()

df = clean_data(file = args.file)

plot_data(df, args.key)