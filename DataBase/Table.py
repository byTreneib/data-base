# Base classes for different data fields and foreign key relations
from Exceptions import NullConstraintException


import datetime

from typing import Optional, Iterable, Union, Tuple, List, Dict


######### FIELDS #########

class _Field:
    def __init__(self, default=None, allow_null=True, unique=False):
        self.default = default  # TODO: only None if allow_null?
        self.allow_null = allow_null
        self.unique = unique


class _ForeignField(_Field):
    def __init__(self, other: type, default=Optional[Union[_Field, Iterable[_Field]]], allow_null=True):
        super().__init__(default, allow_null, True)
        self._other_cls = other
        self._source_cls = None

    def set_source(self, source: type):
        self._source_cls = source


class TextField(_Field):
    def __init__(self, default: Optional[str] = None, allow_null=True, unique=False):
        super().__init__(default, allow_null, unique)


class IntegerField(_Field):
    def __init__(self, default: Optional[int] = None, allow_null=True, unique=False):
        super().__init__(default, allow_null, unique)


class RealField(_Field):
    def __init__(self, default: Optional[float] = None, allow_null=True, unique=False):
        super().__init__(default, allow_null, unique)


class DateField(_Field):
    def __init__(self, default: Optional[datetime.date] = None, allow_null=True, unique=False):
        super().__init__(default, allow_null, unique)


class DateTimeField(_Field):
    def __init__(self, default: Optional[datetime.datetime] = None, allow_null=True, unique=False):
        super().__init__(default, allow_null, unique)


# TODO: Default value in _ForeignField classes?

class OneToOneField(_ForeignField):
    def __init__(self, other: type, default: Optional[_Field] = None, allow_null=True):
        super().__init__(other, default, allow_null)

        if not self.allow_null and self.default is None:
            raise NullConstraintException(f"Default value cannot be {default} if allow_null={allow_null}.")


class OneToManyField(_ForeignField):
    def __init__(self, other: type, default: Optional[Union[_Field, Iterable[_Field]]] = None, allow_null=True):
        super().__init__(other, default, allow_null)

        if not self.allow_null and self.default is None:
            raise NullConstraintException(f"Default value cannot be {default} if allow_null={allow_null}.")


class ManyToOneField(_ForeignField):
    def __init__(self, other: type, default: Optional[Union[_Field, Iterable[_Field]]] = None, allow_null=True):
        super().__init__(other, default, allow_null)

        if not self.allow_null and self.default is None:
            raise NullConstraintException(f"Default value cannot be {default} if allow_null={allow_null}.")


class ManyToManyField(_ForeignField):
    def __init__(self, other: type, default: Optional[Union[_Field, Iterable[_Field]]] = None, allow_null=True):
        super().__init__(other, default, allow_null)

        if not self.allow_null and self.default is None:
            raise NullConstraintException(f"Default value cannot be {default} if allow_null={allow_null}.")


class _FieldValue:
    def __init__(self, field: _Field, value=None, use_default=False):
        self._field = field
        self.value = value if not use_default else self._field.default

        if self.value is None and not self._field.allow_null:
            raise NullConstraintException(f"Cannot set field {self._field.__class__.__name__} to {self.value} "
                                          f"if allow_null={self._field.allow_null}.")


class ForeignFieldValue:
    def __init__(self, field: _ForeignField, value=None,
                 use_default=False):
        self._field = field
        self.value = value if not use_default else self._field.default

        if self.value is None and not self._field.allow_null:
            raise NullConstraintException(f"Cannot set field {self._field.__class__.__name__} to {self.value} "
                                          f"if allow_null={self._field.allow_null}.")

    def _get_other(self):
        # return self._field.
        pass


########## TABLE ###########

class _TableMeta(type):
    def __new__(mcs, name, bases, attrs, **kwargs):
        base_attrs = {}
        for base in bases:
            base_attrs = {**base_attrs, **base._fields}

        new_attrs = {
            "_fields": {key: value for key, value in {**base_attrs, **attrs}.items() if isinstance(value, _Field)},
        }

        for key, value in attrs.items():
            if not isinstance(value, _Field) and key not in new_attrs.keys():
                new_attrs[key] = value

        newCls = type.__new__(mcs, name, bases, new_attrs, **kwargs)

        for field in new_attrs["_fields"].values():
            if isinstance(field, _ForeignField):
                field.set_source(newCls)

        return newCls


class Table(metaclass=_TableMeta):
    _id = IntegerField(unique=True)

    _fields: Dict[str, _Field] = {}
    _registered_to = None
    _count = 0

    def __init__(self, *args, **kwargs):
        self.__class__._count += 1

        if len(args) != 0:
            raise AttributeError(f"Got unexpected parameter {args[0]}.")

        for field_name, field in self.fields().items():
            if field_name in kwargs.keys():
                if isinstance(field, _ForeignField):
                    setattr(self, field_name, ForeignFieldValue(field, kwargs[field_name]))
                else:
                    setattr(self, field_name, _FieldValue(field, kwargs[field_name]))

                kwargs.pop(field_name)
            else:
                if isinstance(field, _ForeignField):
                    setattr(self, field_name, ForeignFieldValue(field, use_default=True))
                else:
                    setattr(self, field_name, _FieldValue(field, use_default=True))

        if len(kwargs) != 0:
            raise AttributeError(f"Cannot set value for {kwargs.keys()[0]}: Field does not exist.")

    def fields(self):
        return self.__class__._fields

    def field_names(self):
        return self.__class__._fields.keys()

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)

        if isinstance(value, _FieldValue):
            return value.value



        return value


if __name__ == '__main__':
    pass
