import xml.etree.ElementTree as ET
import gzip
from io import StringIO
from math import sqrt

class momentum:
    p4 = []
    def __init__(self, px=0.0, py=0.0, pz=0.0, e=0.0):
        self.p4 = [px, py, pz, e]
    def __str__(self):
        print '(px=%.3f, py=%.3f, pz=%.3f, E=%.3f ; m=%.3f)' % (p4, mass())
    def __add__(self, p2):
        for i in range(4):
            self.p4[i] += p2.p4[i]
        return self
    def p(self):
        out = 0.0
        for i in range(3):
            out += self.p4[i]**2
        return sqrt(out)
    def px(self):
        return self.p4[0]
    def py(self):
        return self.p4[1]
    def pz(self):
        return self.p4[2]
    def energy(self):
        return self.p4[3]
    def mass(self):
        return sqrt(self.energy()**2-self.p()**2)

class particle:
    mom = momentum()
    pdgId = 0
    def __init__(self, pdg, px, py, pz, e):
        self.mom = momentum(px, py, pz, e)
        self.pdgId = pdg
    def __str__(self):
        print 'particle with pdgid=%s and momentum: %s' % (self.pdgId, self.mom)
    def mass(self):
        return self.mom.mass()

class event:
    def __init__(self):
        self.clear()
    def addParticle(self, part):
        self.particles.append(part)
    def clear(self):
        self.particles = []

class reader:
    def __init__(self, filename):
        infile = open(filename)
        if '.gz' in filename:
            infile = gzip.open(filename)
        self._context = ET.iterparse(infile, events=('start',))
    def next(self, evt):
        evt.clear()
        for action, elem in self._context:
            if elem.tag=='event' and elem.text!=None:
                self.parseEvent(elem.text, evt)
            return True
        return False
    def parseEvent(self, text, evt):
        evt.clear()
        try:
            lines = [l for l in text.splitlines() if len(l)>0]
            num_part = lines[0].split()[0]
            for l in lines[1:]:
                pdg, status, par1, par2, col1, col2, px, py, pz, e, m = l.split()[0:11]
                evt.addParticle(particle(int(pdg), float(px), float(py), float(pz), float(e)))
            return True
        except AttributeError:
            print 'impossible to parse event:', text
            return False
