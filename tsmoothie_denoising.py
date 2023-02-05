

'''
tsmoothie python package: vectorized time-series smoothing and outlier detection
    Link: https://github.com/cerlymarco/tsmoothie

Uses a LowessSmoother (locally-weighted scatterplot smoothing for time series)
: non-parametric regression that fits a unique linear regression for every data point by including nearby data points to
  estimate the slope and intercept.

'''



# import required packages
import pandas as pd
from tsmoothie.smoother import LowessSmoother
import matplotlib.pyplot as plt



# user defined parameters
r_df = pd.read_csv('20220325_battery_files_important_ingredients.csv', usecols=['battery_file_id', 'DischargeCapacityRetention', 'Cyc_'])
smooth_fraction = 0.1
iterations = 5



# denoise on "discharge capacity retention"
def denoise(id_number, sf, iter):
    data = r_df[r_df['battery_file_id'] == id_number]
    data = data.sort_values(by='Cyc_')

    y = data['DischargeCapacityRetention']

    # smooth_fraction: smoothing span; a larger value results in a smoother curve.
    # iterations: the number of residual-baed reweightings to perform. Maximum can be 6
    smoother = LowessSmoother(smooth_fraction=sf, iterations=iter)
    smoother.smooth(y.to_frame().T)
    smooth_result = smoother.smooth_data[0]

    dat = data.copy()
    dat['Smoothed'] = smooth_result

    return dat


# denoise full data
id_number=[]

id_numbers = r_df['battery_file_id'].unique()
appended_data=[]
for i in id_numbers:
    dat = denoise(i, smooth_fraction, iterations)
    appended_data.append(dat)
appended_data = pd.concat(appended_data, ignore_index=True)
# save the full data
appended_data.to_csv('denoise_full_data.csv')
print(appended_data)



# classify accepted & dropped
cols2 = ['battery_file_id', 'Cyc_', 'Smoothed']
full_df = pd.read_csv('denoise_full_data.csv', usecols=cols2)
#full_df = appended_data


gb = full_df.groupby('battery_file_id')
g = [gb.get_group(x) for x in gb.groups]

accepted=[]
dropped=[]
cnt_accepted=0
cnt_dropped=0
cnt=0


# "filter out" dropped cases
for i in g:
    cnt+=1
    capacity=i['Smoothed'].values
    if capacity[0] < 0.7 or max(capacity) > 1.05:
        dropped.append(i)
        cnt_dropped+=1
    else:
        cnt_accepted+=1
        acpt_val = []
        for x in i['Smoothed'].values:
            #print(idx, x)
            if x >= 0.7:
                acpt_val.append(x)
            else:
                break
        j = i[:len(acpt_val)].copy()
        j['Smoothed'] = acpt_val
        accepted.append(j)


# count the number of each cases
print('Total cases: {}'.format(cnt))
print('Dropped cases: {} ({}%)'.format(cnt_dropped, round((cnt_dropped/cnt)*100, 2)))
print('Accepted cases: {} ({}%)'.format(cnt_accepted, round((cnt_accepted/cnt)*100, 2)))

# create dataframes
accepted = pd.concat(accepted, ignore_index=True)
dropped = pd.concat(dropped, ignore_index=True)

accepted.to_csv('denoise_accepted.csv')
dropped.to_csv('denoise_droopped.csv')


# visualize dropped cases; blue=original data, red=smoothed data
print("Visualizing dropped cases")
d_df = pd.read_csv('denoise_droopped.csv')

axis_x =0
axis_y =0

num_subplot_y =10
num_subplot_x =(len(d_df['battery_file_id'].unique()) // num_subplot_y)+1

fig, axis = plt.subplots(num_subplot_x, num_subplot_y, figsize=(num_subplot_y+1, num_subplot_x+1))
fig.subplots_adjust(hspace=2 , wspace=0.8)

start = 0

id_number=d_df['battery_file_id'].unique()
for i in id_number:


    df = d_df[d_df['battery_file_id'] == i]
    df = df.sort_values(by='Cyc_')
    x_axis_vals = df['Cyc_'].values
    y_axis_vals = df['DischargeCapacityRetention'].values
    y_axis_vals2 = df['Smoothed'].values
    axis[axis_x, axis_y].plot(x_axis_vals, y_axis_vals, color='cornflowerblue', label='Discharge')
    axis[axis_x ,axis_y].plot(x_axis_vals, y_axis_vals2, color='red', label='Discharge')
    axis[axis_x ,axis_y].set_title('fileid={}'.format(i), fontsize=10)

    axis_y = axis_y +1

    if axis_y == num_subplot_y:
        axis_y = 0
        axis_x = axis_x + 1


plt.suptitle('Dropped Cases', fontsize=15)
plt.show()
plt.savefig('dropped_ids.png')


# visualize accepted cases; blue=original data, red=smoothed data
print("Visualizing accepted cases")
a_df = pd.read_csv('denoise_accepted.csv')

axis_x =0
axis_y =0

num_subplot_y =30
num_subplot_x =(len(a_df['battery_file_id'].unique()) // num_subplot_y)+1

fig, axis = plt.subplots(num_subplot_x, num_subplot_y, figsize=(num_subplot_y+1, num_subplot_x))
fig.subplots_adjust(hspace=2 , wspace=0.8)

start = 0

id_number=a_df['battery_file_id'].unique()
for i in id_number:
    df = a_df[a_df['battery_file_id'] == i]
    df = df.sort_values(by='Cyc_')
    x_axis_vals = df['Cyc_'].values
    y_axis_vals = df['DischargeCapacityRetention'].values
    y_axis_vals2 = df['Smoothed'].values
    axis[axis_x ,axis_y].plot(x_axis_vals, y_axis_vals, color='cornflowerblue', label='Discharge') # original retention data
    axis[axis_x ,axis_y].plot(x_axis_vals, y_axis_vals2, color='red', label='Discharge') # smoothed retention data
    axis[axis_x ,axis_y].set_title('fileid={}'.format(i), fontsize=10)
    axis_y = axis_y +1
    if axis_y == num_subplot_y:
        axis_y = 0
        axis_x = axis_x + 1


plt.suptitle('Accepted Cases', fontsize=30)
plt.show()
plt.savefig('accepted_ids.png')