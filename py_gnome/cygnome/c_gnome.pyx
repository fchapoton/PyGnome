import cython
import random
import math

from libcpp.vector cimport vector
from cython.operator import preincrement as preinc

cimport numpy as np
import numpy as np

include "c_gnome_defs.pxi"

cpdef extern Model_c *model

cpdef set_model_start_time(Seconds uh):
    model.SetStartTime(uh)
    
cpdef set_model_duration(Seconds uh):
    model.SetDuration(uh)
    
cpdef set_model_time(Seconds uh):
    model.SetModelTime(uh)
    
cpdef set_model_timestep(Seconds uh):
    model.SetTimeStep(uh)

cpdef step_model():
    cdef Seconds t, s
    t = model.GetModelTime()
    s = model.GetTimeStep()
    model.SetModelTime(t + s)
    
#====================================================================#
# cdef class shio_time_value:
#     
#     cdef ShioTimeValue_c *time_value
#     
#     def __cinit__(self):
#         self.time_value = new ShioTimeValue_c()
#         
#     def __dealloc__(self):
#         del self.time_value
#         
#     def __init__(self):
#        pass
#     
#     def read_time_values(self, path, format, units):
#         self.time_value.ReadTimeValues(path, format, units)
#====================================================================#

cdef class cats_mover:

    cdef CATSMover_c *mover
    
    def __cinit__(self):
        self.mover = new CATSMover_c()
    
    def __dealloc__(self):
        del self.mover
    
    def __init__(self, scale_type, scale_value=1, diffusion_coefficient=1, shio_file=None):
        cdef ShioTimeValue_c *shio
        cdef WorldPoint p
        self.mover.scaleType = scale_type
        self.mover.scaleValue = scale_value
        self.mover.fEddyDiffusion = diffusion_coefficient
        ## should not have to do this manually.
        ## make-shifting for now.
        self.mover.fOptimize.isOptimizedForStep = 0
        self.mover.fOptimize.isFirstStep = 1  
        shio = new ShioTimeValue_c()
        shio.ReadTimeValues(shio_file)
        self.mover.SetTimeDep(shio)
        self.mover.SetRefPosition(shio.GetRefWorldPoint(), 0)
        self.mover.bTimeFileActive = True

    def read_topology(self, path):
        cdef Map_c **naught
        self.mover.ReadTopology(path, naught)
        
    def get_move(self, int t, np.ndarray[LERec, ndim=1] LEs):
        cdef int i    
        cdef WorldPoint3D wp3d
        cdef np.ndarray[LERec] ra = np.copy(LEs)
        cdef float dpLat, dpLong
        ra['p']['p_long']*=10**6
        ra['p']['p_lat']*=10**6
        for i in xrange(0, len(ra)):
            if ra[i].statusCode != status_in_water:
                continue
            wp3d = self.mover.GetMove(t, 0, 0, &ra[i], 0)
            dpLat = wp3d.p.pLat
            dpLong = wp3d.p.pLong
            LEs[i].p.pLat += (dpLat/1000000)
            LEs[i].p.pLong += (dpLong/1000000)
        self.mover.fOptimize.isOptimizedForStep = 1
        self.mover.fOptimize.isFirstStep = 0
    
    def compute_velocity_scale(self):
        self.mover.ComputeVelocityScale()

        
cdef class random_mover:

    cdef Random_c *mover

    def __cinit__(self):
        self.mover = new Random_c()
        
    def __dealloc__(self):
        del self.mover
        
    def __init__(self, diffusion_coefficient):
        self.mover.bUseDepthDependent = 0                
        self.mover.fOptimize.isOptimizedForStep = 0
        self.mover.fOptimize.isFirstStep = 1           
        self.mover.fUncertaintyFactor = 2
        self.mover.fDiffusionCoefficient = diffusion_coefficient

    def get_move(self, int t, np.ndarray[LERec, ndim=1] LEs):
        cdef int i    
        cdef WorldPoint3D wp3d
        cdef np.ndarray[LERec] ra = np.copy(LEs)
        cdef float dpLat, dpLong
        ra['p']['p_long']*=10**6
        ra['p']['p_lat']*=10**6
        for i in xrange(0, len(ra)):
            if ra[i].statusCode != status_in_water:
                continue
            wp3d = self.mover.GetMove(t, 0, 0, &ra[i], 0)
            dpLat = wp3d.p.pLat
            dpLong = wp3d.p.pLong
            LEs[i].p.pLat += (dpLat/1000000)
            LEs[i].p.pLong += (dpLong/1000000)

cdef class wind_mover:

    cdef WindMover_c *mover

    def __cinit__(self):
        self.mover = new WindMover_c()
        
    def __dealloc__(self):
        del self.mover
    
    def __init__(self, constant_wind_value):
        """
        initialize a constant wind mover
        
        constant_wind_value is a tuple of values: (u, v)
        """
        self.mover.fUncertainStartTime = 0
        self.mover.fDuration = 3*3600                                
        self.mover.fSpeedScale = 2
        self.mover.fAngleScale = .4
        self.mover.fMaxSpeed = 30 #mps
        self.mover.fMaxAngle = 60 #degrees
        self.mover.fSigma2 = 0
        self.mover.fSigmaTheta = 0 
        self.mover.bUncertaintyPointOpen = 0
        self.mover.bSubsurfaceActive = 0
        self.mover.fGamma = 1
        self.mover.fIsConstantWind = 1
        self.mover.fConstantValue.u = constant_wind_value[0]
        self.mover.fConstantValue.v = constant_wind_value[1]

    def get_move(self, t, np.ndarray[LERec, ndim=1] LEs):
        cdef int i
        cdef WorldPoint3D wp3d
        cdef float dpLat, dpLong
        cdef np.ndarray[LERec] ra = np.copy(LEs)
        ra['p']['p_long']*=10**6
        ra['p']['p_lat']*=10**6
        for i in xrange(0, len(ra)):
            if ra[i].statusCode != status_in_water:
                continue
            wp3d = self.mover.GetMove(t, 0, 0, &ra[i], 0)
            dpLat = wp3d.p.pLat
            dpLong = wp3d.p.pLong
            LEs[i].p.pLat += (dpLat/1000000)
            LEs[i].p.pLong += (dpLong/1000000)
