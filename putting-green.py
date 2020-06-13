#!/usr/bin/python

w = 8.0  # metres
h = 10.5 # metres
depth = 0.45 # m

area = w * h
volume = area * depth

barrel_w = 0.55
barrel_h = 0.7
barrel_d = 0.20
barrel_v = barrel_w * barrel_h * barrel_d

print "Width = %.1f m, Height = %.1f m, Depth = %d cm" % (w, h, depth * 100)
print "Volume = %.1f cubic metres" % volume
print "Barrel Volume %0.2f cubic metres" % barrel_v
print "Number of barrels %d" % (volume / barrel_v)



