"""
genrel package for GR calculations
David Clark, Kai Smith
Case Western Reserve University
2014
"""

import numpy as np
import sympy as sp

#returns a rank 3 tensor that represents the symbols
#first index corresponds to the upper index
def christoffel_symbols(metric, metric_key):
    symbols = tensor(3)
    inverse = inverse_metric(metric)
    for alpha in range(4):
        for beta in range(4):
            for gamma in range(4):
                total = 0
                for delta in range(4):
                    total += inverse[alpha][delta] * (sp.diff(metric[delta][beta], metric_key[gamma])
                        + sp.diff(metric[delta][gamma], metric_key[beta])
                        - sp.diff(metric[beta][gamma], metric_key[delta]))
                symbols[alpha][beta][gamma] = sp.simplify(total/2)
    return symbols

#returns the rank 4 Reimann curvature tensor
#the first index corresponds to an upper index -- the rest are lower
def reimann_tensor(chris_sym, metric_key):
    reimann = tensor(4)
    for alpha in range(4):
        for beta in range(4):
            for gamma in range(4):
                for delta in range(4):
                    total = 0
                    total += sp.diff(chris_sym[alpha][beta][delta], metric_key[gamma])
                    total -= sp.diff(chris_sym[alpha][beta][gamma], metric_key[delta])
                    for epsilon in range(4):
                        total += chris_sym[alpha][gamma][epsilon]*chris_sym[epsilon][beta][delta]
                        total -= chris_sym[alpha][delta][epsilon]*chris_sym[epsilon][beta][gamma]
                    reimann[alpha][beta][gamma][delta] = sp.cancel(total)
    return reimann

#returns the rank 2 Ricci curvature tensor
#both indicies are lower
def ricci_tensor(reimann):
    ricci = tensor(2)
    for alpha in range(4):
        for beta in range(4):
            total = 0
            for gamma in range(4):
                total += reimann[gamma][alpha][gamma][beta]
            ricci[alpha][beta] = sp.cancel(total)
    return ricci

#returns the Ricci scalar, a sympy symbol
def ricci_scalar(ricci_t, metric):
    scalar = 0
    inverse = inverse_metric(metric)
    for alpha in range(4):
        for beta in range(4):
            scalar += inverse[alpha][beta] * ricci_t[alpha][beta]
    scalar = sp.cancel(scalar)
    return scalar

#returns the rank 2 Einstein tensor
#both indices are lower
#think about whether you need to call raise_one_index before equating with a stress-energy tensor
def einstein_tensor(ricci_t, ricci_s, metric):
    einstein = tensor(2)
    for alpha in range(4):
        for beta in range(4):
            einstein[alpha][beta] = sp.cancel(ricci_t[alpha][beta] - 0.5*metric[alpha][beta]*ricci_s)
    return einstein

#runs through all parts of the program to find the Einstein tensor given only the metric and its key
def einstein_tensor_from_scratch(metric, metric_key, showprogress = False):
    c_syms = christoffel_symbols(metric, metric_key)
    if showprogress: print("Christoffel Symbols calculated")
    reimann_t = reimann_tensor(c_syms, metric_key)
    if showprogress: print("Reimann Tensor calculated")
    ricci_t = ricci_tensor(reimann_t)
    if showprogress: print("Ricci Tensor calculated")
    ricci_s = ricci_scalar(ricci_t, metric)
    if showprogress: print("Ricci Scalar calculated")
    return einstein_tensor(ricci_t, ricci_s, metric)

#returns expressions which, when set equal to zero, give the Einstein equations
def einstein_equations(einstein_tensor, stress_energy_tensor):
    einstein_equations = []
    for alpha in range(4):
        for beta in range(4):
            eq = sp.simplify(einstein_tensor[alpha][beta] - 8*sp.pi*sp.Symbol('G')*stress_energy_tensor[alpha][beta])
            if eq != 0 and eq not in einstein_equations:
                einstein_equations.append(eq)
    return np.array(einstein_equations)

def conservation_equations(metric, metric_key, stress_energy_tensor):
    equations = []
    stress_energy_tensor = raise_one_index(stress_energy_tensor, metric)
    cs = christoffel_symbols(metric, metric_key)
    for u in range(4):
        eq = 0
        for v in range(4):
            eq += sp.diff(stress_energy_tensor[u][v], metric_key[v])
            for s in range(4):
                eq += stress_energy_tensor[s][v]*cs[u][s][v]
                eq += stress_energy_tensor[u][s]*cs[v][s][v]
        eq = sp.simplify(eq)
        if eq != 0 and eq not in equations:
            equations.append(eq)
    return np.array(equations)

