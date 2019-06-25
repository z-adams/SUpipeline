import scipy.io as sio

filename = raw_input("Where is the data file?: ")
x = sio.loadmat(filename)

for i in range(50):
    for j in range(50):
        for k in range(50):
            if x['G'][i][j][k] > 0:
                print "({},{},{}): {}".format(i, j, k, x['G'][i][j][k])
