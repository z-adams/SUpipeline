import scipy.io as sio

path = raw_input("Where is the data file?: ")
x = sio.loadmat(path)

for i in range(100):
    for j in range(100):
        for k in range(100):
            if x['G'][i][j][k] > 0:
                print "({},{},{})".format(i, j, k)
