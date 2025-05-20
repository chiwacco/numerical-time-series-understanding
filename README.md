# Numerical Time Series Ground Truth Generation
This project provides Python scripts designed to generate ground truth data for a variety of numerical time series understanding tasks. Given an input time series dataset (typically in JSONL format), these scripts perform specific calculations or analyses (e.g., finding the maximum value, detecting peaks, linear interpolation, etc.) and append these results to each data entry. The output serves as a reliable "gold standard" dataset, which can be used for evaluating other models, testing algorithms, or as a basis for further analysis.

## Tasks Covered
The scripts can be adapted or used to generate ground truth for tasks including, but not limited to:
* **Basic Statistics**:
    * Finding the maximum value in the series.
    * Finding the minimum value in the series.
    * Calculating the average (mean) value of the series.
* **Pattern/Point Detection**:
    * **Peak Detection**: Identifying local maxima (peaks) in the time series using `scipy.signal.find_peaks`.
* **Range-based Analysis**:
    * **Range Max/Min/Difference**: Calculating the maximum, minimum, or difference between values within a randomly selected sub-range of the series.
* **Thresholding**:
    * Identifying all values in the series that exceed a randomly generated threshold.
* **Data Imputation/Prediction**:
    * **Linear Interpolation**: Introducing a `NaN` (missing value) at a random internal point in the series and then calculating the linearly interpolated value for that point.
    * **Next Value Prediction (Linear Regression)**: Predicting the subsequent value in a time series based on a simple linear regression model fitted to the existing data points and their corresponding time/year identifiers.
* **Comparative Analysis**:
    * **Value Comparison**: Comparing values at two randomly selected points in the series and determining if the first is greater than, less than, or equal to the second.

## Input Format
The scripts generally expect input data in **JSONL (JSON Lines) format** (`.jsonl`). Each line in the input file should be a valid JSON object representing a single time series instance.

**Example of one line in an input JSONL file:**
```json
{"id": "ts_001", "years_column": [2018, 2019, 2020, 2021, 2022], "values": [10.5, 12.3, 11.8, 13.5, 12.9]}
