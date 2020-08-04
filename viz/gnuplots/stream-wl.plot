set terminal pdfcairo enhanced font "Gill Sans,16" linewidth 2 rounded

set style line 100 lt 1 lc rgb "#606060"
set style line 101 lt 0 lc rgb "#606060"

set border 3 back ls 100
set grid noxtics ytics back ls 101
set xtics nomirror offset 0, 0.5 font ",14"
set ytics nomirror

set boxwidth 1.0 absolute
set style fill pattern 1 border
set style histogram clustered gap 2 title offset 0, 0.2
set style data histograms

set style line 1 lt rgb "#CF0000" lw 1 pt 7
set style line 2 lt rgb "#0BC681" lw 1 pt 9
set style line 3 lt rgb "#0E1589" lw 1 pt 13
set style line 4 lt rgb "#000000" lw 1 pt 5
set style line 5 lt rgb "#E69F00" lw 1 pt 2

set ylabel "Coverage"
set xlabel "Resources" offset 0,0.9

set xrange[-.5:7.5]

set bmargin 4
set key bmargin center maxrows 1
set title "Coverage analysis of different STREAM kernels"
set output "stream-wl.pdf"

plot 'stream-wl-2600.dat' using 2:xtic(1) title "ADD vs. TRIAD" fs pattern 1 ls 1, \
'' u 4 title "COPY vs. SCALE" fs pattern 3 ls 3

