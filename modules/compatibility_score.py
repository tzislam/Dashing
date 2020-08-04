import math
import warnings
from copy import deepcopy

import numpy as np
import scipy
from scipy import linalg
from scipy.stats import entropy
from sklearn import decomposition
from sklearn.preprocessing import StandardScaler
from sklearn.utils.extmath import svd_flip

from util.dKL import dKL
from util.pcaOrig import pcaOrig

#NOTES:
#Single features passed in to the program always return a value of 0.

def compat_task(data_loaders, global_options):

    compat_pair_strings = global_options['compat_pairs']
    for compat_pair_str in compat_pair_strings:
        key_reg1, key_reg2 = compat_pair_str.split(',')
        dl1_name, reg1 = key_reg1.split(':', 1)
        dl2_name, reg2 = key_reg2.split(':', 1)

        dl1 = data_loaders[dl1_name]
        dl2 = data_loaders[dl2_name]

        print("%s regions: %s" % (dl1_name, dl1.get_regions()))
        print("%s regions: %s" % (dl2_name, dl2.get_regions()))

        print("Starting %s vs. %s\n---------------------------------"
            % (key_reg1, key_reg2))

        if set(dl1.proc_configs) != set(dl2.proc_configs):
            print("ERROR: proc configurations aren't the same")
            continue
        
        ev1 = set(dl1.get_events())
        ev2 = set(dl2.get_events())

        ev_diff = ev1.difference(ev2)
        events = ev1.intersection(ev2)

        if len(ev_diff) != 0:
            print("Removed %d events for not being present in both datasets" % len(ev_diff))
        
        compat_results = {}
        resource_map = dl1.res_to_ev_map
        for res in resource_map:
            event_keys = resource_map[res]
            event_keys = [key for key in event_keys if key in events]

            if event_keys:
                key1 = reg1 if reg1 in dl1.get_regions() else reg2
                key2 = reg1 if reg1 != key1 else reg2

                data1 = dl1.get_app_data(key1, keys=event_keys, rescale=True)
                data2 = dl2.get_app_data(key2, keys=event_keys, rescale=True)

                score = compat_score(data1, data2)
            else:
                score = np.nan

            compat_results[res] = score
            prefix = '%s-score: ' % res
            print(prefix.rjust(20), '%0.3f' % score)
        
        if 'compat_results' not in dl1:
            dl1['compat_results'] = {}
        if 'compat_results' not in dl2:
            dl2['compat_results'] = {}
        
        dl1['compat_results'][compat_pair_str] = deepcopy(compat_results)
        dl2['compat_results'][compat_pair_str] = deepcopy(compat_results)




def compat_score(app_data, proxy_data):
    OPT_THRESHOLD = 0.4
    
    app_data = app_data.copy()
    proxy_data = proxy_data.copy()
    joint_data = np.concatenate((app_data, proxy_data), axis=1)
    num_samples, num_features = app_data.shape


    _, _, V_app = get_svd(app_data)
    _, _, V_proxy = get_svd(proxy_data)
    if num_features >= num_samples:
        _, _, V_joint = get_svd(joint_data)

        alpha = get_principal_angles(V_app, V_joint)
        beta = get_principal_angles(V_proxy, V_joint)
        theta = 0.5 * (np.sin(alpha) + np.sin(beta))

        dim_opt = len(theta)
        for i in range(len(theta)):
            if theta[i] > OPT_THRESHOLD:
                dim_opt = i
                break
        V_app = V_app[:dim_opt, :]
        V_proxy = V_proxy[:dim_opt, :]
    else:
        dim_opt = num_features


    theta = get_principal_angles(V_app.T, V_proxy.T)
    for i in range(len(theta)):
        if np.isclose(theta[i], 0.0, atol=1e-6):
            diff = abs(app_data[i, :] - proxy_data[i, :])
            theta[i] = np.dot(diff, diff.T)


    score = 0
    for i in range(dim_opt):
        app_proj = np.dot(V_app[i, :], app_data.T)
        proxy_proj = np.dot(V_proxy[i, :], proxy_data.T)

        app_mu, app_sigma = np.mean(app_proj), np.std(app_proj)
        proxy_mu, proxy_sigma = np.mean(proxy_proj), np.std(proxy_proj)


        if np.isclose(app_mu, 0.0, atol=1e-6):
            app_mu = 0.0
        if np.isclose(app_sigma, 0.0, atol=1e-6):
            app_sigma = 0.0
        if np.isclose(proxy_mu, 0.0, atol=1e-6):
            proxy_mu = 0.0
        if np.isclose(proxy_sigma, 0.0, atol=1e-6):
            proxy_sigma = 0.0


        if proxy_sigma != 0.0 and app_sigma != 0.0:
            kl1 = kl(app_mu, proxy_mu, app_sigma, proxy_sigma)
            kl2 = kl(proxy_mu, app_mu, proxy_sigma, app_sigma)
        else:
            kl1 = np.nan
            kl2 = np.nan


        if np.isfinite(kl1) and np.isfinite(kl2):
            score_incr = theta[i]*0.5*(kl1 + kl2)
        else:
            score_incr = theta[i]*(abs(app_mu - proxy_mu) + abs(app_sigma - proxy_sigma))

        '''
        print("\nApp mean, std: (%0.3f, %0.3f)" % (app_mu, app_sigma))
        print("Proxy mean, std: (%0.3f, %0.3f)" % (proxy_mu, proxy_sigma))
        print("kl1, kl2: (%0.3f, %0.3f)" % (kl1, kl2))
        print("Theta (radians): %0.3f" % theta[i])
        print("Theta (degrees): %0.3f" % np.degrees(theta[i]))
        print("Score incr: %0.3f" % score_incr)
        '''
        
        score += score_incr
    
    score = 1 - (score/dim_opt)
    return score

def get_principal_angles(basis_1, basis_2):
    _, sig, _ = get_svd(np.dot(basis_1.T, basis_2))
    # Fix bad values
    sig[sig>1.0] = 1.0
    sig[sig<0.0] = 0.0
    theta = np.arccos(sig)
    
    return theta

def get_svd(X):
    U, S, V = np.linalg.svd(X, full_matrices=False)
    U, V = svd_flip(U, V)

    return U, S, V

def kl(mu0, mu1, sigma0, sigma1):
    # https://stats.stackexchange.com/questions/234757/how-to-use-kullback-leibler-divergence-if-mean-and-standard-deviation-of-of-two
    return abs(np.log(sigma1/sigma0) + (sigma0**2 + (mu0-mu1)**2)/(2*(sigma1**2)) - 0.5)
