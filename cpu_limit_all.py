import os, re, time, json

prog_log = "progs.txt"
settings_file = "settings.ini"
limited_pids = {}
excluded_pids = {}

child_pid = None
child_processes = 0
process_pid = None

main_pid = os.getpid()
excluded_pids[main_pid] = True

loop = True
while(loop):
	
	os.system(f"ps aux > {prog_log}")

	with open(settings_file) as file:
		settings = json.load(file)
		limit = float(settings["limit"])		# % cpu
		interval = float(settings["interval"])	# seconds

	with open(prog_log) as file:
		lines = file.readlines()[1:]
	
	current_pids = []
	for process_info in lines:
		process_info = re.sub(re.compile("\s+"), " ", process_info)
		process_info = process_info.split(" ")

		process_pid = int(process_info[1])
		process_cpu = float(process_info[2])
		process_command = process_info[10]
		
		current_pids.append(process_pid)

		if process_cpu > limit:
			if not process_pid in excluded_pids:
				# if pid has not been marked as 'limited' or it has been
				# marked as 'limited' but now points to another program
				if (not process_pid in limited_pids) or \
					limited_pids[process_pid] != process_command:

					# mark pid with associated command to avoid repeated limits
					limited_pids[process_pid] = process_command
					print(f"limit process: pid={process_pid}, cpu_usage={process_cpu}%, command={process_command}")
					
					# create child process to handle cpulimit
					child_pid = os.fork()
					
					# execute if parent
					if child_pid > 0:
						# mark child process for exclusion to avoid a chain of infinite limits
						excluded_pids[child_pid] = process_pid
						child_processes += 1
						print(f"\nChild processes: {child_processes}\n\n")
					
					# execute if child
					if child_pid == 0:
						loop = False
						break

	# make copy so we can make changes as we iterate through it -- improve this later
	excluded_pids_ = excluded_pids.copy()

	# kill child processes assigned to PIDs no longer active
	for pid, assigned_pid in excluded_pids_.items():
		if type(assigned_pid) == int and not assigned_pid in current_pids:
			# kill the child process via pid			
			os.system(f"kill -9 {pid}")
			print(f"Killed child process (pid={pid}) tasked with limiting dead process of PID: {assigned_pid}")
			child_processes -= 1
			print(f"\nChild processes: {child_processes}\n\n")

			# remove the child pid from excluded pids
			excluded_pids.pop(pid)
			
			# remove the assigned pid from limited pids
			limited_pids.pop(assigned_pid)

				
	# print("\n\n")			
	time.sleep(interval)
	
# execute if child
if child_pid == 0:
	instance_pid = os.getpid()
	print(f"program fork (pid={instance_pid}) limiting process {process_command} having pid: {process_pid}\n")
	# limit the process
	os.system(f"cpulimit -p {process_pid} -l {limit}")
