import os, re, time

prog_log = "progs.txt"
limited_pids = {}
excluded_pids = {}
limit = 20
interval = 5 # secs

child_pid = None
child_processes = 0
process_pid = None

main_pid = os.getpid()
excluded_pids[main_pid] = True

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
		
		if process_cpu > limit:
			if not process_pid in excluded_pids:
				# if pid has not been marked as 'limited' or it has been
				# marked as 'limited' but now points to another program
				if (not process_pid in limited_pids) or \
					limited_pids[process_pid] != process_command:

					# mark pid with associated command to avoid repeated limits
					limited_pids[process_pid] = process_command
					print("limit:", process_pid, process_cpu, process_command)
					
					# create child process to handle cpulimit
					child_pid = os.fork()
					
					# execute if parent
					if child_pid > 0:
						# mark child process for exclusion to avoid a chain of infinite limits
						excluded_pids[child_pid] = True
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
