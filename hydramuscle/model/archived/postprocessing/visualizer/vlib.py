#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.animation as anim
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d import axes3d, Axes3D

def save_anim(x, interval, filename, canvas = 'flat', show = True):
    # Convert the 2D data into a video and save it
    fig = plt.figure()
    ims = []

    values = x.values
    time_len = len(values)
    space_len = int(np.sqrt(len(values[0])))

    x = np.reshape(values, (time_len, space_len, space_len))

    if canvas == "flat":
        for j in tqdm(range(np.int(len(x)/interval))):
            im = plt.imshow(x[interval * j], cmap = 'Greens', animated = True, vmin=1, vmax=2.5)
            ims.append([im])

    elif canvas == "cylindar":
        pass

    ani = anim.ArtistAnimation(fig, ims, interval = 1, blit=False, repeat = True)
    ani.save(filename, writer="ffmpeg")
    if show: plt.show()

def save_pattern(x, filename, save = True, show = True, size = (20, 20)):
    # Save the 2D/1D data as a spatiotemporal pattern
    ax = plt.figure(figsize = size).gca()
    x = x.T
    im = plt.imshow(x, aspect = 'auto')
    plt.ylabel('Cell #')
    plt.xlabel('t [ms]')
    if save:    ax.savefig(filename)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    cb = plt.colorbar()
    cb.set_label("Fluorescence [A.U.]")
    if show:    plt.show()

def save_curve(x, dt, xlabel, ylabel, title, filename, show = True, save = True):
    # Save the data as curve figure
    fig = plt.figure()
    if type(x) != np.ndarray:    x = x.values
    t = np.arange(0, len(x)*dt, dt)
    plt.plot(t, x, color='k')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if save:    fig.savefig(filename)
    if show:    plt.show()

def vplot(pars, model, tmin=0 , tmax = 100, separate = True,
          xlabel = 'time[s]', ylabels = None, 
          colors = 'b', size = (15,8), legend = None):
    plt.figure(figsize = size)
    num = len(pars)
    nrow = np.floor(np.sqrt(num))
    ncol = np.ceil(num/nrow)
    
    for j in range(num):
        if separate: plt.subplot(nrow, ncol, j+1)
        model.plot(a = pars[j], tmin = tmin, tmax = tmax, xlabel = xlabel,
                   ylabel = ylabels[j] if ylabels else None,
                  color = colors if len(colors) == 1 else colors[j])
    if legend: plt.legend(legend)
    plt.show()   

def plot_frame(x, t, dt):
    ncels = len(x[0])
    x = np.reshape(x, (-1, int(np.sqrt(ncels)), int(np.sqrt(ncels))))
    frame = x[int(t/dt)]
    plt.figure()
    plt.imshow(frame, vmin=0, vmax=2)
    plt.colorbar()
    plt.show()

def plot_frames(data, nx, ny, ts, dt, vmin, vmax):
    ntime = len(data)
    data = np.reshape(data, (-1, nx, ny))

    nrow = 2
    ncol = int(np.ceil(len(ts)/nrow))

    fig = plt.figure(figsize=(20,10))
    
    for j in range(len(ts)):
        t = ts[j]
        plt.subplot(nrow, ncol, j+1)
        frame = data[int(t/dt)]
        plt.imshow(frame, cmap='hot', vmin=vmin, vmax=vmax)
        plt.colorbar()
        plt.title('t=' + str(t) + 's')

    plt.show()

if __name__ == '__main__':
    
    # x = pd.read_csv('../save/data/c_20x20_100s.csv')
    # # save_pattern(x, '../save/figures/grid_pattern.png')
    # save_anim(x, 1, '../save/animations/grid_movie.mp4')

    x = pd.read_csv('../save/data/c_20x20_100s.csv')
    # save_pattern(x, '../save/figures/chain_fluo_pattern.png')
    # save_anim(x, 1, '../save/animations/grid_fluo_movie.mp4')
    # plot_frames(x.values, [11, 20, 30], 0.1, 1.0)