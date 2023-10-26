# MIT License
#
# Copyright (c) 2023 Niall McCarroll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import xarray as xr
import numpy as np
import argparse

import tempfile

from htmlfive.html5_builder import Html5Builder

from netcdf2html.fragments.utils import anti_aliasing_style
from netcdf2html.fragments.image import save_image, save_image_falsecolour, InlineImageFragment
from netcdf2html.fragments.table import TableFragment

class Convert:

    def __init__(self, folder, output_path, main_variable, red_variable, green_variable, blue_variable, vmin, vmax):
        self.folder = folder
        self.output_path = output_path
        self.main_variable = main_variable
        self.red_variable = red_variable
        self.green_variable = green_variable
        self.blue_variable = blue_variable
        self.vmin = vmin
        self.vmax = vmax

    def run(self):
        builder = Html5Builder(language="en")

        builder.head().add_element("title").add_text("NetCDF to HTML")
        builder.head().add_element("style").add_text(anti_aliasing_style)

        table = TableFragment()
        table.add_row(["Acquired", self.main_variable + "(%.0f-%.0f K)" % (self.vmin, self.vmax),
                       "RGB=(%s,%s,%s)" % (self.red_variable, self.green_variable, self.blue_variable)])
        files = []
        for filename in os.listdir(self.folder):
            if filename.endswith(".nc"):
                ds = xr.open_dataset(os.path.join(self.folder, filename))
                timestamp = str(ds["time"].data[0])[:10]
                files.append((timestamp, filename))
        files = sorted(files, key=lambda item: item[0])

        for (timestamp, filename) in files:
            ds = xr.open_dataset(os.path.join(self.folder, filename))
            cells = [timestamp]
            if self.main_variable:
                da = ds[self.main_variable]
                count_nans = np.count_nonzero(np.isnan(da.data))
                if count_nans / (da.shape[1] * da.shape[2]) > 0.1:
                    continue
                with tempfile.NamedTemporaryFile(suffix=".png") as p:
                    save_image(da.data[0, :, :], self.vmin, self.vmax, p.name)
                    cells.append(InlineImageFragment(p.name, alt_text=filename, w=500))
            if self.red_variable and self.green_variable and self.blue_variable:
                red = ds[self.red_variable].data[0, :, :]
                green = ds[self.green_variable].data[0, :, :]
                blue = ds[self.blue_variable].data[0, :, :]
                with tempfile.NamedTemporaryFile(suffix=".png") as p:
                    save_image_falsecolour(red, green, blue, p.name)
                    cells.append(InlineImageFragment(p.name, alt_text=filename, w=500))
            table.add_row(cells)

        builder.body().add_fragment(table)
        with open(self.output_path, "w") as f:
            f.write(builder.get_html())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_folder", help="folder containing netcdf4 files to visualise")
    parser.add_argument("output_path", help="path to write html output")
    parser.add_argument("--data-variable", default=None, help="the data variable, organised by (time,y,x)")
    parser.add_argument("--data-min", type=float, default=None, help="min value for data variable scale")
    parser.add_argument("--data-max", type=float, default=None, help="max value for data variable scale")
    parser.add_argument("--red-variable", default=None,
                        help="the red variable for plotting false colour, organised by (time,y,x)")
    parser.add_argument("--green-variable", default=None,
                        help="the green variable for plotting false colour, organised by (time,y,x)")
    parser.add_argument("--blue-variable", default=None,
                        help="the blue variable for plotting false colour, organised by (time,y,x)")

    args = parser.parse_args()

    if args.data_variable is not None:
        if args.data_min is None or args.data_max is None:
            print("Error - please specify --data-min and --data-max if providing --data-variable")

    c = Convert(args.input_folder, args.output_path, args.data_variable, args.red_variable, args.green_variable,
                args.blue_variable, args.data_min, args.data_max)
    c.run()

if __name__ == '__main__':
    main()