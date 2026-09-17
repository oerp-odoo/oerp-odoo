import dataclasses
import enum
import operator


class ValueType(enum.StrEnum):
    RAW = 'raw'
    EXPRESSION = 'expression'


@dataclasses.dataclass(frozen=True, kw_only=True)
class Value:
    val: any
    val_type: ValueType = ValueType.RAW

    def evaluate(self, obj=None):
        if self.val_type == ValueType.EXPRESSION:
            if obj is None:
                raise ValueError("Expression expects obj to be passed!")
            f = operator.attrgetter(self.val)
            return f(obj)
        return self.val
