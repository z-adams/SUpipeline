import numpy as np
import matplotlib.pyplot as plt


def plot(output_path):
    lines = []

    with open(output_path, "r") as f:
        for line in f:
            lines.append(line)

    matrix = []

    for line in lines:
        matrix.append([float(f) for f in line.split()])

    mat = np.array(matrix)
    plt.imshow(mat)
    plt.show()

if __name__ == "__main__":
    plot("output.txt")
