if [ ! -z $1 ] 
then 
    for t in $( ls test*.py ); do
      echo $t
      python $t
    done
else
    for t in $( ls test*.py ); do
      echo $t
      python $t -s
    done
fi
