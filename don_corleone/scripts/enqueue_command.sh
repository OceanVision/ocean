COUNTER=0
# Wait for lock for 2 seconds
while [ -f command_queue_lock ]
do
  sleep 1
  echo 'Waitning for lock ...'
  echo $COUNTER
  COUNTER=$((COUNTER+1))
  if [ $COUNTER -gt 2 ]
  then
      exit 1
  fi
done

echo $1 >> command_queue
