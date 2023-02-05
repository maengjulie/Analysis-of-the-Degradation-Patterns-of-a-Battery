

'''
Fischer's exact test (R package); to determine if there are nonrandom associations between each cluster pair.
: The code is written for the dataset produced by profiling.
: The code runs for a single component (separated by excel sheets), and outputs a visualized table containing the p-values for each pair.
: Green indicates that the p-value is significant (<0.05).

* If there is only one observation between the cluster pairs (i.e. only one observation exists for a component in each cluster),
Fischer test is replaced by Chi-Squared test (due to package error). If this is the case, plot is saved with '_chi' at the end of its name


'''
# Import packages
import pandas as pd
import numpy as np
import rpy2.robjects.numpy2ri
from rpy2.robjects.packages import importr
import imgkit
import os
from scipy.stats import chisquare
import math
import shutil


components=['C_rate', 'Temperature', 'Voltage_Balanced', 'Components', 'CMPNT_Category'] # the order of sheet names in the input file

# define parameters
component = "C_rate" # component of interest (the sheet name)
df = pd.read_excel('battery_info_K25.xlsx', sheet_name=[index for index, c in enumerate(components) if c == component][0]) # define data and sheet name
use_original_cluster_order = False
od = [9,24,23,12,1,28,15,2,26,3,14,4,10,11,16,8,22,25,27,6,5,29,17,7,13] # Specify order of clusters by cycle length, in increasing order
con = imgkit.config(wkhtmltoimage="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltoimage.exe") # specify path to wkhtmltoimage.exe




df = df.fillna(0)

if use_original_cluster_order:
    od = df['cluster'].unique()

# Fisher Exact Test
rpy2.robjects.numpy2ri.activate() # import R package
stats = importr('stats')

significant_pairs = []
insignificant_pairs = []
num_clusters = len(od)

# Functions for table visualization
def highlight_significant(s, props=''):
    return np.where(s < 0.05, props, '')
def highlight_not_significant(s, props=''):
    return np.where(s > 0.05, props, '')
def highlight_na(s, props=''):
    return np.where(s.isna(), props, '')


cluster_names = ['cluster_{}'.format(x) for x in od]

current_directory = os.getcwd()

# perform test on sheet name with 'CMPNT_Category' or 'Components'. This is coded separately since they contain multiple components instead of one
if component == 'CMPNT_Category' or component == 'Components':
    chi_required = [] # record components that need chi squared test because there is only one data point
    components_list = df['level_1'].unique()
    for n in components_list:
        if (df[df['cluster']==1]['level_1'] == n).sum() == 1:
            chi_required.append(n)
    #print(chi_required)

    if component == 'CMPNT_Category': # different factors to analyze for each sheet
        columns_val = 'value'
        values_val = 'count'
    else:
        columns_val = 'level_1'
        values_val = 'pct%'

    final_directory = os.path.join(current_directory, r'statistical_test_result_{}'.format(component)) # create folder to save results
    if os.path.exists(final_directory):
        shutil.rmtree(final_directory)
    os.makedirs(final_directory)
    os.chdir(final_directory) # working in the created folder now

    for x in components_list: # consider each possible pairs of clusters, and go through each component
        values = []
        for i in od:
            p = []
            for j in od:
                if i != j:
                    table = df[df['cluster'].isin([i, j])]
                    tbl = table[table['level_1'] == x]
                    t = tbl.pivot(index='cluster', columns=columns_val, values=values_val)
                    if x in chi_required: # chi test if only one data is available for the component in the cluster pair
                        p_value = chisquare(t.to_numpy()).pvalue[0] # calculate p-value for the component in each cluster pair
                        name = '_chi'
                        if math.isnan(p_value):
                            p_value = 1
                    else:
                        res = stats.fisher_test(t.to_numpy(), workspace=2e7) # fischer test
                        p_value = res[0][0] # calculate p-value for the component in each cluster pair
                        name = ''
                    # classify significant and insignificant pairs
                    if p_value < 0.05:
                        significant_pairs.append((i, j))
                    else:
                        insignificant_pairs.append((i, j))
                else:
                    p_value = float("NaN") # for self- pairs
                p.append(p_value)
            values.append(p)
        r2 = pd.DataFrame(values, index=cluster_names, columns=cluster_names)
        #highlight significant pairs with green, grey for self pairs
        final_table = r2.style.apply(highlight_significant, props='background-color:lightgreen', axis=0) \
            .apply(highlight_na, props='color:grey;background-color:grey')
        html = final_table.render()
        imgkit.from_string(html, 'stats_test_{}{}.png'.format(x, name), config=con) # add "_chi" if chi-squared is performed instead of fischer
        print("----component {} done".format(x))
    os.chdir(current_directory)

# perform same test on other components
else:
    values = []
    for i in od:
        p = []
        for j in od:
            if i != j:
                table = df[df['cluster'].isin([i, j])]
                t = table.pivot(index='cluster', columns='value', values='count')
                res = stats.fisher_test(t.to_numpy())
                p_value = res[0][0]
                print('{} and {} p-value: {}'.format(i, j, p_value))
                if p_value < 0.05:
                    significant_pairs.append((i, j))
                else:
                    insignificant_pairs.append((i, j))
            else:
                p_value = float("NaN")
            p.append(p_value)
        values.append(p)
    r2 = pd.DataFrame(values, index=cluster_names, columns=cluster_names)
    final_table = r2.style.apply(highlight_significant, props='background-color:lightgreen', axis=0) \
        .apply(highlight_na, props='color:grey;background-color:grey')
    html = final_table.render()
    imgkit.from_string(html, 'stats_test_{}.png'.format(component), config=con)
    print("-------------component {} done".format(component))


'''#Check pairs if necessary
sig_pairs = list({*map(tuple, map(sorted, significant_pairs))})
sig_pairs.sort(key=lambda x:x[0])
insig_pairs = list({*map(tuple, map(sorted, insignificant_pairs))})
insig_pairs.sort(key=lambda x:x[0])'''



