#!/bin/bash
DATE=`date +%Y%m%d`
echo "*** Sending the alerting results generated on " ${DATE}
python /data4/Panda/exportData/Alert_System/AlertSystem.py /data4/Panda/exportData/${DATE}/ ${DATE} > /data4/Panda/exportData/Alert_System/log/${DATE}_out.log