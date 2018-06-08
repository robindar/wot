import numpy as np
from wot.grn import SparseOptimization
from scipy.stats import entropy
import numexpr as ne
from sklearn.cluster import SpectralClustering
from itertools import combinations
import scipy


def dum(x):
    return x


def dumg(x):
    return 1


def compose_transports(Lineage, TP, lag):
    ComposedLineage = []
    for i in range(len(Lineage)):
        if len(Lineage[i]) > 0:
            j = i + 1
            while (j < len(TP)) and (TP[j] > TP[j - 1]) and (TP[j] < TP[i] + lag):
                j += 1
            if j == len(TP):
                break
            if TP[j] < TP[i] + lag:
                ComposedLineage.append([])
            else:
                composed_lineage = Lineage[i]
                for k in range(i + 1, j):
                    composed_lineage = composed_lineage.dot(Lineage[k])
                ComposedLineage.append(composed_lineage)
        else:
            ComposedLineage.append([])
    return ComposedLineage


def coupling_sampler(Lineage, nf=1e-3, s=1, threads=1, nmin=10):
    from gslrandom import PyRNG, multinomial
    Pairs = [[] for _ in range(s)]
    for lineage in Lineage:
        if len(lineage) > 0:
            l = lineage / lineage.sum(0)
            l = l / l.sum()
            l = l.flatten()
            sd = np.exp(entropy(l))
            n = max(nmin, int(sd * nf)) * np.ones(s, dtype=np.uint32)
            # P = np.ones((s,len(l)),dtype=np.uint32)
            P = np.empty((s, len(l)), dtype=np.uint32)
            l_tile = np.tile(l, (s, 1))
            rngs = [PyRNG(np.random.randint(2 ** 16)) for _ in range(threads)]
            P = multinomial(rngs, n, l_tile, P)
            # P = np.random.multinomial(n, l, size=s)
            for i in range(s):
                pairs = np.nonzero(P[i].reshape(lineage.shape))
                Pairs[i].append(pairs)
            del P, l_tile
        else:
            for i in range(s):
                Pairs[i].append([])
    return Pairs


def get_expression_pairs(Pairs, Lineage, Xg, Xr, TP, lag, differences=True):
    Xgs = [[]]
    Xrs = []
    for i in range(len(Lineage)):
        if len(Lineage[i]) > 0:
            j = i + 1
            while (j < len(TP)) and (TP[j] > TP[j - 1]) and (TP[j] < TP[i] + lag):
                j += 1
            if j == len(TP):
                break
            if TP[j] < TP[i] + lag:
                xgp = []
                xr = []
            else:
                pairs = Pairs[i]
                if differences:
                    a = Xg[j][pairs[1]]
                    b = Xg[i][pairs[0]]
                    xgp = ne.evaluate("a-b")
                else:
                    xgp = Xg[j][pairs[1]]
                # interpolate
                delta_t = TP[j] - TP[i]
                x1 = Xr[i][pairs[0]]
                x2 = Xr[j][pairs[1]]
                xr = x1 * lag / delta_t + x2 * (1. - lag / delta_t)
        else:
            xgp = []
            xr = []
        Xgs.append(xgp)
        Xrs.append(xr)
    Xrs.append([])
    return Xgs, Xrs


def initialize_modules(Xg, N, threads=1, nn=150):
    XG = np.vstack(Xg)
    XG = XG[np.random.choice(range(XG.shape[0]), int(XG.shape[0] / 20), replace=False)]
    SC = SpectralClustering(n_clusters=N, n_neighbors=nn, affinity='nearest_neighbors', n_jobs=threads)
    labels = SC.fit_predict(XG.T)
    U = np.zeros((N, XG.shape[1]))
    for i, c in enumerate(set(labels)):
        U[i, np.where(labels == c)[0]] = 1. / (labels == c).sum() ** .5
    return U


