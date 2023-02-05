# Analysis-of-the-Degradation-Patterns-of-a-Battery
*w. Solvay Korea, Ewha Research Team*
## Data Deonising
*tsmoothie_denoising.py*: Denoising ("smoothing") the battery retention curves using  a LOWESS smoother (Python tsmoothie package)
* Input: Raw battery data containing columns ‘battery_file_id’, 'DischargeCapacityRetention', 'Cyc_’, etc.
* Output: Plot visualizations of discharge capacity retention for all battery ids and the csv files of the smoothing results. The original curves are in blue, and the smoothed curves are red.
![image](https://user-images.githubusercontent.com/94361544/216827665-d303102f-4d54-4eb9-b03f-dbf56c293666.png)
* Output example\
![image](https://user-images.githubusercontent.com/94361544/216827381-97f56a17-def6-48f4-b726-1e9c07c4a578.png)
## Statistical Test
*statistical_test.py*: Performing Fischer’s exact test (or chi-squared test)
* Input: profiling data that was put together for descriptive analysis of formed clusters
* Output: Table images (values of significance highlighted in green)
![image](https://user-images.githubusercontent.com/94361544/216827813-c208447e-790b-48af-b40c-a9b569ab9e61.png)
* Output example
![image](https://user-images.githubusercontent.com/94361544/216828015-f8310636-a9cc-4b0c-b5cd-4d490191d7a3.png)
## Oversampling
*SMOTEN_oversampling.py*: Oversampling the clustered data while accounting for component distributions (Python SMOTEN package)
* Input: Clustering result with meta data containing battery id, cluster, and components
* Output: 29 plots and 1 csv file
![image](https://user-images.githubusercontent.com/94361544/216827923-5172dd53-ab63-41a8-a790-1f86352c48d5.png)
* Output example
![image](https://user-images.githubusercontent.com/94361544/216827963-b46ece87-d22a-4084-b9a5-c624562ab546.png)
