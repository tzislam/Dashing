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

set ylabel "Resource importance"
set xlabel "Resources" offset 0, 0.7

set xrange[-.5:7.5]


set key at graph 0.3, graph 0.95
set title "Resource utilization of different STREAM kernels"
set output "stream.pdf"

plot 'stream-2600.dat' using 2:xtic(1) title "ADD" fs pattern 1 ls 1, \
'' u 3 title "SCALE" fs pattern 2 ls 2, \
'' u 4 title "COPY" fs pattern 3 ls 3, \
'' u 5 title "TRIAD" fs pattern 4 ls 4


set key at graph 0.95, graph 0.95
set title "Resource utilization for DGEMM"
set output "dgemm.pdf"

plot 'dgemm.dat' using 4:xtic(1) notitle fs pattern 1 ls 1
