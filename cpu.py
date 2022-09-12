import os, re, time

prog_log = "progs.txt"
limited_pids = []
excluded_pids = []
limit = 2.0
interval = 5 # secs

child_pid = None
child_processes = 0
process_pid = None

loop = True
while(loop):
	
	os.system(f"ps aux > {prog_log}")

	with open(prog_log) as file:
		lines = file.readlines()[1:]
		
	for process_info in lines:
		process_info = re.sub(re.compile("\s+"), " ", process_info)
		process_info = process_info.split(" ")

		process_pid = int(process_info[1])
		process_cpu = float(process_info[2])
		process_command = process_info[10]
		
		if process_cpu > limit and not (process_pid in limited_pids + excluded_pids):
			limited_pids.append(process_pid)
			print("limit:", process_pid, process_cpu, process_command)
			
			# create child process to handle cpulimit
			child_pid = os.fork()
			
			# execute if parent
			if child_pid > 0:
				excluded_pids.append(child_pid)
				child_processes += 1
				print(f"\nChild processes: {child_processes}\n\n")
			
			# execute if child
			if child_pid == 0:
				loop = False
				break
				
	# print("\n\n")
		
	time.sleep(interval)
	
# execute if child
if child_pid == 0:
	instance_pid = os.getpid()
	print(f"program fork (pid={instance_pid}) limiting process {process_command} having pid: {process_pid}\n")
	# limit the process
	os.system(f"cpulimit -p {process_pid} -l {limit}")