import json
import datetime
import cherrypy
import decimal

class JSONEncoder(json.JSONEncoder):
    """Allows cherry py to handle dates correctly

    Args:
        json (_type_): _description_
    """
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif(isinstance(obj,decimal.Decimal)):
            return float(obj)
        return super().default(obj)
    def iterencode(self, value):
        # Adapted from cherrypy/_cpcompat.py
        for chunk in super().iterencode(value):
            yield chunk.encode("utf-8")

jsonEncoderInstance = JSONEncoder()


def json_handler(*args, **kwargs):
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return jsonEncoderInstance.iterencode(value)