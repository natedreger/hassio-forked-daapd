#!/usr/bin/env bash
# mabye use for jsonValue https://gist.github.com/cjus/1047794
# choose-group.sh
# Shell script to control forked-daapd
# Turns on or off a group of speakers and sets default volumes

source /config/shell_scripts/jsonValue
#source jsonValue # Local file location

# Find the difference in two arrays thanks to https://stackoverflow.com/users/207248/siegex
diff(){
  awk 'BEGIN{RS=ORS=" "}
       {NR==FNR?k[$0]++:k[$0]--}
       END{for(a in k)if(k[a])print a}' <(echo -n "${!1}") <(echo -n "${!2}")
}


# IP address of forked-daapd installation, include port number
HOST_IP=192.168.0.101:3689

# reset the counters
i=0
l=0
n=0
o=0
v=0

# Add some default values if no values are passed
FUNCTION='true'
MASTER_VOLUME=50
GROUP=Everywhere

# Setup search parameters
SEARCH_FILE=/config/forked-daapd/groups/AllOutputs.json
#SEARCH_FILE=AllOutputs.json # local file location

# define search terms for parsing
SEARCH_ID='id'
SEARCH_NAME='name'
SEARCH_VOLUME='default'
SEARCH_MVOLUME='master'
SEARCH_SELECTION='selected'

# Get all the outputs and make files for None group and a reference
curl -X GET "http://$HOST_IP/api/outputs" -o /config/forked-daapd/groups/AllOutputs.json
curl -X GET "http://$HOST_IP/api/outputs" -o /config/forked-daapd/groups/None.json
#curl -X GET "http://$HOST_IP/api/outputs" -o AllOutputs.json # Local file location
#curl -X GET "http://$HOST_IP/api/outputs" -o None.json # Local file location

# Lets read all the exisiting outputs just for fun
outputs=`cat $SEARCH_FILE | jsonValue $SEARCH_ID`
for output in $outputs; do
  EXISTING_OUTPUTS[$o]=$output
  o=$((o+1))
done

echo "Existing outputs: "${EXISTING_OUTPUTS[@]}
# Assign arguments to the variables

# Group
if [ $1 != $GROUP ]
  then
    GROUP=$1
fi

# Are we turning ON or off?
if [ $2 == 'On' ]
  then
    FUNCTION=true
  elif [ $2 == 'Off' ]
  then
    FUNCTION=false
  fi


# Open the file with the group definitions
#SEARCH_FILE=$GROUP.json # Local file location
SEARCH_FILE=/config/forked-daapd/groups/$GROUP.json

echo "Searching" $SEARCH_FILE "for outputs."

# Here we're Searching the file for the keys and adding them to arrays

ids=`cat $SEARCH_FILE | jsonValue $SEARCH_ID`
for id in $ids; do
  GROUP_DEVICES[$l]=$id
  l=$((l+1))
done
echo ${#GROUP_DEVICES[*]}" devices added to" $GROUP "group."

names=`cat $SEARCH_FILE | jsonValue $SEARCH_NAME`
for name in $names; do
  DEVICE_NAMES[$n]=$name
  n=$((n+1))
done
  echo ${DEVICE_NAMES[@]}" were added to" $GROUP "group."

volumes=`cat $SEARCH_FILE | jsonValue $SEARCH_VOLUME`
for volume in $volumes; do
  DEVICE_VOLUMES[$v]=$volume
  v=$((v+1))
done
echo ${DEVICE_VOLUMES[@]}" volumes were applied to" $GROUP "group devices."

selections=`cat $SEARCH_FILE | jsonValue $SEARCH_SELECTION`
for selection in $selections; do
 case $GROUP in
  None)
    DEVICE_SELECTIONS[$s]='false'
    ;;
  *)
    DEVICE_SELECTIONS[$s]=$selection
    ;;
esac

  s=$((s+1))
done

echo ${DEVICE_SELECTIONS[@]}" selections were applied to" $GROUP "group devices."

# Lets do this!

# Loop through the group device array and turn speakers on
for DEVICE in "${GROUP_DEVICES[@]}"
do
  curl -X PUT "http://$HOST_IP/api/outputs/$DEVICE" --data "{\"selected\":${DEVICE_SELECTIONS[$i]}}"
  echo "id:"$DEVICE" is "$1" with volume set to: "${DEVICE_VOLUMES[$i]}
  i=$((i+1))
done

# pause quickly between operations
sleep 1

# Loop through the group device array and set default volume
i=0
for DEVICE in "${GROUP_DEVICES[@]}"
do
  curl -X PUT "http://$HOST_IP/api/player/volume?volume=${DEVICE_VOLUMES[$i]}&output_id=$DEVICE"
  echo "id:"$DEVICE" is "$1" with volume set to: "${DEVICE_VOLUMES[$i]}
  i=$((i+1))
done


# Use the diff function to find the difference between current group array and existing outputs

NON_GROUP_DEVICES=($(diff GROUP_DEVICES[@] EXISTING_OUTPUTS[@] ))

# Loop through the EXISTING_OUTPUTS and turn off stuff not in current group
for DEVICE_OFF in "${NON_GROUP_DEVICES[@]}"
do
  curl -X PUT "http://$HOST_IP/api/outputs/$DEVICE_OFF" --data "{\"selected\":false}"
  echo "id:"$DEVICE" is off"
  i=$((i+1))
done


# Get master volume from the group config if present
MASTER_VOLUME=`cat $SEARCH_FILE | jsonValue $SEARCH_MVOLUME`

# Master Volume Override
if [ $3 != $MASTER_VOLUME ]
  then
    MASTER_VOLUME=$3
fi

#now set the master volume
curl -X PUT "http://$HOST_IP/api/player/volume?volume=$MASTER_VOLUME"

echo $GROUP "group is on"
echo "Master volume set to "$MASTER_VOLUME
