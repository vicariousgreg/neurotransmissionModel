# Stochastic tools

from random import betavariate

def beta(maximum, noise=0.0, rate=1.0):
    """
    """
    if rate < 0.0 or noise < 0.0: raise ValueError
    ratio = 1/(0.0001+rate)
    a = 1.0+(100.0*(1.0-noise))
    b = ratio * a
    return maximum*(betavariate(a,b))

'''
for noise in [0.0, 0.5, 1.0]:
    for rate in [0.0, 1.0, 10.0]:
        print(noise,rate)
        for _ in xrange(5):
            print(beta(1.0, noise=noise, rate=rate))
        print("")
'''
