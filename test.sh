for t in $( ls test*.py ); do
  echo $t
  python $t -s
done
python simulation.py -s
