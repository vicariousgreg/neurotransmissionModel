from matplotlib import pyplot

def plot(data_list, file_name=None):
    for name,data in data_list:
        pyplot.plot(range(len(data)), data, label=name)
    pyplot.legend()
    pyplot.xlabel('iterations')
    pyplot.ylabel('concentration')
    if file_name:
        pyplot.savefig(file_name)
    else:
        pyplot.show()
