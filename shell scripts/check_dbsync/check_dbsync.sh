#!/bin/sh
# Check  DB sync back log
## Checks every 10 mins whether anything is upated for BP table.

#
#

DBSRV="xxx.ie.company.net"
export DBSRV
DB="cdspdsp1"

check_appdbsync () {
SCHEMA="$1"
TBL="$2"
#x=`sqlplus -s xxx/xxx@${DBSRV}:1521/${DB} <<endl
x=`sqlplus -s xxx/xxxxx@${DBSRV}:1521/cdsshema <<endl
alter session set nls_date_format="yyyy-mm-dd hh24:mi:ss";
select _last_update_dt from ${SCHEMA}.${TBL} where (systimestamp - _last_update_dt) < interval '10' minute;
exit
endl"
`


rowcount=`echo "$x"|sed -n '/rows selected./ s/selected.//p'`
rcount=`echo "$x"|sed -n '/rows selected./ s/rows selected.//p'`
LPAT=`date +%s`


echo "Row Count: $rcount"
PREVCOUNT=`cat $HOME/tmp-${TBL}.txt|awk -F":" '/Row Count/ {print $2}'`
echo "Previous Count: $PREVCOUNT"

CUR_LAST3=`echo "$x"|tail -3`
PREV_LAST3=`cat $HOME/tmp-${TBL}.txt|tail -4`

if [ -n "$rcount" ] && [ ! -z "$rcount" ]; then
echo "Row Count: $rcount" > $HOME/tmp-${LPAT}.txt
echo "TimeStamp:\n$x">> $HOME/tmp-${LPAT}.txt
echo "--TimeStamp End--" >> $HOME/tmp-${LPAT}.txt
fi

CUR_TS=`echo "$CUR_LAST3"|head -1`
PREV_TS=`echo "$PREV_LAST3"|head -1`
echo "Current TS: $CUR_TS"
echo "Previous TS: $PREV_TS"

if [ -s $HOME/tmp-${LPAT}.txt ]; then
mv $HOME/tmp-${LPAT}.txt $HOME/tmp-${TBL}.txt
fi

}

echo " DB Sync Details for Cust Entitlement Offering Table"
echo "-------------------------------------------------------"
check_dbsync asset cust_entitled_offering
echo "-------------------------------------------------------"
echo " DB Sync Details for Billing profile Table"
echo "---------------------------------------------"
check_dbsync billing billing_profile
echo "-------------------------------------------------------"

