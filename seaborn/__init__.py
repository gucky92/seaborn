# Capture the original matplotlib rcParams
import matplotlib as mpl
_orig_rc_params = mpl.rcParams.copy()

# Import seaborn objects
from .rcmod import *
from .utils import *
from .palettes import *
from .relational import *
from .regression import *
from .categorical import *
from .distributions import *
from .matrix import *
from .miscplot import *
from .axisgrid import *
from .widgets import *
from .colors import xkcd_rgb, crayons
from . import cm
from .scalebar import scalebar, panel_letter
from .figuregrid import FacetFigure

__version__ = "0.11.0.dev0"
