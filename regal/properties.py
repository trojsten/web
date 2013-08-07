# -*- coding: utf-8 -*-

from __future__ import unicode_literals

'''
Collection of clases which simplifies working with 'Props' models.
(There is at least one - regal.people.models.PersonProps)

Props model must contain attributes / fields:
    [*] object - owner of this property
    [*] type - must be also model
    [*] value

PropsType model must contain attributes / fields:
    [*] multi - boolean, whether this type of property can have multiple
        (distinct) values per one object
        If true, property is called multiproperty
        Otherwise it's singleproperty

'''

from collections import MutableMapping
from collections import MutableSet

from django.db import transaction
from django.db import models
from django.db.models.query import QuerySet


class SetOfMultiproperties(MutableSet):

    '''
    Helper class of PropsDict.

    Is returned by PropsDict, when multiproperty is required.
    Stores the changes to PropsDict's chnge sets.

    Implements set's behaviour
    '''

    def __init__(self, edited_types_set, del_prop_set, prop_class,
                 prop_type, prop_object):
        self._storage = dict()
        self._edited_types_set = edited_types_set
        self._del_prop_set = del_prop_set
        self._prop_class = prop_class
        self._prop_type = prop_type
        self._prop_object = prop_object

    def add(self, item):
        if not item in self._storage:
            self._storage[item] = self._prop_class(
                type=self._prop_type,
                object=self._prop_object,
                value=item)
            self._edited_types_set.add(self._prop_type)

    def discard(self, item):
        if item in self._storage:
            if self._storage[item].pk is not None:
                self._del_prop_set.add(self._storage[item])
            del self._storage[item]

    def __iter__(self):
        return self._storage.iterkeys()

    def __len__(self):
        return len(self._storage)

    def __contains__(self, item):
        return item in self._storage

    def _add_property_instance(self, prop):
        self._storage[prop.value] = prop
        self._edited_types_set.add(self._prop_type)

    def _save_created(self):
        for x in self._storage.itervalues():
            if x.pk is None:
                x.save()


class PropsDict(MutableMapping):

    '''
    Class used for offline properties edits.

    Fully encapsulates Props model interface - user is working just with
    PropType-s keys and values. Implements dict's behaviour.

    When multiproperty required a set is returned (SetOfMultiproperties).

    All changes can be commited to db in an atomic operation.
    Object is not updatable - to update changes from db create new object.

    '''

    def _del_property_instance(self, key):
        if key.pk in self._data_storage:
            if self._data_storage[key.pk].pk is not None:
                self._del_prop_set.add(self._data_storage[key.pk])

    def _add_multiproperty_set(self, key):
        if key.pk not in self._data_storage:
            self._data_storage[key.pk] = SetOfMultiproperties(
                edited_types_set=self._edited_types_set,
                del_prop_set=self._del_prop_set,
                prop_class=self._prop_class,
                prop_type=key,
                prop_object=self._prop_object)
            self._key_storage[key.pk] = key

    def _add_property_instance(self, prop):
        if prop.type.multi:
            self._add_multiproperty_set(prop.type)
            self._data_storage[prop.type.pk]._add_property_instance(prop)
        else:
            self._data_storage[prop.type.pk] = prop
            self._edited_types_set.add(prop.type)
            self._key_storage[prop.type.pk] = prop.type

    def __init__(self, prop_object, prop_query_set):
        self._data_storage = dict()
        self._key_storage = dict()
        self._edited_types_set = set()
        self._del_prop_set = set()
        self._prop_class = prop_query_set.model
        self._prop_object = prop_object
        qs = prop_query_set.select_related('type')
        for x in list(qs):
            self._add_property_instance(x)
        self._edited_types_set.clear()
        self._del_prop_set.clear()

    def __getitem__(self, key):
        if key.multi:
            self._add_multiproperty_set(key)
            return self._data_storage[key.pk]
        return self._data_storage[key.pk].value

    def __setitem__(self, key, value):
        if key.multi:
            raise MultipropertiEditError()
        self._del_property_instance(key)
        self._data_storage[key.pk] = self._prop_class(
            type=key,
            object=self._prop_object,
            value=value)
        self._edited_types_set.add(self._data_storage[key.pk].type)
        self._key_storage[key.pk] = key

    def __delitem__(self, key):
        if key.multi:
            raise MultipropertiEditError()
        self._del_property_instance(key)
        del self._key_storage[key.pk]
        del self._data_storage[key.pk]

    def __len__(self):
        return len(self._key_storage)

    def __iter__(self):
        return self._key_storage.itervalues()

    @transaction.commit_manually
    def save(self):
        '''
        Atomic operation. Commits all the changes since last save to db.
        '''

        try:
            delete_Q = models.Q()
            for x in self._del_prop_set:
                if x.type.multi:
                    delete_Q |= models.Q(pk=x.pk)
                else:
                    delete_Q |= models.Q(type__pk=x.type.pk)
            self._prop_class.objects.filter(delete_Q).delete()
            for x in self._edited_types_set:
                if x.multi:
                    self._data_storage[x.pk]._save_created()
                else:
                    self._data_storage[x.pk].save()
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()
            self._edited_types_set.clear()
            self._del_prop_set.clear()

    class MultipropertiEditError(KeyError):
        pass


