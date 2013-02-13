procedure fit_coords(file, prefix) 
string file="" {prompt="Input file"}
string prefix="fc_" {prompt="Prefix for files"}
string catalog="muench.txt" {prompt="Input catalog"}
int ptolerance=20 {prompt="ccxymatch pixel tolerance"}
int tolerance=1 {prompt="ccxymatch angular tolerance"}
string pixmapfile="" {prompt="master coordinates file for pixel mapping"}
bool interactive=yes
bool update=no
real xref,yref,lngref,latref,xmag,ymag

begin

    if (pixmapfile=="") {
        pixmapfile=file
    }

    wcsctran(catalog, prefix//"transformed.txt", file, inwcs="world", outwcs="logical",
                      columns="1 2 3", units="hours")
    if(interactive) {
        display(file, frame=1, zscale=no, ocolors='green', ztrans='log')
        tvmark(frame=1, coords=prefix//"transformed.txt", mark="circle", radii=20, lengths=3, color=205, label=yes, txsize=3)
        imexam(file, logfile=prefix//"imexam.log", frame=1, wcs="world", xformat="%h", yformat="%H", keeplog=yes,
                     display="display(image='$1', frame='1', zscale=no,ocolors='green',ztrans='log')")
        }

    imgets(file,'CRPIX1')
    xref = imgets.value
    imgets(file,'CRPIX2')
    yref = imgets.value
    imgets(file,'CRVAL1')
    lngref = real(imgets.value) / 15.
    imgets(file,'CRVAL2')
    latref = imgets.value
    imgets(file,'CD1_1')
    xmag = real(imgets.value) * 3600
    imgets(file,'CD2_2')
    ymag = real(imgets.value) * 3600

    printf("%s %s %f %s %f %f",xref,yref,lngref,latref,xmag,ymag)

    ccxymatch(prefix//"imexam.log", catalog, prefix//"match.txt", tolerance=tolerance, ptolerance=ptolerance,
                                    xrotation=0, yrotation=0,
            xin=xref, yin=yref, xmag=xmag, ymag=ymag, lngref=lngref, latref=latref, 
            matching='tolerance')
    ccmap(prefix//"match.txt", database=prefix//"match.db", images=file,
                               results=prefix//"ccmap.db", xcolumn=3,
                               ycolumn=4, lngcolumn=1, latcolumn=2, update=update,
                               interactive=interactive)
    wcsctran(prefix//"ccmap.db",prefix//"pixpixmap.txt",pixmapfile,inwcs="world",outwcs="logical",
              columns="3 4 1 2 5 6 7 8", units="hours")

end
