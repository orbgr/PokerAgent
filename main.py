import sys, argparse

from train import train as Train
from play import play as Play

def main():

    orig_stdout = sys.stdout
    f = orig_stdout

    parser.add_argument('-l', action="store", default=0,dest="learn",nargs='?',type=int,help='Learn boolean[default], else 0 for play')
    parser.add_argument('-n', action="store", dest="games", nargs='?',default=2,type=int,  help='Number of trainings/learnings[default 10k]')
    parser.add_argument('-a', action="store",nargs='?', default=0.3,dest="alpha", type=float,  help='alpha[default 0.3]')
    parser.add_argument('-g', action="store", nargs='?',default=0.2,dest="gamma", type=float,  help='gamma[default 0.2]')
    parser.add_argument('-m', action="store", nargs='?',default=1,dest="mode", type=float,  help='Mode: if 0 against random, if 1 against u')


    args = vars(parser.parse_args())
    if not args["mode"]:
        f = open('gui-'+str(args["mode"])+'_learn-'+str(args["learn"])+'_analyse_' + str(args["games"]) + '_a='+str(args["alpha"])+'_g='+str(args["gamma"])+'.txt', 'a')
        sys.stdout = f
    else:
        args["learn"] = 0
        args["games"] += 1

    Train(args["games"],args["learn"],args["alpha"],args["gamma"])
    Play(args["games"],not args["learn"],f,orig_stdout,args["mode"])

    # Train(2, 1,0.2,0.2)
    # Play(numberPlays=2,playing=1,file_out=f,stdout=orig_stdout, mode=0)

    sys.stdout = orig_stdout
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    main()
