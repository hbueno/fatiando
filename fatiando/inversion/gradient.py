# Copyright 2012 The Fatiando a Terra Development Team
#
# This file is part of Fatiando a Terra.
#
# Fatiando a Terra is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fatiando a Terra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Fatiando a Terra.  If not, see <http://www.gnu.org/licenses/>.
"""
Gradient solvers for generic inverse problems.

**Solvers**

* :func:`fatiando.inversion.gradient.newton`
* :func:`fatiando.inversion.gradient.lev_marq`

----

"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = 'Created 19-Jan-2012'


import numpy
from numpy import dot as dot_product
from numpy.linalg import solve as linsys_solver
import itertools

from fatiando import logger

log = logger.dummy()


def newton(dms, initial, regs=[], step=1, maxit=100, tol=10**(-5)):
    """
    Solve the non-linear inverse problem using Newton's method.

    The increment to the parameter vector :math:`\\bar{p}` is calculated by
    
    .. math::

        \\bar{\\Delta\\bar{p}} = -\\alpha\\bar{\\bar{H}}^{-1}\\bar{g}

    where :math:`\\alpha` is the step size, :math:`\\bar{\\bar{H}}` is the
    Hessian matrix and :math:`\\bar{g}` is the gradient vector.

    This function is a generator and should be used inside a loop.
    It yields one step of the algorithm per iteration.

    Example::

        Need example
    

    Parameters:

    * dms
        List of data modules. Data modules should be child-classes of the
        :class:`fatiando.inversion.datamodule.DataModule` class.
    * initial
        The initial estimate of the parameters
    * regs
        List of regularizers. Regularizers should be child-classes of the
        :class:`fatiando.inversion.regularizer.Regularizer` class.
    * step
        Step size.
    * maxit
        Maximum number of iterations
    * tol
        Relative tolerance for decreasing the goal function to before
        terminating

    Yields:

    * changeset
        A dictionary with the current solution.        
        ``{'estimate':p, 'misfits':misfits, 'goals':goals, 'dms':dms}``
        
        * ``p`` is the current parameter vector.
        * ``misfits`` list with data-misfit function values per iteration
        * ``goals`` list with goal function values per iteration
        * ``dms`` are the data modules at this iteration
    
    """
    if len(dms) == 0:
        raise ValueError, "Need at least 1 data module. None given"
    p = initial
    nparams = len(p)
    residuals = [d.data - d.get_predicted(p) for d in dms]
    misfit = sum(d.get_misfit(res) for d, res in itertools.izip(dms, residuals))
    goal = misfit + sum(r.value(p) for r in regs)
    misfits = [misfit]
    goals = [goal]
    for i in xrange(maxit):
        gradient = numpy.zeros_like(p)
        for d, res in itertools.izip(dms, residuals):
            gradient = d.sum_gradient(gradient, p, res)
        for r in regs:
            gradient = r.sum_gradient(gradient, p)
        hessian = numpy.zeros((nparams, nparams))
        for m in itertools.chain(dms, regs):
            hessian = m.sum_hessian(hessian, p)
        p += step*linsys_solver(hessian, -1*gradient)
        residuals = [d.data - d.get_predicted(p) for d in dms]
        misfit = sum(d.get_misfit(res) for d, res in itertools.izip(dms,
                     residuals))
        goal = misfit + sum(r.value(p) for r in regs)
        misfits.append(misfit)
        goals.append(goal)
        
        yield {'estimate':p, 'misfits':misfits, 'goals':goals, 'dms':dms}

        # Check if goal function decreases more than a threshold
        if abs((goals[-1] - goals[-2])/goals[-2]) <= tol:
            break
        
    
def _test():
    import doctest
    doctest.testmod()
    print "doctest finished"

if __name__ == '__main__':
    _test()