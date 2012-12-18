from gnome import basic_types, weather
from datetime import datetime
import numpy as np
import pytest
from hazpy import unit_conversion

def test_exceptions(invalid_rq):
    """
    Test ValueError exception thrown if improper input arguments
    Test TypeError thrown if units are not given - so they are None
    """
    with pytest.raises(ValueError):
        weather.Wind()
        wind_vel = np.zeros((1,), basic_types.velocity_rec)
        weather.Wind(timeseries=wind_vel, data_format=basic_types.data_format.wind_uv, units='meters per second')
        
    # following also raises ValueError. This gives invalid (r,theta) inputs which are rejected
    # by the transforms.r_theta_to_uv_wind method. It tests the inner exception is correct
    with pytest.raises(ValueError):
        invalid_dtv_rq = np.zeros((len(invalid_rq['rq']),), dtype=basic_types.datetime_value_2d)
        invalid_dtv_rq['value'] = invalid_rq['rq']
        weather.Wind(timeseries=invalid_dtv_rq, data_format=basic_types.data_format.magnitude_direction, units='meters per second')
        
    # exception raised if datetime values are not in ascending order or not unique
    with pytest.raises(ValueError):
        # not unique datetime values
        dtv_rq = np.zeros((4,), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_rq.value = (1,0)
        weather.Wind(timeseries=dtv_rq, units='meters per second')
        
        # not in ascending order
        dtv_rq.time[:len(dtv_rq)-1] = [datetime(2012,11,06,20,10+i,30) for i in range(len(dtv_rq)-1)]
        weather.Wind(timeseries=dtv_rq, units='meters per second')
        
    # exception raised since no units given for timeseries during init or set_timeseries
    with pytest.raises(TypeError):
        dtv_rq = np.zeros((4,), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_rq.time = [datetime(2012,11,06,20,10+i,30) for i in range(4)]
        dtv_rq.value = (1,0)
        weather.Wind(timeseries=dtv_rq)
        
    with pytest.raises(TypeError):
        dtv_rq = np.zeros((4,), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_rq.time = [datetime(2012,11,06,20,10+i,30) for i in range(4)]
        dtv_rq.value = (1,0)
        wind = weather.Wind(timeseries=dtv_rq,units='meters per second')
        wind.set_timeseries(dtv_rq)
        
    # invalid units
    with pytest.raises(unit_conversion.InvalidUnitError):
        dtv_rq = np.zeros((4,), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_rq.time = [datetime(2012,11,06,20,10+i,30) for i in range(4)]
        dtv_rq.value = (1,0)
        wind = weather.Wind(timeseries=dtv_rq,units='met per second')
        wind.set_timeseries(dtv_rq)
    
        
def test_read_file_init():
    """
    initialize from a long wind file
    """
    file = r"SampleData/WindDataFromGnome.WND"
    wm = weather.Wind(file=file)
    print
    print "----------------------------------"
    print "Units: " + str(wm.user_units)
    assert True

@pytest.fixture(scope="module",params=['wind_circ','rq_rand'])
def wind(wind_circ,rq_rand,request):
    """
    Create Wind object using the time series given by the test fixture
    'wind_circ', 'rq_rand'. 
    
    NOTE:
    Since 'rq_rand' randomly generates (r,theta), the corresponing (u,v) are calculated 
    from gnome.utilities.transforms.r_theta_to_uv_wind(...). Assumes this method works correctly.
    """
    if request.param == 'wind_circ':
        dtv_rq = np.zeros((len(wind_circ['rq']),), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_rq.time = [datetime(2012,11,06,20,10+i,30) for i in range(len(dtv_rq))]
        dtv_rq.value = wind_circ['rq']
        dtv_uv = np.zeros((len(dtv_rq),), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_uv.value= wind_circ['uv'] 
    elif request.param == 'rq_rand':
        from gnome.utilities import transforms

        dtv_rq = np.zeros((len(rq_rand['rq']),), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_rq.time = [datetime(2012,11,06,20,10+i,30) for i in range(len(dtv_rq))]
        dtv_rq.value = rq_rand['rq']
        dtv_uv = np.zeros((len(dtv_rq),), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
        dtv_uv.value = transforms.r_theta_to_uv_wind( rq_rand['rq'])

    dtv_uv.time = dtv_rq.time

    wm  = weather.Wind(timeseries=dtv_rq,data_format=basic_types.data_format.magnitude_direction,units='meters per second')
    return {'wm':wm, 'rq': dtv_rq, 'uv': dtv_uv}


# tolerance for np.allclose(..) function. Results are almost the same but not quite so needed to add tolerance.
# The precision per numpy.spacing(1)=2.2e-16
atol = 1e-14
rtol = 0


def test_init(wind_circ):
    """
    figure out how to pass the parameter to above fixture
    """
    dtv_rq = np.zeros((len(wind_circ['rq']),), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
    dtv_rq.time = [datetime(2012,11,06,20,10+i,30) for i in range(len(dtv_rq))]
    dtv_rq.value = wind_circ['rq']
    dtv_uv = np.zeros((len(dtv_rq),), dtype=basic_types.datetime_value_2d).view(dtype=np.recarray)
    dtv_uv.time = dtv_rq.time
    dtv_uv.value= wind_circ['uv']
    wm  = weather.Wind(timeseries=dtv_rq,data_format=basic_types.data_format.magnitude_direction,units='knots')
    
    # output is in knots
    gtime_val = wm.get_timeseries(data_format=basic_types.data_format.wind_uv).view(dtype=np.recarray)
    assert np.all( gtime_val.time == dtv_uv.time)
    assert np.allclose(gtime_val.value, dtv_uv.value, atol, rtol)
    
    # output is in meters per second
    gtime_val = wm.get_timeseries(data_format=basic_types.data_format.wind_uv, units='meters per second').view(dtype=np.recarray)
    expected = unit_conversion.convert('Velocity',wm.user_units,'meters per second',dtv_uv.value)
    assert np.all(gtime_val.time == dtv_uv.time)
    assert np.allclose(gtime_val.value, expected, atol, rtol)
    
    

class TestWind:
   """
   Gather all tests that apply to a WindObject in this class. All methods use
   the 'wind' fixture
   
   Couldn't figure out how to use "wind" fixture at class level. Tried decorating
   the class with the following: 
   @pytest.mark.usefixtures("wind")
   
   """
   def test_init_units(self, wind):
      """
      check default wind object is created
      
      Also check that init doesn't fail if timeseries given in (u,v) format
      """
      weather.Wind(timeseries=wind['uv'],data_format=basic_types.data_format.wind_uv, units='meters per second')
      assert True

   def test_str_repr_no_errors(self, wind):
       """
       simply tests that we get no errors during repr() and str()
       """
       repr(wind['wm'])
       print str(wind['wm'])
       assert True

   def test_id_matches_builtin_id(self, wind):
       assert id(wind['wm']) == wind['wm'].id
   
   def test_get_timeseries(self, wind):
       """
       Initialize from timeseries and test the get_time_value method 
       """
       # check get_time_value()
       gtime_val = wind['wm'].get_timeseries(data_format=basic_types.data_format.magnitude_direction)
       assert np.all(gtime_val['time'] == wind['rq'].time)
       assert np.allclose(gtime_val['value'], wind['rq'].value, atol, rtol)
       
       
   def test_get_timeseries_uv(self, wind):
       """
       Initialize from timeseries and test the get_time_value method 
       """
       gtime_val = wind['wm'].get_timeseries(data_format=basic_types.data_format.wind_uv).view(dtype=np.recarray)
       assert np.all(gtime_val.time == wind['uv'].time)
       assert np.allclose(gtime_val.value, wind['uv'].value, atol, rtol)
       
   def test_get_timeseries_by_time(self, wind):
       """
       get time series, but this time provide it with the datetime values for which you want timeseries
       """
       gtime_val = wind['wm'].get_timeseries(data_format=basic_types.data_format.magnitude_direction, datetime=wind['rq'].time).view(dtype=np.recarray)
       assert np.all(gtime_val.time == wind['rq'].time)
       assert np.allclose(gtime_val.value, wind['rq'].value, atol, rtol)
       
   def test_get_timeseries_by_time_scalar(self, wind):
      """
      get single time value in the middle of the 0th and 1st index of the timeseries. 
      Read the value (wind velocity) for this time.
      
      Output should be an interpolated value between the values of the 0th and 1st index of timeseries.
      """
      dt = wind['rq'].time[0].astype(object) + (wind['rq'].time[1]-wind['rq'].time[0]).astype(object)/2
      get_rq = wind['wm'].get_timeseries(data_format=basic_types.data_format.magnitude_direction, datetime=dt).view(dtype=np.recarray)
      get_uv = wind['wm'].get_timeseries(data_format=basic_types.data_format.wind_uv, datetime=dt).view(dtype=np.recarray)
      print
      print "=================================================="
      print "(u,v):" 
      print  str( wind['uv'].value[:2,:])
      print
      print "get_uv: " + str(get_uv.value[0])
      print "time: " + repr(dt)
      print "-----------------"
      print "u-bounds: (" + str( min(wind['uv'].value[:2,0])) + ", " + str(max(wind['uv'].value[:2,0])) + "); computed-u: " + str( get_uv.value[0,0])
      print "v-bounds: (" + str( min(wind['uv'].value[:2,1])) + ", " + str(max(wind['uv'].value[:2,1])) + "); computed-v: " + str( get_uv.value[0,1])
      print "-----------------"
      print "(r,theta): " 
      print  str( wind['rq'].value[:2,:])
      print
      print "get_rq: " + str(get_rq.value[0])
      print "-----------------"
      print "FOR INFO ONLY: INTERPOLATION IS DONE IN (u,v) SPACE"
      print "r-bounds: (" + str( min(wind['rq'].value[:2,0])) + ", " + str(max(wind['rq'].value[:2,0])) + "); computed-r: " + str( get_rq.value[0,0])
      print "theta-bounds: (" + str( min(wind['rq'].value[:2,1])) + ", " + str(max(wind['rq'].value[:2,1])) + "); computed-theta: " + str( get_rq.value[0,1])
      print "-----------------"       
      print "NOTE: This test fails at times for randomly generated (r,theta)"
      print "      Still trying to understand how the hermite interpolation should work"
      
      assert get_uv.time[0].astype(object) == dt
      assert get_uv.value[0,0] > np.min( wind['uv'].value[:2,0]) \
         and get_uv.value[0,0] < np.max( wind['uv'].value[:2,0])
      assert get_uv.value[0,1] > np.min( wind['uv'].value[:2,1]) \
         and get_uv.value[0,1] < np.max( wind['uv'].value[:2,1])
      #FOLLOWING DOES NOT WORK
      #assert get_rq.value[0,0] > wind['rq'].value[0,0] and get_rq.value[0,0] < wind['rq'].value[1,0]
      #assert get_rq.value[0,1] > wind['rq'].value[1,0] and get_rq.value[0,1] < wind['rq'].value[1,1]

