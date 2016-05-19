from matplotlib import pyplot

def plot(data_list, title=None, file_name=None):
    """
    A simple function for plotting and displaying data.
    The |data_list| contains tuples of names to lists of data.
    An optional |title| can be provided.
    If |file_name| is specified, the plot will be saved to a file with the
        given name.
    """
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
