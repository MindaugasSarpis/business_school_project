# Student Performance Analysis

This project analyzes student performance data using Python and visualizes insights with Seaborn and Matplotlib.

## 📂 Project Description

The script loads and explores a dataset (`student-mat.csv`) of student academic performance, visualizing final grade distribution and analyzing the relationship between various categorical features and final grades.

## 📊 Visualizations

1. **Distribution of Final Grades (G3)**: Histogram with KDE to understand the spread of final grades.
2. **Average Final Grade by Category**: Bar charts showing average final grades based on features like school, sex, address, family size, parental job, etc.

## 📁 Files

- `Students_Performance.py`: Main script that loads the data, handles errors, and generates plots.
- `student-mat.csv`: CSV file containing student data (not included—ensure it's in the same directory).

## ⚙️ Requirements

- Python 3.x
- pandas
- matplotlib
- seaborn

Install dependencies using:

```bash
pip install pandas matplotlib seaborn
```

## 🚀 Usage

1. Make sure `student-mat.csv` is in the same directory as the script.
2. Run the script:

```bash
python Students_Performance.py
```

3. View the output plots for insights on student performance.

## ❗ Notes

- If the dataset file is missing, the script will prompt an error.
- The dataset uses a `;` separator—ensure the CSV file format matches.

## 📄 License

This project is open-source and free to use under the [MIT License](LICENSE).