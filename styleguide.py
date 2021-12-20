"""Plotting styleguide."""
import matplotlib.pyplot as plt
from datetime import datetime

# Set figures to size recommended by Publish0x for 
# online and mobile viewing:
def set_rcparams():
    plt.rcParams.update(
        {"font.size": 14, 
         "figure.figsize": (10,6),
        "lines.linewidth": 3,
        })

# add user markings and URL's:
def add_markings(ax):
    plt.text(
        1.0,
        0.0,
        """publish0x.com/@simplyrangel
github.com/simplyrangel""",
        transform=ax.transAxes,
        fontsize=10,
        ha="right",
        va="bottom",
        color="gray",
        alpha=0.5,
        )

# class to make saving figures easy:
class imghelper():
    def __init__(
        self,
        save_dir,
        img_series,
        save_flag=True,
        dpi=100,
        ):
        self.img_id = 0
        self.save_dir = save_dir
        self.img_series = img_series
        self.save_flag = save_flag
        self.dpi = dpi
    
    def savefig(self):
        img_name = "%s/%s-%d.png"%(
            self.save_dir,
            self.img_series,
            self.img_id,
            )
        if self.save_flag:
            plt.savefig(img_name,dpi=self.dpi)
            self.img_id += 1
