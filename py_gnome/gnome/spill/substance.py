import copy
import six

from colander import Float, SchemaNode, SequenceSchema, Boolean, Sequence, Tuple, null
import numpy as np
import warnings
from gnome.basic_types import fate, oil_status
from gnome.array_types import gat

from gnome.persist.base_schema import (ObjTypeSchema,
                                       ObjType,
                                       GeneralGnomeObjectSchema)
from gnome.gnomeobject import GnomeId
from gnome.persist.base_schema import OrderedCollectionType
from oil_library.oil_props import OilProps
from oil_library.factory import get_oil
from oil_library.models import Oil
from gnome.environment.water import Water, WaterSchema
from gnome.spill.initializers import (floating_initializers,
                                      InitWindagesSchema,
                                      DistributionBaseSchema)


class SubstanceSchema(ObjTypeSchema):
    initializers = SequenceSchema(
        GeneralGnomeObjectSchema(
            acceptable_schemas=[InitWindagesSchema,
                                DistributionBaseSchema
                                ]
        ),
        save=True, update=True, save_reference=True
    )
    is_weatherable = SchemaNode(Boolean(), read_only=True)

class GnomeOilType(ObjType):

    def _prepare_save(self, node, raw_object, saveloc, refs):
        #Gets the json for the object, as if this were being serialized
        obj_json = None
        if hasattr(raw_object, 'to_dict'):
            #Passing the 'save' in case a class wants to do some special stuff on
            #saving specifically.
            dict_ = raw_object.to_dict('save')

            #Skip the following because this has loads of properties not covered
            #in the schema
#             for k in dict_.keys():
#                 if dict_[k] is None:
#                     dict_[k] = null
            return dict_
        else:
            raise TypeError('Object does not have a to_dict function')
        #also adds the object to refs by id
        refs[raw_object.id] = raw_object

        #note you cannot immediately strip out attributes that wont get saved here
        #because they are still needed by _impl
        return obj_json

class GnomeOilSchema(SubstanceSchema):
    standard_density = SchemaNode(Float(), read_only=True)
    water = WaterSchema(save_reference=True, test_equal=False)

    def __init__(self, unknown='preserve', *args, **kwargs):
        super(SubstanceSchema, self).__init__(*args, **kwargs)
        self.typ = GnomeOilType(unknown)

    def _save(self, obj, zipfile_=None, refs=None):
        return SubstanceSchema._save(self, obj, zipfile_=zipfile_, refs=refs)

class NonWeatheringSubstanceSchema(SubstanceSchema):
    standard_density = SchemaNode(Float(), read_only=True)


class Substance(GnomeId):
    _schema = SubstanceSchema
    _ref_as = 'substance'

    def __init__(self,
                 initializers=None,
                 windage_range=(.01, .04),
                 windage_persist=900,
                 *args,
                 **kwargs):
        super(Substance, self).__init__(*args,**kwargs)
        if not initializers:
            initializers = floating_initializers(windage_range=windage_range,
                                                 windage_persist=windage_persist)
        self.initializers = initializers
        #add the types from initializers
        self._windage_init=None
        for i in self.initializers:
            self.array_types.update(i.array_types)
            if 'windages' in i.array_types:
                self._windage_init = i
        if windage_range != (.01, .04):
            self.windage_range = windage_range
        if windage_persist != 900:
            self.windage_persist = windage_persist

    @property
    def is_weatherable(self):
        if not hasattr(self, '_is_weatherable'):
            self._is_weatherable = True
        return self._is_weatherable

    @is_weatherable.setter
    def is_weatherable(self, val):
        self._is_weatherable = True if val else False
    '''
    Windage range/persist are important enough to receive properties on the
    Substance.
    '''
    @property
    def windage_range(self):
        if self._windage_init:
            return self._windage_init.windage_range
        else:
            raise ValueError('No windage initializer on this substance')

    @windage_range.setter
    def windage_range(self, val):
        if self._windage_init:
            if np.any(np.asarray(val) < 0) or np.asarray(val).size != 2:
                raise ValueError("'windage_range' >= (0, 0). "
                                 "Nominal values vary between 1% to 4%. "
                                 "Default windage_range=(0.01, 0.04)")
            self._windage_init.windage_range = val
        else:
            raise ValueError('No windage initializer on this substance')

    @property
    def windage_persist(self):
        if self._windage_init:
            return self._windage_init.windage_persist
        else:
            raise ValueError('No windage initializer on this substance')

    @windage_persist.setter
    def windage_persist(self, val):
        if self._windage_init:
            if val == 0:
                raise ValueError("'windage_persist' cannot be 0. "
                                 "For infinite windage, windage_persist=-1 "
                                 "otherwise windage_persist > 0.")
            self._windage_init.windage_persist = val
        else:
            raise ValueError('No windage initializer on this substance')

    def get_initializer_by_name(self, name):
        ''' get first initializer in list whose name matches 'name' '''
        init = [i for i in enumerate(self.initializers) if i.name == name]

        if len(init) == 0:
            return None
        else:
            return init[0]

    def has_initializer(self, name):
        '''
        Returns True if an initializer is present in the list which sets the
        data_array corresponding with 'name', otherwise returns False
        '''
        for i in self.initializers:
            if name in i.array_types:
                return True

        return False
    def initialize_LEs(self, to_rel, arrs):
        '''
        :param to_rel - number of new LEs to initialize
        :param arrs - dict-like of data arrays representing LEs
        '''
        for init in self.initializers:
            init.initialize(to_rel, arrs, self)

    def _attach_default_refs(self, ref_dict):
        for i in self.initializers:
            i._attach_default_refs(ref_dict)
        return GnomeId._attach_default_refs(self, ref_dict)


