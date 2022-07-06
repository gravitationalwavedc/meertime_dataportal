"""
There are lots of different names for the same plot and they get used randomly by the 
science team when nameing images. This dict helps store different names for plots so that
the web cache can use a single name.

It will have lots of repeat values for easy lookup.

Known images types as of 6/07/2022
'time'
'snr-single'
'snr.cumul'
'phase-freq'
'snr.single'
'toa-single'
'flux'
'phase.time'
'zap.dynspec'
'zap-dynspec'
'calib.dynspec'
'profile.pol'
'snr-cumul'
'freq'
'snrt'
'toa-bal'
'phase.freq'
'toa.single'
'band'
'phase-time'
'bandpass'
'profile.int'
'profile-pol'
'calib-dynspec'
'profile-int'
"""

PLOT_NAMES = {
    "flux": ["flux", "profile-int", "profile", "profile.int"],
    "freq": ["freq", "frequency", "phase-vs-freq", "phase-freq", "phase.freq"],
    "time": ["time", "phase-time", "phase-vs-time", "phase.time"],
    "snrt": ["snrt", "snr", "snr-single", "snr.single"],
    "zap": ["zap", "zap.dynspec", "zap-dynspec"]
}
