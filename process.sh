#!/bin/bash
F="remycc"
TRACE_ALL="trace_all.tr"
TRACE_APP="app-trace.tr"
nsrc=1

if [ "$1" == "" ]; then
	echo "usage: process.sh <number of sending sources>"
	exit
fi

rm cwnd*
rm rtt*
rm ack*
rm maxse*
rm dupac*
rm ssth*
mkdir flows
mkdir apps

nsrc=$1
sender_port=0		#const
receiver_number=$nsrc

for ((sender_number=0; sender_number < $nsrc; sender_number++))	#sender_number = 0 ... $nsrc-1.
do
	S="$sender_number  $sender_port"	#sender<number, port> = <$sender_number,0>
	S_num="$sender_number"
	R_num="$receiver_number"
	R="$receiver_number  $sender_number"	#receiver<number,port> = <$nsrc, $sender_number>

	echo "Sender = $S -> receiver = $R"
	
	###filter remycc.tr for Tcp variables of sending flows:
	grep "$S  $R  cwnd_" $F-$sender_number.tr > cwnd_$sender_number	#cwnd of flow x
	grep "$S  $R  ack_" $F-$sender_number.tr > ack_$sender_number	#ack of the flow above
	grep "$S  $R  maxseq_" $F-$sender_number.tr > maxseq_$sender_number
	grep "$S  $R  rtt_" $F-$sender_number.tr > rtt_$sender_number
	grep "$S  $R  ssthresh_" $F-$sender_number.tr > ssthresh_$sender_number
	grep "$S  $R  dupacks_" $F-$sender_number.tr > dupacks_$sender_number

	###filter trace_all.tr and app-trace.tr for: e2e throughput, delay, queue size, losses, etc.
	middle_node=$[$nsrc+1]	#middle node forwarding packet, its node number is the nsrc+1.

	echo $middle_node
	
	#sender-enqueued
	grep "$S_num.$sender_port $R_num.$sender_number" $TRACE_ALL | grep "+" | grep "tcp" | grep "$S_num $middle_node tcp" > flows/$S_num-$R_num-sender-enqueue #sender enqueue/ app sending rate.

	#middle_node enqueued and dequeued.
	grep "$S_num.$sender_port $R_num.$sender_number" $TRACE_ALL | grep "+" | grep "tcp" | grep "$middle_node $R_num tcp" > flows/$S_num-$R_num-middlenode-enqueue #middle node enqueue.
	grep "$S_num.$sender_port $R_num.$sender_number" $TRACE_ALL | grep "-" | grep "r" -v | grep "d" -v | grep "+" -v | grep "tcp" | grep "$middle_node $R_num tcp" > flows/$S_num-$R_num-middlenode-dequeue #middle node dequeue.

	#send-received
	echo "$S_num.$sender_port $R_num.$sender_number" 
	grep "$S_num.$sender_port $R_num.$sender_number" $TRACE_ALL | grep "r" | grep "tcp" | grep "$middle_node $R_num tcp" > flows/$S_num-$R_num-send #received flow

	#ack-received
	grep "$R_num.$sender_number $S_num.$sender_port" $TRACE_ALL | grep "r" | grep "ack" | grep "$middle_node $S_num ack" > flows/$S_num-$R_num-ack #received flow

	#app on time
	grep "app $sender_number ON" $TRACE_APP > apps/$sender_number-on

	#app off time
	grep "app $sender_number OFF" $TRACE_APP > apps/$sender_number-off

	#drop pkts
	grep "$S_num.$sender_port $R_num.$sender_number" $TRACE_ALL | grep "d" | grep "tcp" | grep "$S_num $middle_node tcp" > flows/$S_num-$R_num-send-drop #app sending
	grep "$R_num.$sender_number $S_num.$sender_port" $TRACE_ALL | grep "d" | grep "ack" | grep "$S_num $middle_node tcp" > flows/$S_num-$R_num-ack-drop #app sending

done	


###run the througput calculation
python ./calculate_put.py