#returns a 4 x 4 x ... x 4 array of sympy symbols which represent a tensor
def tensor(rank):
    shape = [4 for i in range(rank)]
    return np.empty(shape, dtype = type(sp.Symbol('')))

#returns a 4 x 4 x ... x 4 array of sympy symbols filled with zeros which represent a tensor
def zerotensor(rank):
    shape = [4 for i in range(rank)]
    return np.zeros(shape, dtype = type(sp.Symbol('')))

#returns the rank of the tensor, passed in as a numpy array
def rank(tensor):
    return len(tensor.shape)

#returns the inverse of metric
def inverse_metric(metric):
    return np.array(sp.Matrix(metric).inv())

#matrix-multiplies the inverse metric and the tensor
#represents raising one index on a rank 2 tensor
def raise_one_index(tensor, metric, index = 1):
    return np.tensordot(inverse_metric(metric), tensor, index)

#matrix-multiplies the  metric and the tensor
#represents lowering one index on a rank 2 tensor
def lower_one_index(tensor, metric, index = 1):
    return np.tensordot(metric, tensor, index)

def kronecker_delta(a, b):
    if a == b:
        return 1
    return 0

#prints a tensor (or a sympy scalar) in a readable form
def rprint(obj, position = []):
    if type(obj) != type(np.array([])):
        if obj != 0:
            sp.pprint(sp.simplify(obj))
    else:
        for n, entry in enumerate(obj):
            if type(entry) != type(np.array([])) and entry != 0:
                    print(str(position + [n]) + ": ")
                    sp.pprint(sp.simplify(entry))
            else:
                rprint(entry, position + [n])

#prints a tensor (or a sympy scalar) in LaTeX
def lprint(obj, position = []):
    if type(obj) != type(np.array([])):
        if obj != 0:
            print(sp.latex(sp.simplify(entry)))
    else:
        for n, entry in enumerate(obj):
            if type(entry) != type(np.array([])) and entry != 0:
                    print(str(position + [n]) + ": ")
                    print(sp.latex(sp.simplify(entry)))
            else:
                lprint(entry, position + [n])

#Prints a sympy expression or expressions in a Mathematica ready form
def mprint(obj, position = []):
    if type(obj) != type(np.array([])):
        if obj != 0:
            print(mathematicize(obj))
    else:
        for n, entry in enumerate(obj):
            if type(entry) != type(np.array([])) and entry != 0:
                    print(str(position + [n]) + ": ")
                    print(mathematicize(entry))
            else:
                mprint(entry, position + [n])

#Turns a single expression into Mathematica readable form
def mathematicize(exp):
    #NOTE: Program currently assumes that all functions are functions of time and all derivatives are with respect to time
    exp = str(exp)
    #Deals with exponentiation
    exp = exp.replace('**', '^')
    #Deals with derivatives
    while exp.find('Derivative') != -1:
        plevel = 1
        clevel = 0
        fname = ""
        start = exp.find('Derivative')
        i = start + 11
        while plevel > 0:
            if exp[i] == '(':
                plevel += 1
            elif exp[i] == ')':
                plevel -= 1
            elif exp[i] == ',':
                clevel += 1
            elif plevel == 1 and clevel == 0:
                fname += exp[i]
            i += 1
        end = i
        exp = exp[:start] + fname + '\''*clevel +'[t]' + exp[end:]
    #Deals with giving function calls square brackets
    exp = exp.replace('(t)', '[t]')
    return exp