class PropsQuerySet(QuerySet):

    '''
    Query set of properties owned by one object. Can create PropsDict.
    '''

    def __init__(self, prop_object=None, *args, **kwargs):
        super(PropsQuerySet, self).__init__(*args, **kwargs)
        self.prop_object = prop_object

    def _clone(self, *args, **kwargs):
        c = super(PropsQuerySet, self)._clone(*args, **kwargs)
        c.prop_object = self.prop_object
        return c

    def create_dict(self):
        return PropsDict(self.prop_object, self)


class PropQuerySet(PropsQuerySet):

    '''
    QuerySet of properties of one type owned by one object.
    Provides common functionality for Multi/SinglePopr subclasses.
    '''

    def __init__(self, prop_type=None, *args, **kwargs):
        super(PropQuerySet, self).__init__(*args, **kwargs)
        self.prop_type = prop_type

    def _clone(self, *args, **kwargs):
        c = super(PropQuerySet, self)._clone(*args, **kwargs)
        c.prop_type = self.prop_type
        return c

    def _add(self, value):
        self.model.objects.create(
            value=value,
            type=self.prop_type,
            object=self.prop_object)

    def _safe_query_set(self):
        return self.filter(object=self.prop_object, type=self.prop_type)


class MultiPropQuerySet(PropQuerySet):

    '''
    QuerySet of multiproperties of one type owned by one object.
    Provides interface for direct db editing.
    '''

    def add_value(self, value):
        '''
        Adds new property with given value to database
        '''
        self._add(value)

    def values(self):
        '''
        Returns set of values of properties in this QuerySet
        '''
        res = set()
        for i in list(self):
            res.add(i.value)
        return res

    def delete_value(self, value):
        '''
        Removes property with given value from database (if exists)
        '''
        self._safe_query_set().filter(value=value).delete()


class SinglePropQuerySet(PropQuerySet):

    '''
    QuerySet of multiproperties of one type owned by one object.
    Provides interface for direct db editing.
    '''

    def value(self):
        '''
        Abbrevitation for get().value
        '''
        return self.get().value

    @transaction.commit_manually
    def set_value(self, value):
        '''
        Removes all properties of this type and object from the db and
        creates a new one. (Should be just one of this type per object.)
        '''
        try:
            self._safe_query_set().delete()
            self._add(value)
        except:
            transaction.rollback()
            raise
        else:
            transaction.commit()


class PropsManager(models.Manager):

    '''
    Manager for all properties woned by one object.

    Normally returns PropsQuerySet-s but using dictionary index returns
    Single/MultiPropQuerySet-s.
    '''

    def __init__(self, owner, model):
        super(PropsManager, self).__init__()
        self.owner = owner
        self.model = model

    def get_query_set(self):
        qs = PropsQuerySet(
            prop_object=self.owner,
            model=self.model,
            using=self._db)
        return qs.filter(object=self.owner)

    def create_dict(self):
        '''
        For direct access.
        '''
        return self.get_query_set().create_dict()

    def __getitem__(self, key):
        '''
        Returns Single/MultiPropQuerySet, for direct db manipulation
        '''
        if key.multi:
            qs = MultiPropQuerySet(
                prop_type=key,
                prop_object=self.owner,
                model=self.model,
                using=self._db)
        else:
            qs = SinglePropQuerySet(
                prop_type=key,
                prop_object=self.owner,
                model=self.model,
                using=self._db)
        return qs.filter(object=self.owner, type=key)
