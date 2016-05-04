from matplotlib import pyplot

def plot(data_list, title=None, file_name=None):
    for name,data in data_list:
        pyplot.plot(range(len(data)), data, label=name)
    pyplot.legend()
    pyplot.xlabel('iterations')
    pyplot.ylabel('concentration')

    if title:
        pyplot.title(title)

    if file_name:
        pyplot.savefig(file_name)
    else:
        pyplot.show()
