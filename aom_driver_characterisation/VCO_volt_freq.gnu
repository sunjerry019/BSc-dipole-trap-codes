#!/usr/bin/env gnuplot

set term epscairo
set output "VCO_volt_freq.eps"
f(x) = A*x + b

fit f(x) "VCO_volt_freq.dat" u 1:2:3 yerrors via A,b

plot "VCO_volt_freq.dat" u 1:2:3 with yerrorbars, f(x)

# RESULTS: F = 8.43397*V + 65.2