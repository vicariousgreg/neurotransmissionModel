from stochastic import beta

def stochastic_bind(available_mols, available_spots, affinity=0.5, verbose=False):
    # Check available molecules
    if available_mols <= 0: return 0.0

    # Sample available molecules
    sample = beta(available_mols, rate=2)
    bound = sample * available_spots * affinity

    if verbose: print("Bound %f" % bound)

    # Bind sampled molecules
    return bound

def stochastic_release(available_mols, release_rate, verbose=False):
    # Stochastically sample bound molecules
    sample = beta(available_mols, rate=release_rate)

    if verbose: print("Removed %f molecules" % sample)

    # Release sampled molecules
    return sample
