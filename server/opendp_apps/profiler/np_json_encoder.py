from datetime import date, datetime
import simplejson as json
import numpy as np


class NumpyJSONEncoder(json.JSONEncoder):
    """class to encode the data"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        else:
            return super(NumpyJSONEncoder, self).default(obj)


# Encoder function
def np_dumps(obj):
    return json.dumps(obj, cls=NumpyJSONEncoder)
