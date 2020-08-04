set terminal pdfcairo enhanced font "Gill Sans,16" linewidth 2 rounded

set style line 100 lt 1 lc rgb "#606060"
set style line 101 lt 0 lc rgb "#606060"

set border 3 back ls 100
set grid noxtics ytics back ls 101
set xtics nomirror
set ytics nomirror
set pointsize 0.8

set style line 1 lt rgb "#CF0000" dt 2 lw 1 pt 6
set style line 2 lt rgb "#0BC681" lw 1 pt 9
set style line 3 lt rgb "#0E1589" lw 1 pt 13
set style line 4 lt rgb "#000000" lw 1 pt 5
set style line 5 lt rgb "#E69F00" lw 1 pt 2

set xlabel "Resource importance"
set ylabel "Coverage"

set parametric
const=0.8
set trange [0:1.0]


set title "XSBench vs. OpenMC on Xeon"
set output "xsbench-xeon.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_6a_xeon.txt" using 2:3:1 notitle with labels point pt 7 left offset -0.4,-0.8 font ",14"

set title "XSBench vs. OpenMC on Blue Gene/Q"
set output "xsbench-bgq.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_6b_bgq.txt" using 2:3:1 notitle with labels point pt 7 left offset 0.8,0 font ",14"


set title "RSBench vs. OpenMC on Xeon"
set output "rsbench-xeon.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_7a_xeon.txt" using 2:3:1 notitle with labels point pt 7 left offset -0.8,-0.8 font ",14"

set title "RSBench vs. OpenMC on Blue Gene/Q"
set output "rsbench-bgq.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_7b_bgq.txt" using 2:3:1 notitle with labels point pt 7 left offset -0.4,-0.8 font ",14"


set title "CMTbone vs. CMTnek (point compute kernel)"
set output "cmtbone-pck.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_8.txt" using 2:3:1 notitle with labels point pt 7 left offset -0.4,-0.8 font ",14"

set title "CMTbone vs. CMTnek (compute kernel)"
set output "cmtbone-ck.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_9.txt" using 2:3:1 notitle with labels point pt 7 left offset -0.4,-0.8 font ",14"

set title "CMTbone vs. CMTnek (comm kernel)"
set output "cmtbone-comm.pdf"

plot \
  t,const notitle with lines ls 1, \
  const,t notitle with lines ls 1, \
  "figure_10.txt" using 2:3:1 notitle with labels point pt 7 left offset -0.4,-0.8 font ",14"