if __name__ == "__main__":
    #Defines commonly used variable and functions
    t = sp.Symbol('t')
    r = sp.Symbol('r')
    theta = sp.Symbol('theta')
    phi = sp.Symbol('phi')
    x = sp.Symbol('x')
    y = sp.Symbol('y')
    z = sp.Symbol('z')
    k = sp.Symbol('k')
    pi = sp.pi
    #k = 0

    a = sp.Function('a')(t)
    b = sp.Function('b')(t)
    c = sp.Function('c')(t)

    a0 = sp.Symbol('a0')
    b0 = sp.Symbol('b0')
    c0 = sp.Symbol('c0')

    """
    f = sp.Function('f')(t)
    f0 = sp.Symbol('f_0')
    #f = sp.sqrt(t)
    #f0 = 0

    fa = sp.Function('f_1')(t)
    fb = sp.Function('f_2')(t)
    fc = sp.Function('f_3')(t)
    fa0 = sp.Symbol('f_10')
    fb0 = sp.Symbol('f_20')
    fc0 = sp.Symbol('f_30')

    p = sp.Function('p')(t)
    p0 = sp.Symbol('p_0')
    fa = p
    fb = p
    fc = p
    fa0 = p0
    fb0 = p0
    fc0 = p0

    ca = sp.Symbol('c_1')
    cb = sp.Symbol('c_2')
    cc = sp.Symbol('c_3')

    a = ca*f + fa
    b = cb*f + fb
    c = cc*f + fc
    a0 = ca*f0 + fa0
    b0 = cb*f0 + fb0
    c0 = cc*f0 + fc0

    """
    w = sp.Rational(1, 3)#sp.Symbol('w')
    rho = sp.Function('rho')(t)
    p = w*rho
    G = sp.Symbol('G')

    I0 = sp.Symbol('I0')
    omega0 = sp.Symbol('Omega0')
    rho0 = sp.Symbol('rho0')#I0*omega0/(8 * sp.pi * G)
    p0 = sp.Symbol('p0')#w*rho0


    #FRW metric
    frw_metric, frw_metric_key = np.diag([-1, a**2/(1-k*r**2), a**2*r**2,a**2*r**2*sp.sin(theta)**2]), [t, r, theta, phi]
    #Bianchi metric (currently flat, does not assume isotropy)
    bc_metric, bc_metric_key = np.diag([-1, a**2, b**2, c**2]), [t, x, y, z]
    #Generalized Schwartzchild metric
    A, B = sp.Function('A')(r), sp.Function('B')(r)
    sc_metric, sc_metric_ky = np.diag([B, A, r**2, r**2*sp.sin(theta)**2]), [t, r, theta, phi]

    frw_c_metric_key = [t, x, y, z]
    frw_c_metric = zerotensor(2)
    frw_c_metric[0][0] = -1
    for i in range(1, 4):
        for j in range(1, 4):
            frw_c_metric[i][j] = a**2*(kronecker_delta(i, j) + 
                k*((frw_c_metric_key[i]*frw_c_metric_key[j])/(1-k*(x**2+y**2+z**2))))
    #rprint(frw_c_metric)
    
    T = np.diag([-rho0*(a0*b0*c0/(a*b*c))**sp.Rational(4, 3) - (3.0*k)/((a*b*c)**sp.Rational(2, 3)*8*pi*G) , p0*a0**2*b0*c0/(a**2*b*c) - k/(a**2*8*pi*G), p0*a0*b0**2*c0/(a*b**2*c) - k/(b**2*8*pi*G), p0*a0*b0*c0**2/(a*b*c**2) - k/(c**2*8*pi*G)])
    #T = np.diag([-rho0*(a0/a)**4.0, (rho0*(a0/a)**4.0)/3.0, (rho0*(a0/a)**4.0)/3.0, (rho0*(a0/a)**4.0)/3.0])
    #T = np.diag([0, 0, 0, 0])
    einstein = raise_one_index(einstein_tensor_from_scratch(bc_metric, bc_metric_key, showprogress = True), bc_metric)
    #rprint(einstein)

    print('Bianchi Spacetime Einstein Equations:')

    ein_eq = einstein_equations(einstein, T)

    #rprint(einstein[1,1]*einstein[2,2]*einstein[3,3]/einstein[0,0]**3-(p0/rho0)**3)
    rprint(ein_eq)
    #print(sp.simplify(-1*ein_eq[3] + sum(ein_eq[:3])))
    print('Conservation Equation for Bianchi Spacetime:')
    rprint(conservation_equations(bc_metric, bc_metric_key, T))
    
    #einstein = raise_one_index(einstein_tensor_from_scratch(frw_c_metric, bc_metric_key), frw_c_metric, showprogress = True)
    #print('FRW Spacetime Einstein Equations:')
    #rprint(einstein_equations(einstein, np.diag([-rho, p, p, p])))
    #print('FRW Equation for Bianchi Spacetime:')
    #rprint(conservation_equations(frw_c_metric, frw_c_metric_key, np.diag([-rho, p, p, p])))
