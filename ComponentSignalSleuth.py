# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 10:42:06 2024

@author: quiks
"""

# --------------------------------------------------------- Necessary Libraries  ---------------------------------------------------------
import os
import deareis          
import pandas as pd
from scipy import stats

# --------------------------------------------------------- Change These Variables -------------------------------------------------------------
ECM = 'R(Q[RQ])'
directoryA = r'C:\Users\quiks\OneDrive\Documents\SEEDS\DATA\testA'
directoryB = r'C:\Users\quiks\OneDrive\Documents\SEEDS\DATA\testB'
alpha = 0.05
numEvals = 100 #Bigger number is slower but produces more accurate fits

# --------------------------------------------------------- Plug and Chug -------------------------------------------------------------
paramsECM, resultsA, resultsB = [], pd.DataFrame([]), pd.DataFrame([]) 

print('Working on Folder A...')
for root, dirs, files in os.walk(directoryA):
    for filename in files:
        temp = []
        data = deareis.parse_data(os.path.join(root, filename))
        settings = deareis.FitSettings(ECM, method = '10', weight = 'AUTO', max_nfev = numEvals) 
        fit = deareis.fit_circuit(data[0], settings)
        for d in fit.parameters.keys():
            for e in fit.parameters[d]:
                temp.append(fit.parameters[d][e].value)
        temp = pd.DataFrame(temp).T
        resultsA = pd.concat([resultsA, temp])
        print((len(resultsA) / len(files)) * 100)
        
print('Working on Folder B...')        
for root, dirs, files in os.walk(directoryB):
    for filename in files:
        temp = []
        data = deareis.parse_data(os.path.join(root, filename))
        settings = deareis.FitSettings(ECM, method = '10', weight = 'AUTO', max_nfev = numEvals) 
        fit = deareis.fit_circuit(data[0], settings)
        for d in fit.parameters.keys():
            for e in fit.parameters[d]:
                temp.append(fit.parameters[d][e].value)
        temp = pd.DataFrame(temp).T
        resultsB = pd.concat([resultsB, temp])
        print((len(resultsB) / len(files)) * 100)        
print('DONE!')
        
for d in fit.parameters.keys():
    for e in fit.parameters[d]:
        paramsECM.append(d + '_' +e)
paramsECM[0] = 'R_sol'
resultsA.columns, resultsB.columns = paramsECM, paramsECM    

# --------------------------------------------------------- Stats Magic -------------------------------------------------------------
meanA, meanB = pd.DataFrame(resultsA.astype('float64').mean(axis = 0, numeric_only = True)), pd.DataFrame(resultsB.astype('float64').mean(axis = 0, numeric_only = True))
stdA, stdB = pd.DataFrame(resultsA.astype('float64').std(numeric_only = True)), pd.DataFrame(resultsB.astype('float64').std(numeric_only = True))
tStat, pVal = stats.ttest_ind(resultsA, resultsB, equal_var = False)
testResults = []
for i in pVal:
    if i > alpha: testResults.append('fail')
    else: testResults.append('PASS')
tTest, pVal, testResults = pd.DataFrame(tStat, index = paramsECM), pd.DataFrame(pVal, index = paramsECM), pd.DataFrame(testResults, index = paramsECM)
out = pd.concat([meanA, meanB, stdA, stdB, tTest, pVal, testResults], axis = 1)
out.columns = ['Average A', 'Average B', 'StDev A', 'StDev B', 't Value', 'p Value', 'Significant?']
out.to_csv('out.csv')  


