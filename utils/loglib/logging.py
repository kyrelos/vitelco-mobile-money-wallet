import json
import datetime
import decimal
from django.utils.timezone import is_aware


def _serializer(obj):
    """
    Render particular types in an appropriate way for logging. Allow
    the json module to handle the rest as usual.
    """
    # Datetime-like objects
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        message = ('Object of type {0} with value of {1} is not JSON '
                   'serializable').format(type(obj), repr(obj))
        raise TypeError(message)


class KeyValueRenderer(object):
    """
    Render event_dict as a list of Key=json.dumps(str(Value)) pairs.

    This is a drop-in replacement for the structlog
    KeyValueRenderer. The primary motivation for using it is to avoid
    logging Python object representations for things like datetimes
    and unicode strings. json.dumps ensures that strings are
    double-quoted, with embedded quotes conveniently escaped.
    """

    def __call__(self, logger, name, event_dict):
        serialize = lambda v: json.dumps(v, default=_serializer)

        return ', '.join('{0}={1}'.format(k, serialize(v))
                         for k, v in event_dict.items())


class INSerializer(json.JSONEncoder):
    """
    Adapted from django.core.serializers.json.DjangoJSONEncoder
    Allows serialising IN results by returning a string of any non-json-serializable objects
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            r = obj.isoformat()
            if obj.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            if is_aware(obj):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = obj.isoformat()
            if obj.microsecond:
                r = r[:12]
            return r
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, bytes):
            return list(obj)
        else:
            return str(obj)
