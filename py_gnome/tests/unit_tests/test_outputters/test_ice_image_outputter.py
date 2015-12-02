'''
tests for ice image outputter
'''
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

import time
from datetime import datetime, timedelta

import numpy as np
import pytest

from gnome.model import Model
# from gnome.basic_types import oil_status
from gnome.utilities import time_utils

from gnome.spill import SpatialRelease, Spill, point_line_release_spill
from gnome.movers import IceMover
from gnome.outputters import IceImageOutput


from ..conftest import testdata


curr_file = testdata['IceMover']['ice_curr_curv']
topology_file = testdata['IceMover']['ice_top_curv']


## fixme: should use a proper pytest fixutre r-- but a bit broken.
# #@pytest.fixture(scope='function')
# def model(sample_model, output_dir):
#     model = sample_model['model']
# #    rel_start_pos = sample_model['release_start_pos']
# #    rel_end_pos = sample_model['release_end_pos']

#     model.start_time = datetime(2015, 5, 14, 0)
#     model.cache_enabled = True
#     model.uncertain = True

# #    N = 10  # a line of ten points
# #    line_pos = np.zeros((N, 3), dtype=np.float64)
# #    line_pos[:, 0] = np.linspace(rel_start_pos[0], rel_end_pos[0], N)
# #    line_pos[:, 1] = np.linspace(rel_start_pos[1], rel_end_pos[1], N)

# #    start_pos = (-164.01696, 72.921024, 0)
# #    model.spills += point_line_release_spill(1,
# #                                             start_position=start_pos,
# #                                             release_time=model.start_time,
# #                                             end_position=start_pos)

#     # release = SpatialRelease(start_position=line_pos,
#     #                          release_time=model.start_time)

#     # model.spills += Spill(release)

#     model.movers += c_ice_mover

#     model.outputters += IceImageOutputer([c_ice_mover,])

#     return model

def make_model():

    start_time = datetime(2015, 5, 14, 0)
    model = Model(time_step=3600*24, # one day
                  start_time=start_time,
                  duration=timedelta(days=3),)
    model.cache_enabled = False
    model.uncertain = False

# #    N = 10  # a line of ten points
# #    line_pos = np.zeros((N, 3), dtype=np.float64)
# #    line_pos[:, 0] = np.linspace(rel_start_pos[0], rel_end_pos[0], N)
# #    line_pos[:, 1] = np.linspace(rel_start_pos[1], rel_end_pos[1], N)

# #    start_pos = (-164.01696, 72.921024, 0)
# #    model.spills += point_line_release_spill(1,
# #                                             start_position=start_pos,
# #                                             release_time=model.start_time,
# #                                             end_position=start_pos)

#     # release = SpatialRelease(start_position=line_pos,
#     #                          release_time=model.start_time)

#     # model.spills += Spill(release)
    c_ice_mover = IceMover(curr_file, topology_file)
    model.movers += c_ice_mover

    model.outputters += IceImageOutput(c_ice_mover)

    return model


def test_init():
    'simple initialization passes'
    c_ice_mover = IceMover(curr_file, topology_file)
    o = IceImageOutput(c_ice_mover)
    assert o.ice_mover is c_ice_mover


def test_ice_image_output():
    '''
    Test image outputter with a model 
    NOTE: could it be tested with just a mover, and not a full model?
      -- that gets tricky with the cache and timesteps...
    '''
    model = make_model()

    begin = time.time()
    for step in model:
        print '\n\ngot step at: ', time.time() - begin

        ice_output = step['IceImageOutput']
        # print ice_output['time_stamp']
        # print ice_output['concentration_image'][:50] # could be really big!
        # print ice_output['bounding_box']
        # print ice_output['projection']
        for key in ('time_stamp',
                    'thickness_image',
                    'concentration_image',
                    'bounding_box',
                    'projection'):
            assert key in ice_output

    ## not sure what to assert here -- at least it runs!

def test_ice_image_mid_run():
    '''
    Test image outputter with a model 
    NOTE: could it be tested with just a mover, and not a full model?
      -- that gets tricky with the cache and timesteps...
    '''
    start_time = datetime(2015, 5, 14, 0)
    model = Model(time_step=3600*24, # one day
                  start_time=start_time,
                  duration=timedelta(days=3),)
    model.cache_enabled = False
    model.uncertain = False
    c_ice_mover = IceMover(curr_file, topology_file)
    model.movers += c_ice_mover

    ## run the model a couple steps
    step = model.step()
    step = model.step()

    ## now add the outputter
    iio = IceImageOutput(c_ice_mover)
    model.outputters += iio

    ## and run some more:

    step = model.step()
    step = model.step()
    ## and check the output
    ice_output = step['IceImageOutput']
    # print ice_output['time_stamp']
    # print ice_output['concentration_image'][:50] # could be really big!
    # print ice_output['bounding_box']
    # print ice_output['projection']
    for key in ('time_stamp',
                'thickness_image',
                'concentration_image',
                'bounding_box',
                'projection'):
        assert key in ice_output

    ## not sure what to assert here -- at least it runs!


# def test_ice_image_output_1step():
#     '''
#     Test image outputter with a model 
#     NOTE: could it be tested with just a mover, and not a full model?
#       -- that gets tricky with the cache and timesteps...
#     '''
#     model = make_model()

#     begin = time.time()
#     step  = model.step()
#     print '\n\ngot step at: ', time.time() - begin

#     ice_output = step['IceImageOutput']
#     # print ice_output['time_stamp']
#     # print ice_output['concentration_image'][:50] # could be really big!
#     # print ice_output['bounding_box']
#     # print ice_output['projection']
#     for key in ('time_stamp',
#                 'thickness_image',
#                 'concentration_image',
#                 'bounding_box',
#                 'projection'):
#         assert key in ice_output
#     assert False

# def test_ice_image_output_1step():
#     '''
#     Test image outputter with a model 

#     This only runs the first step

#     NOTE: could it be tested with just a mover, and not a full model?
#       -- that gets tricky with the cache and timesteps...
#     '''
#     model = make_model()
#     begin = time.time()


#     model.rewind()
#     step = model.step()
#     print '\n\ngot step at: ', time.time() - begin

#     ice_output = step['IceImageOutput']
#     # print ice_output['time_stamp']
#     # print ice_output['concentration_image'][:50] # could be really big!
#     # print ice_output['bounding_box']
#     # print ice_output['projection']
#     for key in ('time_stamp',
#                 'thickness_image',
#                 'concentration_image',
#                 'bounding_box',
#                 'projection'):
#         assert key in ice_output


# def test_ice_image_output2():
#     '''
#     Test image outputter without a model 
#        -- not working -- need time step to real time adjustment somehow.
#     '''
#     iio = IceImageOutput(c_ice_mover)

#     ice_output = iio.write_output(step_num=0)
#     # print ice_output['time_stamp']
#     # print ice_output['concentration_image'][:50] # could be really big!
#     # print ice_output['bounding_box']
#     # print ice_output['projection']
#     for key in ('time_stamp',
#                 'thickness_image',
#                 'concentration_image',
#                 'bounding_box',
#                 'projection'):
#         assert key in ice_output






















