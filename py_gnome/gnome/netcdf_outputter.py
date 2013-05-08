'''
NetCDF outputter - follows the interface defined by gnome.Outputter for a NetCDF output writer
'''
import copy
import os
from datetime import datetime
from collections import OrderedDict

import netCDF4 as nc
import numpy as np

import gnome
from gnome.outputter import Outputter
from gnome.utilities import serializable, time_utils

class NetCDFOutput(Outputter, serializable.Serializable):
    """
    A NetCDFOutput object is used to write the model's data to a NetCDF file.
    It inherits from Outputter class and implements the same interface.
    
    This class is meant to be used within the Model, to be added to list of outputters.
    
    >>> model = gnome.model.Model(...)
    >>> model.outputters += gnome.netcdf_outputter.NetCDFOutput(os.path.join(base_dir,'sample_model.nc'), all_data=True)
    
    'all_data' flag is used to either output all the data arrays defined in model.spills or only the standard data.
               
               
    .. note::
       cf_attributes and data_vars are static members. cf_attributes is a dict that contains the global attributes per CF convention
       data_vars is a dict used to define NetCDF variables. 
       There is also a list called 'standard_data'. Since the names of the netcdf variables are different from the names in the 
       SpillContainer data_arrays, this simply lists the names of data_arrays that are part of standard data. When writing 'all_data',
       these data arrays are skipped.
    
    """
    cf_attributes={'comment' : 'Particle output from the NOAA PyGnome model',
                   'source' : "PyGnome version x.x.x",
                   'references' : 'TBD',
                   'feature_type' : "particle_trajectory" ,
                   'institution' : "NOAA Emergency Response Division",
                   'conventions' : "CF-1.6",
                   }
    
    """ let's keep order the same as original NetCDF """
    data_vars = OrderedDict()
    var = OrderedDict()
    
    # longitude
    var['dtype'] = np.float32
    var['long_name'] = 'longitude of the particle'
    var['units'] = 'degrees_east'
    data_vars['longitude'] = copy.deepcopy(var)
    
    # latitude
    var['long_name'] = 'latitude of the particle'
    var['units'] = 'degrees_north'
    data_vars['latitude'] = copy.deepcopy(var)
    
    # latitude
    var['long_name'] = 'particle depth below sea surface'
    var['units'] = 'meters'
    var['axis'] = 'z positive down'
    data_vars['depth'] = copy.deepcopy(var)
    
    # mass
    var.clear()
    var['dtype'] = np.float32
    var['units'] = 'grams'
    data_vars['mass'] = copy.deepcopy(var)
    
    # age
    var.clear()
    var['dtype'] = np.int32
    var['long_name'] = 'from age at time of release'
    var['units'] = 'seconds'
    data_vars['age'] = copy.deepcopy(var)
    
    # flag
    var.clear()
    var['dtype'] = np.int8
    var['long_name'] = 'particle status flag'
    var['valid_range'] = [0, 5]
    var['flag_values'] = [1, 2, 3, 4],
    var['flag_meanings'] = 'on_land off_maps evaporated below_surface'
    data_vars['flag'] = copy.deepcopy(var)
    
    # status
    var['long_name'] = 'particle status flag'
    var['valid_range'] = [0, 10]
    var['flag_values'] = [2, 3, 7, 10],
    var['flag_meanings'] = '2:in_water 3:on_land 7:off_maps 10:evaporated'
    data_vars['status'] = copy.deepcopy(var)
    
    # id
    var.clear()
    var['dtype'] = np.int8
    var['long_name'] = 'particle ID'
    var['units'] = '1'
    data_vars['id'] = copy.deepcopy(var)

    del var   # only used during initialization - no need to keep around
    
    # This is data that has already been written in standard format
    standard_data = ['positions','current_time_stamp','status_codes','spill_num','age','mass','flag']
    
    # define state for serialization
    state = copy.deepcopy(serializable.Serializable.state)
    state.add_field([serializable.Field('netcdf_filename',isdatafile=True,create=True,update=True),
                     serializable.Field('all_data',create=True,update=True),
                     serializable.Field('format',create=True,update=True),
                     serializable.Field('compress',create=True,update=True)])
    
    def __init__(self, netcdf_filename, cache=None, all_data=False, format='NETCDF4', compress=True, id=None):
        """
        .. function:: __init__(netcdf_filename, cache=None, all_data=False, id=None)
        
        Constructor for Net_CDFOutput object.
        
        :param netcdf_filename: Required parameter. The filename in which to store the NetCDF data. 
        :type netcdf_filename: str. or unicode
        :param cache: A cache object. Default is None, but this is required before calling write_output. 
                      This will generally be set automatically by the model.
        :type cache: As defined in cache module (gnome.utilities.cache). Currently only ElementCache is defined/used.
        :param all_data: If true, write all data to NetCDF, otherwise write only standard data. Default is False.
        :type all_data: bool
        :param id: Unique Id identifying the newly created mover (a UUID as a string). 
                   This is used when loading an object from a persisted state. User should never have to set this.
        """
        self._check_netcdf_filename(netcdf_filename)
        self._netcdf_filename = netcdf_filename
        self.cache = cache
        self._uncertain = False
        self._u_netcdf_filename = None
        
        self._middle_of_run = False # flag to keep track of state of the object - is True after calling prepare_for_model_run
        
        self.all_data = all_data
        self.arr_types = None   # this is only updated in prepare_for_model_run if all_data is True
        self._format = format
        self._compress= compress
        
        self._gnome_id = gnome.GnomeId(id)
    
    @property
    def id(self):
        """
        Function returns the unique id to identify the object,
        """
        return self._gnome_id.id
    
    @property
    def middle_of_run(self):
        return self._middle_of_run
    
    @property
    def netcdf_filename(self):
        return self._netcdf_filename
    
    @netcdf_filename.setter
    def netcdf_filename(self, new_name):
        if self.middle_of_run:
            raise AttributeError("This attribute cannot be changed in the middle of a run")
        else:
            self._check_netcdf_filename(new_name)
            self._netcdf_filename = new_name
            
    @property
    def all_data(self):
        return self._all_data
    
    @all_data.setter
    def all_data(self, value):
        if self.middle_of_run:
            raise AttributeError("This attribute cannot be changed in the middle of a run")
        else:
            self._all_data = value
         
    @property
    def compress(self):
        return self._compress
    
    @compress.setter
    def compress(self, value):
        if self.middle_of_run:
            raise AttributeError("This attribute cannot be changed in the middle of a run")
        else:
            self._compress = value
            
    @property
    def format(self):
        return self._format
    
    @format.setter
    def format(self, value):
        if self.middle_of_run:
            raise AttributeError("This attribute cannot be changed in the middle of a run")
        else:
            self._format = value
            
    def _check_netcdf_filename(self, netcdf_filename):
        """ basic checks to make sure the netcdf_filename is valid """
        if os.path.isdir(netcdf_filename):
            raise ValueError("netcdf_filename must be a file not a directory.")
        
        if os.path.exists(netcdf_filename):
            raise ValueError("{0} file exists. Enter a filename that does not exist in which to save data.".format(netcdf_filename))
        
        if not os.path.exists( os.path.realpath(os.path.dirname(netcdf_filename))):
            raise ValueError("{0} does not appear to be a valid path".format(os.path.dirname(netcdf_filename)))
    
    def prepare_for_model_run(self, cache=None, model_start_time=None, num_time_steps=None, uncertain=False, spills=None, **kwargs):
        """ 
        .. function:: prepare_for_model_run(cache=None, model_start_time=None, num_time_steps=None, uncertain=False, spills=None, **kwargs)
        
        Write global attributes and define dimensions and variables for NetCDF file. This must be done in prepare_for_model_run
        because if model state changes, it is rewound and re-run from the beginning.
        
        This takes more than standard 'cache' argument. Some of these are required arguments - they contain 
        None for defaults because non-default argument cannot follow default argument. Since cache is already 2nd positional argument
        for Renderer object, the required non-default arguments must be defined following 'cache'.
        
        :param cache=None: Sets the cache object to be used for the data. If None, it will use the one already set up. 
        :type cache: As defined in cache module (gnome.utilities.cache). Currently only ElementCache is defined/used.
        :param model_start_time: (Required) start time of the model run. NetCDF time units calculated with respect to this time.
        :type model_start_time: datetime.datetime object
        :param num_time_steps: (Required) total number of time steps for the run. Currently this is known and fixed.
        :type num_time_steps: int
        :param uncertain: Default is False. Model automatically sets this based on whether uncertainty is on or off. If this is
                          True then a uncertain data is written to netcdf_filename + '_uncertain.nc'
        :type uncertain: bool
        :param spills: If 'all_data' flag is True, then model must provide the model.spills object so NetCDF variables can be
                       defined for the remaining data arrays. If spills is None, but all_data flag is True, a ValueError will be raised.
                       It does not make sense to write 'all_data' but not provide 'model.spills'. 
        :type spills: gnome.spill_container.SpillContainerPair object. 
        
        .. note:: 
        Does not take any other input arguments; however, to keep the interface the same for all outputters,
        define **kwargs incase future outputters require different arguments.
        """
        if cache is not None:
            self.cache = cache
        
        if model_start_time is None or num_time_steps is None:
            raise TypeError("model_start_time and num_time_steps cannot be NoneType")
        
        if self.all_data and spills is None:
            raise ValueError("'all_data' flag is True, however spills is None. Please provide valid model.spills so we know which additional data to write.")
        
        self._uncertain = uncertain
        
        if self._uncertain:
            name, ext = os.path.splitext(self.netcdf_filename)
            self._u_netcdf_filename = "{0}_uncertain{1}".format(name,ext)
            filenames = (self.netcdf_filename, self._u_netcdf_filename)
        else:
            filenames = (self.netcdf_filename,)
        
        for file_ in filenames:
            with nc.Dataset(file_, 'w', format=self._format) as rootgrp:
                """ Global variables """
                rootgrp.comment = self.cf_attributes['comment']
                rootgrp.creation_date = time_utils.round_time(datetime.now(),roundTo=1).isoformat().replace('T',' ')
                rootgrp.source = self.cf_attributes['source']
                rootgrp.references = self.cf_attributes['references']
                rootgrp.feature_type = self.cf_attributes['feature_type']
                rootgrp.institution = self.cf_attributes['institution']
                rootgrp.convention = self.cf_attributes['conventions']
                
                """ Dimensions """
                rootgrp.createDimension('time', num_time_steps)
                rootgrp.createDimension('data', 0)
                
                """ Variables """
                time_ = rootgrp.createVariable('time', np.double, ('time',), zlib=self._compress)
                time_.units = 'seconds since {0}'.format(model_start_time.isoformat().replace('T',' '))
                time_.long_name = 'time'
                time_.standard_name = 'time'
                time_.calendar = 'gregorian'
                time_.comment = 'unspecfied time zone'
                
                pc = rootgrp.createVariable('particle_count',np.int32, ('time',), zlib=self._compress)
                pc.units = '1'
                pc.long_name = "number of particles in a given timestep"
                pc.ragged_row_count = "particle count at nth timestep"
                
                for key,val in self.data_vars.iteritems():
                    var = rootgrp.createVariable(key, val.get('dtype'), ('data',), zlib=self._compress)  # don't pop since it maybe required twice
                    # iterate over remaining attributes
                    [setattr(var,key2,val2) for key2,val2 in val.iteritems() if key2 != 'dtype']
                    
                """ End standard data. Next create variables for remaining arrays if all_data is True """ 
                if self.all_data:
                    rootgrp.createDimension('world_point', 3)
                    self.arr_types = dict()
                    for spill in spills:
                        at = spill.array_types
                        [self.arr_types.update({key:atype}) for key,atype in at.iteritems() if key not in self.arr_types and key not in self.standard_data]
                    
                    # create variables
                    for key,val in self.arr_types.iteritems():
                        if len(val.shape) == 0:
                            rootgrp.createVariable(key, val.dtype,('data'), zlib=self._compress)
                        elif val.shape[0] == 3:
                            rootgrp.createVariable(key, val.dtype,('data','world_point'), zlib=self._compress)
                        else:
                            raise ValueError("{0} has an undefined dimension: {1}".format(key,val.shape))
                        
        
        self._middle_of_run = True
        
    
    def write_output(self, step_num):
        """ 
        write NetCDF output at the end of the step
        
        :param step_num: The model's current timestep for which data is being written. model.current_time_step
        :type step_num: int
        """
        if self.cache is None:
            raise ValueError("cache object is not defined. It is required prior to calling write_output")
        
        for sc in self.cache.load_timestep(step_num).items():
            if sc.uncertain and self._u_netcdf_filename is not None:
                file_ = self._u_netcdf_filename
            else:
                file_ = self.netcdf_filename
            
            time_stamp = sc['current_time_stamp'].item()
            
            with nc.Dataset(file_, 'a') as rootgrp:
                rootgrp.variables['time'][step_num] = nc.date2num( time_stamp, 
                                                                   rootgrp.variables['time'].units,
                                                                   rootgrp.variables['time'].calendar)
                pc = rootgrp.variables['particle_count']
                pc[step_num] = len(sc['status_codes'])
                
                """ write keys that don't map directly to sc variable names """
                ixs = step_num * pc[step_num]   # starting index for writing data in this timestep
                ixe = ixs + pc[step_num]        # ending index for writing data in this timestep
                rootgrp.variables['longitude'][ixs:ixe] = sc['positions'][:,0]
                rootgrp.variables['latitude'][ixs:ixe] = sc['positions'][:,1]
                rootgrp.variables['depth'][ixs:ixe] = sc['positions'][:,2]
                rootgrp.variables['status'][ixs:ixe] = sc['status_codes'][:]
                rootgrp.variables['id'][ixs:ixe] = sc['spill_num'][:]
                
                # write remaining data
                if self.all_data:
                    for key, val in self.arr_types.iteritems():
                        if len(val.shape) == 0:
                            rootgrp.variables[key][ixs:ixe] = sc[key]
                        else:
                            rootgrp.variables[key][ixs:ixe,:] = sc[key]
                    
                
        return {'step_num': step_num,
                'netcdf_filename': (self.netcdf_filename, self._u_netcdf_filename),
                'time_stamp': time_stamp}
            
    
    def rewind(self):
        """ 
        if rewound, delete both the files and expect prepare_for_model_run to be called since
        rewind means start from beginning. 
        """
        if os.path.exists(self.netcdf_filename):
            os.remove(self.netcdf_filename)
            
        if self._u_netcdf_filename is not None and os.path.exists(self._u_netcdf_filename):
            os.remove(self._u_netcdf_filename)
            
        self._middle_of_run = False