def update_regulation(Lineage, Xg, Xr, TP, lag, Z=[], U=[], num_modules=50, lda_z1=100., lda_z2=100., lda_u=10.,
                      epochs=25, sample_fraction=0.01, inner_iters=1, threads=1, k=1, b=6, y0=.01, x0=0,
                      differences=True, frequent_fa=False, fa_update_itrs=10, epoch_block_size=100, savepath=None):
    # lineage from optimal transport
    # Xg is a list of observed gene expression matrices at each time point
    # Xr is a list of regulatory levels at each time point (lagged by 1 from Xg)
    model = SparseOptimization(threads)
    if len(U) == 0:
        model.U = np.random.random((num_modules, Xg[0].shape[1]))
        model.U = (model.U.T / np.linalg.norm(model.U, axis=1)).T
    else:
        model.U = U
    if len(Z) > 0:
        model.Z = Z
    if differences:
        model.fa = dum
        model.fa_grad = dumg
        model.k, model.b, model.y0, model.x0 = k, b, y0, x0
    else:
        model.set_fa(k, b, y0, x0)
    for epoch_block in range(0, epochs, epoch_block_size):
        nepochs = min(epoch_block_size, epochs - epoch_block)
        Pairs = coupling_sampler(Lineage, nf=sample_fraction, s=nepochs, threads=threads)
        for epoch in range(nepochs):
            Xgs, Xrs = get_expression_pairs(Pairs[epoch], Lineage, Xg, Xr, TP, lag, differences=differences)
            model.withCoupling = False
            model.Lineage, model.Xg, model.Xr = Lineage, Xgs, Xrs
            for innerItr in range(inner_iters):
                model.lda1, model.lda2 = lda_z1, lda_z2
                model.z_shape = (Xr[0].shape[1], num_modules)
                model.update_Z(maxItr=1, with_prints=False, fa_update_freq=10 ** 6, forceNorm=True)
                model.lda1, model.lda2 = lda_u, 0
                model.update_U(maxItr=1, with_prints=False, fa_update_freq=10 ** 6)
            if ((epoch + epoch_block) % 5 == 0) or ((epoch + epoch_block) == epochs - 1):
                if frequent_fa:
                    model.update_fa(fmin_itrs=fa_update_itrs)
                model.print_performance(model.U, epoch + epoch_block)
        if savepath != None:
            np.save('%s/Z.%d.npy' % (savepath, epoch + epoch_block), model.Z)
            np.save('%s/U.%d.npy' % (savepath, epoch + epoch_block), model.U)
            np.save('%s/kbyx.%d.npy' % (savepath, epoch + epoch_block), (model.k, model.b, model.y0, model.x0))
    model.Xg, model.Xr = Xg, Xr
    return model.Z, model.U, model.get_all_Xhat(model.U), model.k, model.b, model.y0, model.x0


