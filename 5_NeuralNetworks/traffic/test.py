import matplotlib.pyplot as plt


plt.figure(figsize=(10,10))
    for i in range(25):
        plt.subplot(5,5,i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        # The CIFAR labels happen to be arrays,
        # which is why you need the extra index
        plt.xlabel(i)

    plt.ion()
plt.show()
