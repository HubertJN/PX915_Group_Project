import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.stats import qmc
import netCDF4 as nc
import sys

inp = nc.Dataset('SPM_input_ori.nc', "r", format='NETCDF4')
dat_size = inp['no_samples'][:][0]

data = np.empty((dat_size, 9))
imported = np.zeros(9)
dists = []

try:
    temp_sd = inp['temp_std'][:][0]
    temp = inp['temp'][:][0]
    temp_dis = st.norm(temp, temp_sd)
    dists.append(temp_dis)
    imported[0] = 1
except:
    temp_sd = 0.0
    temp = inp['temp'][:][0]
    data[:, 0] = temp

try:
    rad_sd = inp['rad_std'][:][0]
    rad = inp['rad'][:][0]
    rad_dis = st.norm(rad, rad_sd)
    dists.append(rad_dis)
    imported[1] = 1
except:
    rad_sd = 0.0
    rad = inp['rad'][:][0]
    data[:, 1] = rad

try:
    thick_sd = inp['thick_std'][:][0]
    thick = inp['thick'][:][0]
    thick_dis = st.norm(thick, thick_sd)
    dists.append(thick_dis)
    imported[2] = 1
except:
    thick_sd = 0.0
    thick = inp['thick'][:][0]
    data[:, 2] = thick
    
try:
    rr_coef_sd = inp['rr_coef_std'][:][0]
    rr_coef = inp['rr_coef'][:][0]
    rr_coef_dis = st.norm(rr_coef, rr_coef_sd)
    dists.append(rr_coef_dis)
    imported[3] = 1
except:
    rr_coef_sd = 0.0
    rr_coef = inp['rr_coef'][:][0]
    data[:, 3] = rr_coef
    
try:
    dif_coef_sd = inp['dif_coef_std'][:][0]
    dif_coef = inp['dif_coef'][:][0]
    dif_coef_dis = st.norm(dif_coef, dif_coef_sd)
    dists.append(dif_coef_dis)
    imported[4] = 1
except:
    dif_coef_sd = 0.0
    dif_coef = inp['dif_coef'][:][0]
    data[:, 4] = dif_coef
    
try:
    init_c_sd = inp['init_c_std'][:][0]
    init_c = inp['init_c'][:][0]
    init_c_dis = st.norm(init_c, init_c_sd)
    dists.append(init_c_dis)
    imported[5] = 1
except:
    init_c_sd = 0.0
    init_c = inp['init_c'][:][0]
    data[:, 5] = init_c
    
try:
    max_c_sd = inp['max_c_std'][:][0]
    max_c = inp['max_c'][:][0]
    max_c_dis = st.norm(max_c, max_c_sd)
    dists.append(max_c_dis)
    imported[6] = 1
except:
    max_c_sd = 0.0
    max_c = inp['max_c'][:][0]
    data[:, 6] = max_c
    
try:
    vol_per_sd = inp['vol_per_std'][:][0]
    vol_per = inp['vol_per'][:][0]
    vol_per_dis = st.norm(vol_per, vol_per_sd)
    dists.append(vol_per_dis)
    imported[7] = 1
except:
    vol_per_sd = 0.0
    vol_per = inp['vol_per'][:][0]
    data[:, 7] = vol_per
    
try:
    iapp_sd  = inp['iapp_std'][:][0]
    iapp = inp['iapp'][:][0]
    iapp_dis = st.norm(iapp, iapp_sd)
    dists.append(iapp_dis)
    imported[8] = 1
except:
    iapp_sd = 0.0
    iapp = inp['iapp'][:][0]
    data[:, 8] = iapp

num_vars = int(np.sum(imported))

sampler = qmc.LatinHypercube(d=num_vars)
sample = sampler.random(n=dat_size)

j = 0
for i in range(9):
    if (imported[i] == 1):
        data[:, i] = dists[j].ppf(sample[:, j])
        j += 1
    else:
        continue
mu = [temp, rad, thick, rr_coef, dif_coef, init_c, max_c, vol_per, iapp]

data[0, :] = mu

dat_fram = {'temp': data[:, 0],
            'rad': data[:, 1],
            'thick': data[:, 2],
            'rr_coef': data[:, 3],
            'dif_coef': data[:, 4],
            'init_c': data[:, 5],
            'max_c': data[:, 6],
            'vol_per': data[:, 7],
            'iapp': data[:, 8],
            }
df = pd.DataFrame(dat_fram, columns=['temp', 'rad', 'thick', 'rr_coef', 'dif_coef', 'init_c', 'max_c', 'vol_per', 'iapp'])
df.to_csv('data.csv', index=False)

if (sys.argv[1] == 'True'):
    sim_steps = inp['sim_steps'][:][0]
    dV_dx = np.empty((9, sim_steps))
    
    sens_dat = pd.read_csv('./data_store_sens/sens_data.csv')
    
    dV_dx[0,:] = sens_dat['temp_dvdx'][:]
    dV_dx[1,:] = sens_dat['rad_dvdx'][:]
    dV_dx[2,:] = sens_dat['thick_dvdx'][:]
    dV_dx[3,:] = sens_dat['rr_coef_dvdx'][:]
    dV_dx[4,:] = sens_dat['dif_coef_dvdx'][:]
    dV_dx[5,:] = sens_dat['init_c_dvdx'][:]
    dV_dx[6,:] = sens_dat['max_c_dvdx'][:]
    dV_dx[7,:] = sens_dat['vol_per_dvdx'][:]
    dV_dx[8,:] = sens_dat['iapp_dvdx'][:]

    #so now set covariance matrix
    #here is a placeholder where the standard deviations are 1%
    std_devs = [temp_sd, rad_sd, thick_sd, rr_coef_sd, dif_coef_sd, init_c_sd, max_c_sd, vol_per_sd, iapp_sd] #0.01*mu
    Sigma = np.zeros((len(mu),len(mu)))
    for i in range(len(std_devs)):
        Sigma[i,i] = std_devs[i]**2
    
    #Now calculate covariance matrix of V in time
    #The diagonal entries are the actual variance of V at each time
    #Off-diagonal entries are correlations - not important here
    var_V = dV_dx.T @ Sigma @ dV_dx

    #extract standard deviations
    std_V = np.zeros(sim_steps)
    for i in range(sim_steps):
        std_V[i] = np.sqrt(var_V[i,i])
    std_dat_fram = {'std_V': std_V}
    df = pd.DataFrame(std_dat_fram, columns=['std_V'])
    df.to_csv('std_V_dat.csv', index=False)
    

print(dat_size)