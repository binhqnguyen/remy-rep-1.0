#!/usr/bin/python
import sys

nsrc=1

SAMPLING_INTERVAL=20 #sampling a put for 20 pkts
count=0
total_bytes_sent=0.0
time_interval=0.0
last_time=0.0
last_seq=-1


def reset():
	count = 0
	total_bytes_sent=0.0
	time_interval=0.0
	last_time=0.0
	last_seq=-1


if len(sys.argv) <= 1:
	print "Usage %s <number of senders>" % sys.argv[0]
	sys.exit()

####Rx rate
for s_n in range (0,nsrc):	
	read_f_name = "flows/"+str(s_n)+"-"+str(nsrc)+"-send"
	write_f_name = read_f_name+".dat"
	print "calculating Rx rate ... %s, write to %s\n" % (read_f_name, write_f_name)
	in_f = open(read_f_name,"r")
	out_f = open(write_f_name,"w")
	for line in in_f:
		tokens = line.split()
		#print "%s %s\n" % (tokens[0], tokens[4])
		if last_seq == tokens[10]:
			continue
		last_seq = tokens[10]
		total_bytes_sent+=float (tokens[5]) #add new bytes sent
		count += 1
		#print "%d %s %f\n" % (count , tokens[0], total_bytes_sent)
		if count > SAMPLING_INTERVAL: #record a sampling value and reset an epoch
			count = 0
			time_interval = float (tokens[1]) - last_time
			#print "%f\n" % time_interval;
			out_f.write("%s %f\n" % (tokens[1], total_bytes_sent*8/time_interval) )
			#print "%s %f\n" % (tokens[0], total_bytes_sent*8/time_interval)

			total_bytes_sent=0
			time_interval=0
			last_time = float(tokens[1]) #update last sampling time.


##repeat for application send rate (enqueue speed)
reset()
for s_n in range (0,nsrc):	
	read_f_name = "flows/"+str(s_n)+"-"+str(nsrc)+"-sender-enqueue"
	write_f_name = read_f_name+".dat"
	print "calculating Tx ... %s, write to %s\n" % (read_f_name, write_f_name)
	in_f = open(read_f_name,"r")
	out_f = open(write_f_name,"w")
	for line in in_f:
		tokens = line.split()
		#print "%s %s\n" % (tokens[0], tokens[4])
		if last_seq == tokens[10]:
			continue
		last_seq = tokens[10]

		total_bytes_sent+=float (tokens[5]) #add new bytes sent
		count += 1
		#print "%d %s %f\n" % (count , tokens[0], total_bytes_sent)

		if count > SAMPLING_INTERVAL: #record a sampling value and reset an epoch
			count = 0
			time_interval = float (tokens[1]) - last_time
			if time_interval == 0: #bursty send
				continue
			out_f.write("%s %f\n" % (tokens[1], total_bytes_sent*8/time_interval) )
			#print "%s %f\n" % (tokens[0], total_bytes_sent*8/time_interval)

			total_bytes_sent=0
			time_interval=0
			last_time = float(tokens[1]) #update last sampling time.


##middlenode's queue size
reset()
for s_n in range (0,nsrc):	
	read_f_name = "flows/"+str(s_n)+"-"+str(nsrc)+"-middlenode-enqueue"
	read_f_name_2 =  "flows/"+str(s_n)+"-"+str(nsrc)+"-middlenode-dequeue"
	print "calculating middle node's queue size... %s, write to %s\n" % (read_f_name, write_f_name)
	in_f = open(read_f_name,"r")
	in_f_2 = open(read_f_name_2,"r")
	merge_f = open("tmp","w")

	tmp_map = {}
	out_f = open("flows/queue_size.dat","w")
	for line in in_f:
		tokens = line.split()
		tmp_map[tokens[1]] = tokens[0]+" "+tokens[5]+" "+tokens[10]+" "+tokens[11]
	
	for line in in_f_2:
		tokens = line.split()
		tmp_map[tokens[1]] = tokens[0]+" "+tokens[5]+" "+tokens[10]+" "+tokens[11]

		
	##sort the map of <time, enqueue/dequeue, bytes>
	for key in sorted(tmp_map):
		merge_f.write("%s %s\n" % (key, tmp_map[key]))
		#print ("%s %s\n" % (key, tmp_map[key]))
	
	queue_size = 0
	in_f = open("tmp","r")
	for line in in_f:
		#print "%s %s\n" % (tokens[0], tokens[4])
		tokens = line.split()
		if tokens[1] == "+":
			print "enque...\n"
			queue_size += int(tokens[2])
		if tokens[1] == "-":
			print "dequeu...\n"
			queue_size -= int(tokens[2])
		count += 1
		if count > SAMPLING_INTERVAL:
			out_f.write("%s %f\n" % (tokens[0], queue_size) )

in_f.close()
out_f.close()








