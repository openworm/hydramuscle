import os
import datetime
import pandas as pd
import argparse

from hydramuscle.model.smc import SMC
from hydramuscle.model.layer import Layer
from hydramuscle.model.shell import Shell

def run_shell(numx, numy, seed, gip3x, gip3y, gcx, gcy, sparsity, gc, gip3,
              save_interval, save_dir, randomnum, **kargs):
    
    # Check the existence of the saving directory
    if not save_dir.endswith('/'):
        save_dir += '/'
    if not os.path.isdir(save_dir):
        raise FileExistsError("Target directory " + save_dir + " does not exist. ")

    # Build layers
    smc = SMC(**kargs)
    ectoderm = Layer(smc, numx=numx, numy=numy, gip3x=gip3x, gip3y=gip3y,
                     gcx=gcx, gcy=gcy, save_interval=save_interval)
    endoderm = Layer(smc, numx=numx, numy=numy, gip3x=gip3x, gip3y=gip3y,
                     gcx=gcx, gcy=gcy, save_interval=save_interval)
    
    # Define stimulation times
    stims_fast = []
    stims_slow1 = [10]
    # stims_slow2 = [15]
    # stims_slow3 = [20]

    # Set stimulation patterns
    ectoderm.set_stim_pattern("slow", xmin=0, xmax=-1, ymin=0, ymax=-1,
                              stim_times=stims_slow1, randomnum=randomnum)
    # ectoderm.set_stim_pattern("slow", xmin=0, xmax=-1, ymin=0, ymax=-1,
    #                           stim_times=stims_slow2, randomnum=randomnum)
    # ectoderm.set_stim_pattern("slow", xmin=0, xmax=-1, ymin=0, ymax=-1,
    #                           stim_times=stims_slow3, randomnum=randomnum)

    # Build shell
    shell = Shell(ectoderm, endoderm, seed, sparsity, gc, gip3)

    # Run the model
    sol = shell.run()
    sol = pd.DataFrame(sol)

    # Generate filename and corresponding metadata
    filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    filemeta = "numx=" + str(numx) + ","
    filemeta += "numy=" + str(numy) + ","
    filemeta += "gip3x=" + str(gip3x) + ","
    filemeta += "gip3y=" + str(gip3y) + ","
    filemeta += "randomnum=" + str(randomnum)

    for key in kargs:
        filemeta += "," + key + '=' + str(kargs[key])

    filemeta += ",slowwave"

    # Save the results
    sol.to_hdf(save_dir + filename + '.h5', 'calcium')

    # Document the metadata
    with open("../results/data/meta.txt", "a+") as metafile:
        metafile.write(filename + "    " + filemeta + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('--numx', type=int, default=200)
    parser.add_argument('--numy', type=int, default=200)
    parser.add_argument('--seed', type=int, default=896)
    parser.add_argument('--gip3x', type=float, default=5)
    parser.add_argument('--gip3y', type=float, default=40)
    parser.add_argument('--gcx', type=float, default=1000)
    parser.add_argument('--gcy', type=float, default=1000)
    parser.add_argument('--sparsity', type=float, default=0.002)
    parser.add_argument('--gc', type=float, default=1000)
    parser.add_argument('--gip3', type=float, default=5)
    parser.add_argument('--save_interval', type=int, default=100)
    parser.add_argument('--save_dir', type=str, default="../results/data/calcium")
    parser.add_argument('--randomnum', type=int, default=10)
    parser.add_argument('--T', type=float, default=100)
    parser.add_argument('--dt', type=float, default=0.0002)
    parser.add_argument('--k_ipr', type=float, default=0.2)
    parser.add_argument('--s0', type=float, default=100)
    parser.add_argument('--d', type=float, default=20e-4)
    parser.add_argument('--v_delta', type=float, default=0.04)
    parser.add_argument('--k_deg', type=float, default=0.15)
    args = parser.parse_args()

    run_shell(args.numx, args.numy, args.seed, args.gip3x, args.gip3y,
              args.gcx, args.gcy, args.sparsity, args.gc, args.gip3,
              args.save_interval, args.save_dir, args.randomnum,
              T=args.T, dt=args.dt, k_ipr=args.k_ipr, s0=args.s0,
              d=args.d, v_delta=args.v_delta, k_deg=args.k_deg)