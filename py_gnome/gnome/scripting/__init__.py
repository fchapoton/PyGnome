
"""
Scripting package for GNOME with assorted utilities that make it easier to
write scripts.

The ultimate goal is to be able to run py_gnome for the "common" use cases
with only functionality available in this module

Classes and helper functions are imported from various py_gnome modules
(spill, environment, movers etc).

we recommend that this module be used like so::

  import gnome.scripting as gs

Then you will have easy access to most of the stuff you need to write
py_gnome scripts with, e.g.::

    model = gs.Model(start_time="2018-04-12T12:30",
                     duration=gs.days(2),
                     time_step=gs.minutes(15))

    model.map = gs.MapFromBNA('coast.bna', refloat_halflife=0.0)

    model.spills += gs.point_line_release_spill(num_elements=1000,
                                                start_position=(-163.75,
                                                                69.75,
                                                                0.0),
                                                release_time="2018-04-12T12:30")
"""

from gnome.model import Model

from gnome.basic_types import oil_status_map

from .utilities import (make_images_dir,
                        remove_netcdf,
                        set_verbose,
                        PrintFinder,
                        )

from gnome.utilities.time_utils import asdatetime

from .time_utils import (seconds,
                         minutes,
                         hours,
                         days,
                         weeks,
                         now,
                         )
from gnome.utilities.inf_datetime import MinusInfTime, InfTime

from gnome.spill.spill import Spill                         
from gnome.spill.release import PointLineRelease, PolygonRelease

from gnome.spill.spill import (surface_point_line_spill,
                               subsurface_plume_spill,
                               grid_spill,
                               spatial_release_spill,
                               )

from gnome.spill.substance import NonWeatheringSubstance
from gnome.spill.gnome_oil import GnomeOil

from gnome.environment.wind import Wind, constant_wind
from gnome.movers.wind_movers import (constant_wind_mover,
                                      wind_mover_from_file,
                                      )

from gnome.outputters import (Renderer,
                              NetCDFOutput,
                              KMZOutput,
                              OilBudgetOutput,
                              ShapeOutput,
                              WeatheringOutput,
                              )

from gnome.maps.map import MapFromBNA, GnomeMap

from gnome.environment import (FileGridCurrent,
                               GridCurrent,
                               GridWind,
                               IceAwareCurrent,
                               IceAwareWind,
                               Tide,
                               Water,
                               Waves,
                               )

from gnome.movers import (RandomMover,
                          RandomMover3D,
                          WindMover,
                          CatsMover,
                          ComponentMover,
                          RiseVelocityMover,
                          PyWindMover,
                          PyCurrentMover,
                          IceAwareRandomMover,
                          SimpleMover,
                          )

from gnome.utilities.remote_data import get_datafile


def load_model(filename):
    """
    load a model from an existing savefile

    :param filename: filename (path) of the save file to load.

    :returns: A configured Model object.

    :note: This is simply a handy wrapper around the Model.load_savefile
           classmethod
    """
    return Model.load_savefile(filename)

