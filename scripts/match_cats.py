import numpy as np
try:
    from scipy.spatial import cKDTree as KDT
except ImportError:
    from scipy.spatial import KDTree as KDT


def xymatch(x1, y1, x2, y2, tol=None, nnearest=1):
    """
    Finds matches in one catalog to another.

    Parameters
    x1 : array-like
        X-coordinates of first catalog
    y1 : array-like
        Y-coordinates of first catalog
    x2 : array-like
        X-coordinates of second catalog
    y2 : array-like
        Y-coordinates of second catalog
    tol : float or None, optional
        How close a match has to be to count as a match.  If None,
        all nearest neighbors for the first catalog will be returned.
    nnearest : int, optional
        The nth neighbor to find.  E.g., 1 for the nearest nearby, 2 for the
        second nearest neighbor, etc.  Particularly useful if you want to get
        the nearest *non-self* neighbor of a catalog.  To do this, use:
        ``spherematch(x, y, x, y, nnearest=2)``

    Returns
    -------
    idx1 : int array
        Indecies into the first catalog of the matches. Will never be
        larger than `x1`/`y1`.
    idx2 : int array
        Indecies into the second catalog of the matches. Will never be
        larger than `x1`/`y1`.
    ds : float array
        Distance between the matches

    """

    x1 = np.array(x1, copy=False)
    y1 = np.array(y1, copy=False)
    x2 = np.array(x2, copy=False)
    y2 = np.array(y2, copy=False)

    if x1.shape != y1.shape:
        raise ValueError('x1 and y1 do not match!')
    if x2.shape != y2.shape:
        raise ValueError('x2 and y2 do not match!')

    # this is equivalent to, but faster than just doing np.array([x1, y1])
    coords1 = np.empty((x1.size, 2))
    coords1[:, 0] = x1
    coords1[:, 1] = y1

    # this is equivalent to, but faster than just doing np.array([x2, y2])
    coords2 = np.empty((x2.size, 2))
    coords2[:, 0] = x2
    coords2[:, 1] = y2

    kdt = KDT(coords2)
    if nnearest == 1:
        ds,idxs2 = kdt.query(coords1)
    elif nnearest > 1:
        retval = kdt.query(coords1, nnearest)
        ds = retval[0]
        idxs2 = retval[1][:, -1]
    else:
        raise ValueError('invalid nnearest ' + str(nnearest))

    idxs1 = np.arange(x1.size)

    if tol is not None:
        msk = ds < tol
        idxs1 = idxs1[msk]
        idxs2 = idxs2[msk]
        ds = ds[msk]

    return idxs1, idxs2, ds


def match_cats(cat1, cat2, tol=5, colscat1=[0,1], colscat2=[0,1], savetxt=None,
        extracolcat=None, extracolcatcols=[0,1], verbose=True):
    """
    Extracolcat is indexed as cat2
    """
    x1,y1 = np.loadtxt(cat1,usecols=colscat1).T
    x2,y2 = np.loadtxt(cat2,usecols=colscat2).T
    inds1,inds2,dist = xymatch(x1,y1,x2,y2,tol)

    if extracolcat is not None:
        x3,y3 = np.loadtxt(extracolcat,usecols=extracolcatcols,dtype=str).T

        if verbose:
            print "Size of catalogs. 1: %i  2: %i  extra: %i" % (len(x1),len(x2),len(x3))
    
    if savetxt is not None:
        with open(savetxt,'w') as f:
            for i1,i2 in zip(inds1,inds2):
                outstuff = ["%15.3f" % x for x in (x1[i1],y1[i1],x2[i2],y2[i2])]
                if extracolcat is not None:
                    outstuff = outstuff + ["%15s" % x for x in(x3[i2],y3[i2])]
                print >>f," ".join(outstuff)

    if verbose:
        print "Found %i matches with tolerance %i" % (len(inds1), tol)

    return inds1,inds2,dist


