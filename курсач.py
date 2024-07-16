import pandas as pd
import matplotlib.pyplot as plt

# Средняя почасовая заработная плата работников в разбивке по полу и роду занятий
data_first = pd.read_csv('EAR_4HRL_SEX_OCU_CUR_NB_A.csv')
# Среднемесячный заработок работников в разбивке по полу и роду занятий
data_second = pd.read_csv('EAR_4MTH_SEX_OCU_CUR_NB_A.csv')
# Национальный индекс потребительских цен (ИПЦ) по КИПЦ, процентное изменение по сравнению с предыдущим годом
data_third =  pd.read_csv('CPI_NCYR_COI_RT_A.csv')

ref_area =  pd.read_csv('ref_area_en.csv') 
sex = pd.read_csv('sex_en.csv')
classif1 = pd.read_csv('classif1_en.csv')
classif2 = pd.read_csv('classif2_en.csv')


merged_data_first = pd.merge(data_first, ref_area.rename(columns={' ref_area.label': 'ref_area_label'}), on='ref_area', how='inner')
merged_data_first = pd.merge(merged_data_first, sex.rename(columns={' sex.label': 'sex_label'}), on='sex', how='inner')
merged_data_first = pd.merge(merged_data_first, classif1.rename(columns={' classif1.label': 'classif1_label'}), on='classif1', how='inner')
merged_data_first = pd.merge(merged_data_first, classif2.rename(columns={' classif2.label': 'classif2_label'}), on='classif2', how='inner')

merged_data_first = merged_data_first[['ref_area','ref_area_label', 'sex_label', 'classif1_label', 'classif2_label', 'time', 'obs_value']]

merged_data_second = pd.merge(data_second, ref_area.rename(columns={' ref_area.label': 'ref_area_label'}), on='ref_area', how='inner')
merged_data_second = pd.merge(merged_data_second, sex.rename(columns={' sex.label': 'sex_label'}), on='sex', how='inner')
merged_data_second = pd.merge(merged_data_second, classif1.rename(columns={' classif1.label': 'classif1_label'}), on='classif1', how='inner')
merged_data_second = pd.merge(merged_data_second, classif2.rename(columns={' classif2.label': 'classif2_label'}), on='classif2', how='inner')

merged_data_second = merged_data_second[['ref_area','ref_area_label', 'sex_label', 'classif1_label', 'classif2_label', 'time', 'obs_value']]

merged_data_third = pd.merge(data_third, ref_area.rename(columns={' ref_area.label': 'ref_area_label'}), on='ref_area', how='inner')
merged_data_third = pd.merge(merged_data_third, classif1.rename(columns={' classif1.label': 'classif1_label'}), on='classif1', how='inner')

merged_data_third = merged_data_third[['ref_area', 'classif1_label', 'time', 'obs_value']]

merged_data_first_ref_area = merged_data_first['ref_area'].unique()
merged_data_second_ref_area= merged_data_second['ref_area'].unique()

ref_area_list = [x for x in merged_data_first_ref_area if x in merged_data_second_ref_area]
print(ref_area_list)
ref_area_TAG = 'USA'
Sex_TAG = 'Sex: Total'
# 'Sex: Male' 'Sex: Female' 'Sex: Total' 
merged_data_first_USA = merged_data_first[(merged_data_first.ref_area == ref_area_TAG) & (merged_data_first.sex_label == Sex_TAG) & (merged_data_first.classif2_label == 'Currency: Local currency')]
merged_data_second_USA = merged_data_second[(merged_data_second.ref_area == ref_area_TAG) & (merged_data_second.sex_label == Sex_TAG) & (merged_data_second.classif2_label == 'Currency: Local currency')]
merged_data_third_USA = merged_data_third[(merged_data_third.ref_area == ref_area_TAG)]

merged_data_first_USA_classif1_label = merged_data_first_USA['classif1_label'].unique()
classif1_label_list = [x for x in merged_data_first_USA_classif1_label]
for i, x in enumerate(classif1_label_list):
   print(i, x)

x = int(input('номер рода занятий '))
if(0 <= x and x <= 13):
  classif1_TAG = classif1_label_list[x]
else:
   classif1_TAG = "Occupation (ISCO-08): Total"
# classif1_TAG = "Occupation (ISCO-08): Total"
data_first_managers = merged_data_first_USA[merged_data_first_USA.classif1_label == classif1_TAG]
data_second_managers = merged_data_second_USA[merged_data_second_USA.classif1_label == classif1_TAG]

merged_data_managers = pd.merge(data_first_managers[['time', 'obs_value']].rename(columns={'obs_value': 'hourly_earnings'}), 
                                data_second_managers[['time', 'obs_value']].rename(columns={'obs_value': 'monthly_earnings'}), 
                                on='time', how='inner')
merged_data_managers.dropna(inplace=True)

if(ref_area_TAG == 'SWE'):
    arr_hourly_earnings = [2015, 2016, 2017, 2018, 2019, 2020, 2022]
    arr_monthly_earnings = [2014, 2015, 2016, 2017, 2018, 2019, 2020]
    merged_data_managers.loc[merged_data_managers['time'].isin(arr_hourly_earnings), 'hourly_earnings'] *= 0.1
    merged_data_managers.loc[merged_data_managers['time'].isin(arr_monthly_earnings), 'monthly_earnings'] *= 0.1

print(merged_data_managers)
merged_data_managers['hours'] = merged_data_managers['monthly_earnings'] / merged_data_managers['hourly_earnings']
merged_data_managers = merged_data_managers.set_index('time').sort_index()

pivot_data = (merged_data_third_USA[merged_data_third_USA['classif1_label'] == 'COICOP2012: General - Individual consumption expenditure of households']
                .pivot_table(values='obs_value', index='time', aggfunc='mean')
                .rename(columns={'obs_value': 'General CPI'})
                .sort_index())

pivot_data = pivot_data.apply(lambda old_value: 1 + old_value / 100)
print(pivot_data)

for i in range(len(pivot_data) - 3, -1, -1):
    pivot_data.loc[pivot_data.index[i], 'General CPI'] *= pivot_data.loc[pivot_data.index[i + 1], 'General CPI']

pivot_data.loc[2023, 'General CPI'] = 1.0
print(pivot_data)  
print(merged_data_managers)

merged_data_with_cpi = merged_data_managers.copy().join(pivot_data, how='left')
merged_data_with_cpi[['hourly_earnings', 'monthly_earnings']] *= merged_data_with_cpi['General CPI'].values[:, None]
merged_data_with_cpi.drop(columns=['General CPI'], inplace=True)

print(merged_data_with_cpi)

fig, axs = plt.subplots(3, 2, figsize=(12, 12))


for i, column in enumerate(['hourly_earnings', 'monthly_earnings', 'hours']):
    axs[i, 0].plot(merged_data_managers.index, merged_data_managers[column], marker='o', linestyle='-')
    axs[i, 0].set_ylabel(column.replace('_', ' ').capitalize())
    axs[i, 0].grid(True)

for i, column in enumerate(['hourly_earnings', 'monthly_earnings', 'hours']):
    axs[i, 1].plot(merged_data_with_cpi.index, merged_data_with_cpi[column], marker='o', linestyle='-')
    axs[i, 1].set_ylabel(column.replace('_', ' ').capitalize())
    axs[i, 1].grid(True)

fig.suptitle(data_first_managers['ref_area_label'].iloc[0] + " " + data_first_managers['classif1_label'].iloc[0], fontsize=16)

plt.tight_layout()
plt.show()