def main(argsv):
    import argparse
    import wot.io
    import pandas as pd
    import os
    parser = argparse.ArgumentParser(
        description='Gene Regulatory Networks')

    parser.add_argument('--dir',
                        help='Directory of transport maps', required=True)
    parser.add_argument('--tf',
                        help='File with one gene id per line to assign transcription factors', required=True)
    parser.add_argument('--gene_filter',
                        help='File with one gene id per line to include')
    parser.add_argument('--matrix',
                        help='Gene expression file with cells on '
                             'rows and features on columns', required=True)
    parser.add_argument('--time_lag', help='Time lag', type=float, required=True)
    parser.add_argument('--nmodules', help='Number of gene expression modules', type=int, default=50)

    parser.add_argument('--U', help='Gene module initialization matrix')

    parser.add_argument('--epochs',
                        help='Number of epochs', type=int, default=10000)
    parser.add_argument('--percentile',
                        help='Threshold matrix values at specified percentile (99.5 recommended)', type=float)
    parser.add_argument('--expm1', help='Take exponential minus one of input matrix', action='store_true')

    parser.add_argument('--out',
                        help='Prefix for ouput file names')
    args = parser.parse_args(argsv)
    if args.out is None:
        args.out = wot.io.get_filename_and_extension(os.path.basename(args.matrix))[0] + '_grn'
    N = args.nmodules
    epochs = args.epochs
    TimeLag = args.time_lag
    transport_maps = wot.io.list_transport_maps(args.dir)
    if len(transport_maps) == 0:
        print('No transport maps found in ' + args.dir)
        exit(1)

    ds = wot.io.read_dataset(args.matrix)
    if scipy.sparse.isspmatrix(ds.x):
        ds.x = ds.x.toarray()
    if args.expm1:
        ds.x = np.expm1(ds.x)

    if args.percentile is not None:
        p = np.percentile(ds.x, args.percentile)
        ds.x[ds.x > p] = p

    tf_ids = pd.read_table(args.tf, index_col=0, header=None).index.values
    tf_column_indices = ds.col_meta.index.isin(tf_ids)
    ntf_sum = tf_column_indices.sum()
    if ntf_sum == 0:
        print('No transcription factors found')
        exit(1)
    print(str(ntf_sum) + ' transcription factors')

    non_tf_column_indices = ~tf_column_indices
    non_tf_sum = non_tf_column_indices.sum()
    if non_tf_sum == 0:
        print('No non-transcription factors found')
        exit(1)
    print(str(non_tf_sum) + ' non-transcription factors')

    time_to_tmap_ids = {}
    time_to_tmap = {}
    TP = []
    Lineage = []  # list of transport maps
    threads = os.cpu_count()

    differences = False

    Xg = []  # list of non-tf expression
    Xr = []  # list of tf expression

    for i in range(len(transport_maps)):
        tmap_dict = transport_maps[i]
        tmap = wot.io.read_dataset(tmap_dict['path'])
        if time_to_tmap_ids.get(tmap_dict['t1']) is None:
            time_to_tmap_ids[tmap_dict['t1']] = tmap.row_meta.index.values
        if time_to_tmap_ids.get(tmap_dict['t2']) is None:
            time_to_tmap_ids[tmap_dict['t2']] = tmap.col_meta.index.values

        if time_to_tmap.get(tmap_dict['t2']) is not None:
            raise ValueError('Duplicate time')
        time_to_tmap[tmap_dict['t2']] = tmap.x
        if i == 0:
            TP.append(tmap_dict['t1'])
        TP.append(tmap_dict['t2'])

    for i, tp in zip(range(1, len(TP)), TP[1:]):
        if TP[i] < TP[i - 1]:
            l = []
        else:
            l = time_to_tmap[tp]
        Lineage.append(l)

    for t in TP:
        # align transport map and matrix
        tmap_ids = time_to_tmap_ids[t]
        aligned_order = ds.row_meta.index.get_indexer_for(tmap_ids)
        if (aligned_order == -1).sum() > 0:
            raise ValueError('Missing ids')

        ds_t = wot.Dataset(ds.x[aligned_order], ds.row_meta.iloc[aligned_order], ds.col_meta)
        Xg.append(ds_t.x[:, non_tf_column_indices])
        Xr.append(ds_t.x[:, tf_column_indices])

    if args.U is None:
        # rows are modules, columns are genes
        U = initialize_modules(Xg, N, threads=threads)
        print('Initialized modules')

    else:
        U = wot.io.read_dataset(args.U).x
        # TODO ensure in same order as ds

    assert len(TP) - 1 == len(Lineage)
    Uinv = np.linalg.pinv(U)
    Z = []
    XU = []
    for xg, xr in zip(Xg, Xr):
        XU.append(xg.dot(Uinv))

    XU = np.vstack(XU)
    k, b, x0 = XU.max(0), 1.5, -0.2
    y0 = np.array([ki / 10 for ki in k])
    # for differences model:
    # lda_z1,lda_z2,lda_u = 0.1

    # add all pairs of TFs (optional)
    for i, xr in []:  # enumerate(Xr):
        combo_idx = list(combinations(range(xr.shape[1]), 2))
        xr_combo = np.prod(xr[:, combo_idx], axis=2) ** .5
        Xr[i] = np.hstack([xr, xr_combo])

    # optionally add constant to each day
    for i, x in enumerate(Xr):
        xconst = np.zeros((x.shape[0], len(TP)))
        xconst[:, i] = 1
        Xr[i] = np.hstack([x, xconst])

    # put all features on the same scale
    # (globally)
    Xr_avg = np.average(np.vstack(Xr), axis=0)
    Xr = [x / (Xr_avg + 0.001) for x in Xr]
    # (all TFs have mean 1 on every day)
    # Xr = [x/(np.average(x,axis=0) + 0.01) for x in Xr]

    ComposedLineage = compose_transports(Lineage, TP, TimeLag)
    print('ComposedLineage ' + str(len(ComposedLineage)))

    # for original model: lda_z1=1.5,lda_z2=0.25,lda_u=1.5
    # for sparse model: lda_z1=3,lda_z2=1.5,lda_u=0.25
    # currently using: lda_z1=2,lda_z2=0.5,lda_u=1.5
    Z, U, Xh, k, b, y0, x0 = update_regulation(ComposedLineage, Xg, Xr, TP, TimeLag, Z=Z, U=U, lda_z1=2, lda_z2=0.5,
                                               lda_u=1.5, epochs=epochs, sample_fraction=5e-6, threads=threads,
                                               inner_iters=1,
                                               k=k, b=b, y0=y0, x0=x0, differences=differences, frequent_fa=False,
                                               num_modules=N, epoch_block_size=500,
                                               savepath='LineageRegulators_Combined/intermediateResults')
    np.save(args.out + '_Z.npy', Z)
    np.save(args.out + '_kbyx.npy', (k, b, y0, x0))

    for i, tp in enumerate(TP):
        if len(Xh[i]) > 0:
            np.save(args.out + '_regulators_deltaX.day-%d.npy' % tp, Xh[i])