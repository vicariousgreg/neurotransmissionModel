for t in $( ls test*.py ); do
  python $t -s -v
done
