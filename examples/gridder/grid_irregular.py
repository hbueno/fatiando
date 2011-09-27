"""
Example of manipulating irregular grids.
"""
from matplotlib import pyplot
import numpy
from fatiando import stats, gridder, logger, vis

log = logger.get()
log.info(logger.header())
log.info("Example of generating and plotting irregular grids")

log.info("Calculating...")
x, y = gridder.scatter(-2, 2, -2, 2, n=200)
z = stats.gaussian2d(x, y)

log.info("Plotting...")
shape = (100,100)
pyplot.axis('scaled')
pyplot.title("Irregular grid")
pyplot.plot(x, y, '.k', label='Grid points')
levels = vis.contourf(x, y, z, shape, 12, interpolate=True)
vis.contour(x, y, z, shape, levels, interpolate=True)
pyplot.legend(loc='lower right')
pyplot.show()