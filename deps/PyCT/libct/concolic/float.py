# Copyright: see copyright.txt

import logging
from libct.concolic import Concolic, MetaFinal
from libct.utils import ConcolicObject, unwrap

log = logging.getLogger("ct.con.float")

class ConcolicFloat(float, Concolic, metaclass=MetaFinal):
    def __new__(cls, value, expr=None, engine=None):
        assert type(value) is float
        obj = super().__new__(cls, value)
        Concolic.__init2__(obj, value, expr, engine)
        log.debug(f"ConFloat, value: {value}, expr: {obj.expr}")
        return obj

    def __ge__(self, other, /):
        try:
            if (value := super().__ge__(unwrap(other))) is NotImplemented: raise NotImplementedError
        except: value = unwrap(other).__le__(unwrap(self))
        if isinstance(other, Concolic):
            if hasattr(other, 'isBool'): other = other.__float2__()
            assert not (hasattr(other, 'super') and isinstance(other.super, range))
            assert not isinstance(other, str)
            # other cannot be of type "range" and "str" here, since Exception should be thrown at the statement: value = unwrap(other).__ge__(unwrap(self))
        else:
            if type(other) is bool: other = float(other)
            if type(other) is not int and type(other) is not float: return ConcolicObject(value) # discard the symbolic expression if it cannot match the concrete value
            other = ConcolicObject(other)
        expr = ['>=', self, other]
        return ConcolicObject(value, expr)

    def __truediv__(self, other): # <slot wrapper '__truediv__' of 'float' objects>
        log.debug("ConFloat, __truediv__ is called")
        value = super().__truediv__(unwrap(other))
        if isinstance(other, Concolic):
            if hasattr(other, '__float2__'): other = other.__float2__()
        else:
            try: other = float(other)
            except: other = 1.0
            other = self.__class__(other)
        expr = ['/', self, other]
        return ConcolicObject(value, expr)

    ################################################################
    # Other helper methods are implemented in the following section.
    ################################################################

    def __float2__(self):
        log.debug("ConFloat, __float2__ is called")
        return self

    def __int2__(self):
        log.debug("ConFloat, __int2__ is called")
        value = super().__int__()
        expr = ['+', ['to_int', self], ['ite', ['and', ['<', self, '0'], ['not', ['is_int', self]]], '1', '0']]
        # Please note that ['to_int', -2.5] evaluates to -3 in smtlib2, but int(-2.5) evaluates to -2 in Python!
        return ConcolicObject(value, expr)
