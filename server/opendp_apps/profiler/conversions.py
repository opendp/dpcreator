# map to convert from new to old format

def none_to_null(x):
    return 'NULL' if x is None else x


conversions = dict(
    description=('',),
    variableName=('varnamesSumStat',),
    mode=('mode', lambda x: str(x[0]) if x else ''),
    invalidCount=('invalid',),
    validCount=('valid',),
    stdDev=('sd',),
    uniqueCount=('uniques',),
    herfindahlIndex=('herfindahl',),
    modeFreq=('freqmode',),
    fewestValues=('fewest', lambda x: str(x[0]) if x else ''),
    midpoint=('mid', str),
    fewestFreq=('freqfewest', str),
    midpointFreq=('freqmid', str),
    binary=('binary', lambda x: 'yes' if x else 'no'),
    geographic=('',),
    locationUnit=('',),
    temporal=('',),
    timeUnit=('',),
    pdfPlotType=('plottype', none_to_null),
    pdfPlotX=('plotx',),
    pdfPlotY=('ploty',),
    cdfPlotType=('',),
    cdfPlotX=('',),
    cdfPlotY=('',),
    plotValues=('plotvalues',),
)