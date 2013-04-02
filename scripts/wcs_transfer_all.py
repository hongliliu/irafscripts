# gsaoi script no longer works, so just gonna transfer WCS solutions 
with open('allobjs.lis') as f:
    flist = [fn.strip() for fn in f.readlines()]

for fn in flist:
    iraf.gsaoi.wcs_transfer(fn+".fits","rg%s.fits" % fn)

# h2 is scaled funny
with open('h2obj.lis') as f:
    flist = [fn.strip() for fn in f.readlines()]

for fn in flist:
    iraf.gsaoi.wcs_transfer(fn+".fits","rgs%s.fits" % fn)
