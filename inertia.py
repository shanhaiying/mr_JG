#######################################################################
#
# Copyright (C) 2011 Steve Butler, Jason Grout.
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#######################################################################


class InertiaSet(object):

    def __init__(self, generators, size=None):
        """
        Generators is the minimal (southwest) elements of the inertia

        size is an optional parameter giving the size of the matrix

        If size is given, the entire inertia set is plotted.  Otherwise just the generators are plotted.
        """
        self.generators=set(generators)
        self.generators.update([(y,x) for x,y in self.generators])
        self.reduce()
        self.size=size

    def __add__(self, right):
        """
        Minkowski sum of self and right
        """
        from itertools import product
        size=self.size or right.size
        return InertiaSet([(r1+r2, s1+s2) for ((r1,s1),(r2,s2)) in product(self.generators,
                                                                         right.generators)],
            size=self.size or right.size)

    def union(self, other):
        if isinstance(other, InertiaSet):
            return InertiaSet(self.generators.union(other.generators), size=self.size or other.size)
        else:
            return InertiaSet(self.generators.union(other), size=self.size)
    
    __or__=union

    def reduce(self):
        self.generators=set([x for x in self.generators 
                             if not any(x!=y and x[0]>=y[0] and x[1]>=y[1] 
                                        for y in self.generators)])

    def __repr__(self):
        return "Extended Inertia Set generated by %s"%self.generators

    def __eq__(self, other):
        # assume that both InertiaSets are reduced.
        return self.generators==other.generators and self.size==other.size

    def __contains__(self, p):
        return any(x[0]<=p[0] and x[1]<=p[1] for x in self.generators)

    def plot(self, *args, **kwargs):
        from sage.all import points
        p = set(self.generators)
        if self.size:
            for x,y in self.generators:
                p.update(*[[(i,j) for i in range(x,self.size-j+1)] for j in range(y,self.size-x+1)])
            max_tick=self.size
        else:
            max_tick=max(i[0] for i in self.generators)
        defaults=dict(pointsize=70,gridlines=True,
                ticks=[range(max_tick+1),range(max_tick+1)],
                aspect_ratio=1, xmin=0, ymin=0, frame=True, axes=False)
        defaults.update(kwargs)
        return points(p, *args, **defaults)

inertia_cache = dict()
def basic_inertia_set(g):
    global inertia_cache
    g6=g.canonical_label().graph6_string()
    if g6 in inertia_cache:
        return inertia_cache[g6]
    elif g.order()==1:
        return InertiaSet([(0,0)], size=g.order())
    elif g.order()==2 and g.size()==1:
        return InertiaSet([(0,1)], size=g.order())
    elif g.degree_sequence()[0]==g.order()-1 and g.degree_sequence()[1]==1:
        # g is a star
        return InertiaSet([(1,1), (g.order()-1,0)], size=g.order())
    
    raise ValueError("Do not know inertia set")

import random #in Sage 6.8, a modified version of random is included in misc/prandom.py
one_one=InertiaSet([(1,1)])
def inertia_set(g):
    global inertia_cache
    g6=g.canonical_label().graph6_string()
    if g6 in inertia_cache:
        return inertia_cache[g6]
    components=g.connected_components_subgraphs()
    I=InertiaSet([(0,0)], size=g.order())
    for c in components:
        try:
            #print I
            I+=basic_inertia_set(c)
            #print I
        except ValueError:
            try:
                cut_vertex=random.choice(c.blocks_and_cut_vertices()[1]) #change random.choice to choice it no import
            except IndexError:
                raise ValueError("Can not decompose unknown graph further", c)
            h=c.copy()
            h.delete_vertex(cut_vertex)
            component_inertia=inertia_set(h,f)+one_one
            component_inertia|=sum((inertia_set(c.subgraph(cc+[cut_vertex]),f) 
                                               for cc in h.connected_components()), 
                                   InertiaSet([(0,0)]))
            I+=component_inertia
    inertia_cache[g6]=I
    return I

    

