from matplotlib import pyplot

def plot(data_list):
    for name,data in data_list:
        pyplot.plot(range(len(data)), data, label=name)
    pyplot.legend()
    pyplot.show()
