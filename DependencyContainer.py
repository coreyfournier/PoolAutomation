from lib.GloBrite import GloBrite 
from Pumps.Pump import Pump

light:GloBrite = None
#List of pumps description is the first item in the tuple, pump is the second.
pumps:"list[tuple(str,Pump)]" = None