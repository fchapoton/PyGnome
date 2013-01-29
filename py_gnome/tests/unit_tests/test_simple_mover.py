#!/usr/bin/env python

"""
test code for the simple_mover class

designed to be run with py.test
"""

##fixme: add test for some LEs being not-released, off_map, etc...

import numpy as np

from gnome.spill_container import TestSpillContainer

from gnome.movers import simple_mover

from gnome.utilities.projections import FlatEarthProjection as proj

def test_basic_move():
    sp = TestSpillContainer(num_elements=5) #initilizes to long, lat, z = 0.0, 0.0, 0.0
        
    mover = simple_mover.SimpleMover(velocity=(1.0, 10.0, 0.0) )

    delta = mover.get_move(sp, time_step=100.0, model_time=None)

    expected = np.zeros_like(delta)
    expected = proj.meters_to_lonlat((100.0, 1000.0, 0.0), (0.0, 0.0, 0.0))
    assert np.alltrue(delta == expected)
    
def test_north():
    sp = TestSpillContainer(num_elements=10,
                            start_pos=(20, 0.0, 0.0),
                            )
        
    mover = simple_mover.SimpleMover(velocity=(0.0, 10, 0.0) )

    delta = mover.get_move(sp, time_step = 100.0, model_time=None)
    
    expected = np.zeros_like(delta)
    expected = proj.meters_to_lonlat((0.0, 1000.0, 0.0), (0.0, 0.0, 0.0))
    assert np.alltrue(delta == expected)
    
def test_uncertainty():
    sp = TestSpillContainer(num_elements=1000,
                            start_pos=(0.0, 0.0, 0.0),
                            )

    u_sp = TestSpillContainer(num_elements=1000,
                              start_pos=(0.0, 0.0, 0.0),
                              uncertain=True)

    mover = simple_mover.SimpleMover(velocity=(10.0, 10.0, 0.0) )

    delta = mover.get_move(sp, time_step = 100, model_time=None)
    u_delta = mover.get_move(u_sp, time_step = 100, model_time=None)

    expected = np.zeros_like(delta)
    expected = proj.meters_to_lonlat((1000.0, 1000.0, 0.0), (0.0, 0.0, 0.0))

    assert np.alltrue(delta == expected)

    #but uncertain spills should be different:
    assert not np.alltrue(u_delta == expected)

    # the mean should be close:
    # this is teh smallest tolerance that consitantly passed -- good enough?
    assert np.allclose( np.mean(delta, 0), np.mean(u_delta, 0), rtol=1.7e-2)

    