class GnomeOil(OilProps, Substance):
    _schema = GnomeOilSchema
    _req_refs = ['water']

    def __init__(self, name=None, water=None, **kwargs):
        if isinstance(name, six.string_types):
            if kwargs.get('adios_oil_id', False):
                #init the oilprops from dictionary
                oil_obj = get_oil(kwargs)
            else:
                #GnomeOil('oil_name_here')
                oil_obj = get_oil(name)
            OilProps.__init__(self, oil_obj)
            kwargs['name'] = name #this is important; it passes name up to GnomeId to be handled there!
        elif isinstance(name, Oil):
            oil_obj = name
            OilProps.__init__(self, oil_obj)
        else:
            raise ValueError('Must provide an oil name or OilLibrary.Oil to GnomeOil init')

        #because passing oilLibrary kwargs makes problem up the tree, only pass
        #up the kwargs specified in the schema
        keys = self._schema().get_nodes_by_attr('all')
        if 'windage_range' in kwargs:
            keys.append('windage_range')
        if 'windage_persist' in kwargs:
            keys.append('windage_persist')
        k2 = dict([(key, kwargs.get(key)) for key in keys])
        read_only_attrs = GnomeOil._schema().get_nodes_by_attr('read_only')
        for n in read_only_attrs:
            k2.pop(n, None)
        k2.pop('water')
        Substance.__init__(self, **k2)

        self.water = water

        #add the array types that this substance DIRECTLY initializes
        self.array_types.update({'density': gat('density'),
                                 'viscosity': gat('viscosity'),
                                 'mass_components': gat('mass_components')})
        self.array_types['mass_components'].shape = (self.num_components,)
        self.array_types['mass_components'].initial_value = (self.mass_fraction,)

    def __eq__(self, other):
        t1 = Substance.__eq__(self, other)
        try:
            t2 = self.tojson() == other.tojson()
        except Exception:
            return False
        return t1 and t2

    @classmethod
    def get_GnomeOil(self, oil_info, max_cuts=None):
        '''
        Use this instead of get_oil_props
        '''
        oil_ = get_oil(oil_info, max_cuts)
        return GnomeOil(oil_)


    def to_dict(self, json_=None):
        json_ = super(GnomeOil, self).to_dict(json_=json_)
        substance_json = self.tojson()

        #the old 'prune_substance' function from Spill
        del substance_json['imported_record_id']
        del substance_json['estimated_id']
        del substance_json['id']

        for attr in ('kvis', 'densities', 'cuts',
                     'molecular_weights',
                     'sara_densities', 'sara_fractions'):
            for item in substance_json[attr]:
                for sub_item in ('id', 'oil_id', 'imported_record_id'):
                    if sub_item in item:
                        del item[sub_item]

        json_.update(substance_json)
        return json_

#     @classmethod
#     def new_from_dict(cls, dict_):
#         substance = cls.get_GnomeOil(dict_)
#         return substance

    def initialize_LEs(self, to_rel, arrs):
        '''
        :param to_rel - number of new LEs to initialize
        :param arrs - dict-like of data arrays representing LEs
        '''
        sl = slice(-to_rel, None, 1)
        water = self.water
        if water is None:
            #LEs released at standard temperature and pressure
            self.logger.warning('No water provided for substance initialization, using default Water object')
            water = Water()

        water_temp = water.get('temperature', 'K')
        density = self.density_at_temp(water_temp)
        if density > water.get('density'):
            msg = ("{0} will sink at given water temperature: {1} {2}. "
                   "Set density to water density"
                   .format(self.name,
                           water.get('temperature',
                                          self.water.units['temperature']),
                           water.units['temperature']))
            self.logger.error(msg)

            arrs['density'][sl] = water.get('density')
        else:
            arrs['density'][sl] = density

        substance_kvis = self.kvis_at_temp(water_temp)
        if substance_kvis is not None:
            'make sure we do not add NaN values'
            arrs['viscosity'][sl] = substance_kvis
        super(GnomeOil, self).initialize_LEs(to_rel, arrs)


class NonWeatheringSubstance(Substance):
    _schema = NonWeatheringSubstanceSchema

    def __init__(self,
                 standard_density=1000.0,
                 **kwargs):
        '''
        Non-weathering substance class for use with ElementType.
        - Right now, we consider our substance to have default properties
          similar to water, which we can of course change by passing something
          in.

        :param standard_density=1000.0: The density of the substance, assumed
                                        to be measured at 15 C.
        :type standard_density: Floating point decimal value

        :param pour_point=273.15: The pour_point of the substance, assumed
                                  to be measured in degrees Kelvin.
        :type pour_point: Floating point decimal value
        '''
        super(NonWeatheringSubstance, self).__init__(**kwargs)
        self.standard_density = standard_density
        self.array_types.update({
            'density': gat('density'),
            'fate_status': gat('fate_status')})

    @property
    def is_weatherable(self):
        if not hasattr(self, '_is_weatherable'):
            self._is_weatherable = False
        return self._is_weatherable

    @is_weatherable.setter
    def is_weatherable(self, val):
        self.logger.warn('This substance {0} cannot be set to be weathering')

    def initialize_LEs(self, to_rel, arrs):
        '''
        :param to_rel - number of new LEs to initialize
        :param arrs - dict-like of data arrays representing LEs
        '''
        sl = slice(-to_rel, None, 1)
        arrs['density'][sl] = self.standard_density
        arrs['fate_status'][sl] = fate.non_weather
        super(NonWeatheringSubstance, self).initialize_LEs(to_rel, arrs)

    def density_at_temp(self, temp=273.15):
        '''
            For non-weathering substance, we just return the standard density.
        '''
        return self.standard_density