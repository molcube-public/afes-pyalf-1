#! /usr/bin/env python

def GetVolume(alf_info,fnmout,fnmsin,fnmpsf):
  """
  Reads box volume and number of waters from the given files

  This routine is called by the routine GetVolumes to aid in computing the
  discrete solvent charge change correction.

  Parameters
  ----------
  alf_info : dict
      Dictionary of variables alf needs to run
  fnmout : str
      The filename for the volume time series. The number of waters is
      written to this same file, suffixed by '_NH2O'
  fnmsin : list of str
      A list of the filenames of the spatial trajectories from which the
      volume is read
  fnmpsf : list of str
      The filename of the psf from which the number of waters is read
  """

  import sys
  import numpy as np

  import MDAnalysis as mda
  # See https://docs.python.org/2/tutorial/modules.html for instructions on submodules:
  # import MDAnalysis.analysis.distances
  # from MDAnalysis.analysis import contacts

  # See alse https://www.mdanalysis.org/docs/documentation_pages/coordinates/init.html

  if alf_info['engine'] in ['charmm','bladelib','pycharmm']:
    fmt="DCD"
  elif alf_info['engine'] in ['blade']:
    fmt="XTC"
  else:
    print("Error: unsupported engine type %s" % alf_info['engine'])
    quit()

  Volumes=np.zeros((0,1))

  for ixtc in range(len(fnmsin)):
    trajin=mda.Universe(fnmpsf,[fnmsin[ixtc]],topology_format="psf",format=fmt)

    lines=trajin.trajectory.n_frames
    Volume=np.zeros((lines,1))

    i=0
    for ts in trajin.trajectory:
      Volume[i]=ts.dimensions[0]*ts.dimensions[1]*ts.dimensions[2]
      if (ts.dimensions[3]!=90 or ts.dimensions[4]!=90 or ts.dimensions[5]!=90):
        # print("GetVolume.py rquires an orthorhombic box")
        cosabc=np.cos(ts.dimensions[3:6]*np.pi/180.)
        Volume[i]=Volume[i]*np.sqrt(1.-cosabc[0]**2-cosabc[1]**2-cosabc[2]**2+2.*cosabc[0]*cosabc[1]*cosabc[2])
      i+=1
    Volumes=np.concatenate((Volumes,Volume),axis=0)

  selection=trajin.select_atoms("resname TIP3 and name OH2")

  np.savetxt(fnmout,Volumes,fmt="%10.6f")
  np.savetxt(fnmout+"_NH2O",np.reshape(selection.n_atoms,(1,)),fmt="%d")
