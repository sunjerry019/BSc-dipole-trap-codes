#!/usr/bin/env gnuplot

set term epslatex color size 5.6in, 4in
set output "2022-07-12_IPG_m2.tex"

set key autotitle columnhead

set title "IPG-YLR-200-LP-WC Caustic Measurement, Wavelength $= 1070~\\si{\\nano\\meter}$"
set ylabel "Beam Radius ($\\si{\\micro\\meter}$)"
set xlabel "Position ($\\si{\\milli\\meter}$)"

set mxtics
set mytics
set samples 10000

set key top right

wavelength = 1070

# w0, z0, msq
f(x) = 23.79708627 * sqrt(1 + ((x - (7.73953974))**2)*(((1.03252135 * wavelength)/(pi * (23.79708627**2)))**2))
g(x) = 24.25144646 * sqrt(1 + ((x - (7.27852809))**2)*(((1.06551593 * wavelength)/(pi * (24.25144646**2)))**2))
# f(x) = wzero * sqrt(1 + ((x - zzero)**2)*(((M_sq * wavelength)/(pi * (wzero**2)))**2))

# https://www.gnuplotting.org/line-breaks-in-labels/
# https://tex.stackexchange.com/a/42860
set label "\\shortstack[l]{Thorlabs LA1433-B Lens\\\\$f = \\SI{150}{\\milli\\meter}$}" at 3.7,75 left

# (x, y, xdelta, ydelta)
plot "2022-07-12_IPG_m2.dat" u 1:($3/2):(0.1) w yerrorbars title "Horizontal" lc 1, \
	f(x) title "Horizontal-Fit, $M^2 = 1.033$" lc 1, \
	"2022-07-12_IPG_m2.dat" u 1:($2/2):(0.1) w yerrorbars title "Vertical" lc 4, \
	g(x) title "Vertical-Fit, $M^2 = 1.066$" lc 4