import os
import sys
import shlex
import signal
import time
import heapq
import threading
import random
from collections import deque

# ==========================================
# ORIGINAL CODE FROM Shell.py
# ==========================================

jobs = {}
job_counter = 1

def clean_finished_jobs():
    finished = []
    for jid, pid in list(jobs.items()):
        try:
            result = os.waitpid(pid, os.WNOHANG)
            if result[0] != 0:
                finished.append(jid)
        except ChildProcessError:
            finished.append(jid)
    for jid in finished:
        del jobs[jid]

def execute_command(args, background=False):
    global job_counter
    pid = os.fork()
    if pid == 0:
        try:
            os.execvp(args[0], args)
        except FileNotFoundError:
            print(f"Command not found: {args[0]}")
            os._exit(1)
    else:
        if background:
            jobs[job_counter] = pid
            print(f"[{job_counter}] started with PID {pid}")
            job_counter += 1
        else:
            os.waitpid(pid, 0)

class SimProcess:
    def __init__(self, pid, name, burst_time, priority=0, arrival_order=0):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.arrival_order = arrival_order
        self.start_time = None
        self.finish_time = None
        self.response_time = None
        self.waiting_time = 0
        self.turnaround_time = 0

    def __repr__(self):
        return (
            f"PID={self.pid}, Name={self.name}, Burst={self.burst_time}, "
            f"Remaining={self.remaining_time}, Priority={self.priority}"
        )

class Scheduler:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rr_queue = deque()
        self.priority_queue = []
        self.completed = []
        self.sim_pid_counter = 1
        self.arrival_counter = 0

    def add_rr_process(self, name, burst_time):
        p = SimProcess(
            pid=self.sim_pid_counter,
            name=name,
            burst_time=burst_time,
            arrival_order=self.arrival_counter
        )
        self.rr_queue.append(p)
        self.sim_pid_counter += 1
        self.arrival_counter += 1
        print(f"Added RR process -> {p}")

    def add_priority_process(self, name, burst_time, priority):
        p = SimProcess(
            pid=self.sim_pid_counter,
            name=name,
            burst_time=burst_time,
            priority=priority,
            arrival_order=self.arrival_counter
        )
        heapq.heappush(self.priority_queue, (priority, self.arrival_counter, p))
        self.sim_pid_counter += 1
        self.arrival_counter += 1
        print(f"Added Priority process -> {p}")

    def show_rr_queue(self):
        if not self.rr_queue:
            print("Round-Robin queue is empty.")
            return
        print("Round-Robin Queue:")
        for p in self.rr_queue:
            print(f"  {p}")

    def show_priority_queue(self):
        if not self.priority_queue:
            print("Priority queue is empty.")
            return
        print("Priority Queue:")
        for prio, order, p in sorted(self.priority_queue, key=lambda x: (x[0], x[1])):
            print(f"  PID={p.pid}, Name={p.name}, Burst={p.burst_time}, Remaining={p.remaining_time}, Priority={p.priority}")

    def run_round_robin(self, quantum):
        if not self.rr_queue:
            print("No Round-Robin processes to schedule.")
            return
        print(f"\nStarting Round-Robin Scheduling with quantum = {quantum}\n")
        current_time = 0
        completed_local = []
        while self.rr_queue:
            process = self.rr_queue.popleft()
            if process.start_time is None:
                process.start_time = current_time
                process.response_time = process.start_time
            run_time = min(quantum, process.remaining_time)
            print(
                f"Running Process PID={process.pid}, Name={process.name}, "
                f"for {run_time} unit(s). Remaining before run = {process.remaining_time}"
            )
            time.sleep(run_time)
            process.remaining_time -= run_time
            current_time += run_time
            if process.remaining_time == 0:
                process.finish_time = current_time
                process.turnaround_time = process.finish_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed_local.append(process)
                print(
                    f"Completed Process PID={process.pid}, Name={process.name}, "
                    f"Finish Time={process.finish_time}"
                )
            else:
                print(
                    f"Time slice expired for PID={process.pid}, Name={process.name}. "
                    f"Remaining Time={process.remaining_time}. Moving to back of queue."
                )
                self.rr_queue.append(process)
            print("-" * 60)
        self.completed.extend(completed_local)
        self.print_metrics(completed_local, "Round-Robin")

    def run_priority_preemptive(self):
        if not self.priority_queue:
            print("No Priority processes to schedule.")
            return
        print("\nStarting Preemptive Priority Scheduling\n")
        current_time = 0
        completed_local = []
        while self.priority_queue:
            priority, arrival_order, process = heapq.heappop(self.priority_queue)
            if process.start_time is None:
                process.start_time = current_time
                process.response_time = process.start_time
            print(
                f"Running Process PID={process.pid}, Name={process.name}, "
                f"Priority={process.priority}, Remaining={process.remaining_time}"
            )
            time.sleep(1)
            process.remaining_time -= 1
            current_time += 1
            if process.remaining_time == 0:
                process.finish_time = current_time
                process.turnaround_time = process.finish_time
                process.waiting_time = process.turnaround_time - process.burst_time
                completed_local.append(process)
                print(
                    f"Completed Process PID={process.pid}, Name={process.name}, "
                    f"Finish Time={process.finish_time}"
                )
            else:
                print(
                    f"Preempting/Re-queueing PID={process.pid}, Name={process.name}, "
                    f"Remaining={process.remaining_time}"
                )
                heapq.heappush(
                    self.priority_queue,
                    (process.priority, process.arrival_order, process)
                )
            print("-" * 60)
        self.completed.extend(completed_local)
        self.print_metrics(completed_local, "Priority-Based Scheduling")

    def print_metrics(self, processes, algorithm_name):
        if not processes:
            print(f"No completed processes for {algorithm_name}.")
            return
        print(f"\nPerformance Metrics for {algorithm_name}")
        print("=" * 72)
        print(
            f"{'PID':<8}{'Name':<15}{'Burst':<10}{'Priority':<10}"
            f"{'Waiting':<12}{'Turnaround':<14}{'Response':<10}"
        )
        total_waiting = 0
        total_turnaround = 0
        total_response = 0
        for p in processes:
            total_waiting += p.waiting_time
            total_turnaround += p.turnaround_time
            total_response += p.response_time
            print(
                f"{p.pid:<8}{p.name:<15}{p.burst_time:<10}{p.priority:<10}"
                f"{p.waiting_time:<12}{p.turnaround_time:<14}{p.response_time:<10}"
            )
        n = len(processes)
        print("=" * 72)
        print(f"Average Waiting Time   : {total_waiting / n:.2f}")
        print(f"Average Turnaround Time: {total_turnaround / n:.2f}")
        print(f"Average Response Time  : {total_response / n:.2f}")
        print()

    def show_completed(self):
        if not self.completed:
            print("No completed scheduled processes.")
            return
        print("Completed Scheduled Processes:")
        for p in self.completed:
            print(
                f"PID={p.pid}, Name={p.name}, Burst={p.burst_time}, "
                f"Priority={p.priority}, Waiting={p.waiting_time}, "
                f"Turnaround={p.turnaround_time}, Response={p.response_time}"
            )

scheduler = Scheduler()

def print_scheduler_help():
    print("\nScheduler Commands:")
    print("  rr_add <name> <burst_time>")
    print("  rr_show")
    print("  rr_run <quantum>")
    print("  prio_add <name> <burst_time> <priority>")
    print("  prio_show")
    print("  prio_run")
    print("  sched_completed")
    print("  sched_reset")
    print("\nDeliverable 3 Commands:")
    print("  demo : Run the memory management & synchronization demo")
    print()


# ==========================================
# ORIGINAL CODE FROM deliverable_3.py
# ==========================================

FRAME_COUNT = 3
memory = []
page_faults = 0
time_counter = 0

class Frame:
    def __init__(self, process_id, page):
        global time_counter
        self.process_id = process_id
        self.page = page
        self.loaded_time = time_counter
        self.last_used = time_counter

def print_memory():
    print("\nCurrent Memory Frames:")
    for i, frame in enumerate(memory):
        print(f"Frame {i}: Process {frame.process_id} Page {frame.page}")
    print()

def fifo_replace():
    oldest = min(memory, key=lambda x: x.loaded_time)
    return oldest

def lru_replace():
    least_used = min(memory, key=lambda x: x.last_used)
    return least_used

def request_page(process_id, page, algorithm="FIFO"):
    global page_faults, time_counter
    time_counter += 1
    for frame in memory:
        if frame.process_id == process_id and frame.page == page:
            frame.last_used = time_counter
            print(f"Process {process_id} accessed Page {page} (Already in memory)")
            return
    print(f"\nPAGE FAULT: Process {process_id} requested Page {page}")
    page_faults += 1
    if len(memory) < FRAME_COUNT:
        memory.append(Frame(process_id, page))
        print(f"Loaded Page {page} of Process {process_id} into memory")
    else:
        if algorithm == "FIFO":
            victim = fifo_replace()
            print(f"FIFO replacing Process {victim.process_id} Page {victim.page}")
        else:
            victim = lru_replace()
            print(f"LRU replacing Process {victim.process_id} Page {victim.page}")
        memory.remove(victim)
        memory.append(Frame(process_id, page))
    print_memory()

BUFFER_SIZE = 5
buffer = []
mutex = threading.Semaphore(1)
empty = threading.Semaphore(BUFFER_SIZE)
full = threading.Semaphore(0)

def producer():
    for i in range(5):
        item = random.randint(1, 100)
        empty.acquire()
        mutex.acquire()
        buffer.append(item)
        print(f"Producer produced {item} | Buffer: {buffer}")
        mutex.release()
        full.release()
        time.sleep(1)

def consumer():
    for i in range(5):
        full.acquire()
        mutex.acquire()
        item = buffer.pop(0)
        print(f"Consumer consumed {item} | Buffer: {buffer}")
        mutex.release()
        empty.release()
        time.sleep(1)

# --- THE ONLY MODIFICATION: Wrap the execution in a function ---
def run_deliverable_3_demo():
    global memory, page_faults # Added to prevent global variable errors

    print("\n============================")
    print(" MEMORY MANAGEMENT (FIFO)")
    print("============================")

    requests = [(1,1),(1,2),(2,1),(1,3),(2,2),(1,4)]

    for p, page in requests:
        request_page(p,page,"FIFO")

    print(f"\nTotal Page Faults (FIFO): {page_faults}")

    # Reset for LRU
    memory.clear()
    page_faults = 0

    print("\n============================")
    print(" MEMORY MANAGEMENT (LRU)")
    print("============================")

    for p, page in requests:
        request_page(p,page,"LRU")

    print(f"\nTotal Page Faults (LRU): {page_faults}")

    print("\n============================")
    print(" PRODUCER CONSUMER DEMO")
    print("============================")

    p = threading.Thread(target=producer)
    c = threading.Thread(target=consumer)

    p.start()
    c.start()

    p.join()
    c.join()

    print("\nExecution Complete")

# ==========================================
# MAIN SHELL LOOP (From Shell.py)
# ==========================================

def run_shell():
    while True:
        clean_finished_jobs()
        try:
            command_input = input("myshell> ")
            if not command_input.strip():
                continue

            args = shlex.split(command_input)
            cmd = args[0]

            if cmd == "exit":
                print("Exiting shell...")
                sys.exit(0)
            elif cmd == "pwd":
                print(os.getcwd())
            elif cmd == "cd":
                if len(args) < 2:
                    print("cd: missing argument")
                else:
                    try:
                        os.chdir(args[1])
                    except FileNotFoundError:
                        print("cd: directory not found")
            elif cmd == "echo":
                print(" ".join(args[1:]))
            elif cmd == "clear":
                os.system("clear")
            elif cmd == "ls":
                execute_command(["ls"])
            elif cmd == "cat":
                if len(args) < 2:
                    print("cat: missing filename")
                else:
                    execute_command(args)
            elif cmd == "mkdir":
                if len(args) < 2:
                    print("mkdir: missing directory name")
                else:
                    try: os.mkdir(args[1])
                    except Exception as e: print(f"mkdir error: {e}")
            elif cmd == "rmdir":
                if len(args) < 2:
                    print("rmdir: missing directory name")
                else:
                    try: os.rmdir(args[1])
                    except Exception as e: print(f"rmdir error: {e}")
            elif cmd == "rm":
                if len(args) < 2:
                    print("rm: missing filename")
                else:
                    try: os.remove(args[1])
                    except Exception as e: print(f"rm error: {e}")
            elif cmd == "touch":
                if len(args) < 2:
                    print("touch: missing filename")
                else:
                    try: open(args[1], "a").close()
                    except Exception as e: print(f"touch error: {e}")
            elif cmd == "kill":
                if len(args) < 2:
                    print("kill: missing PID")
                else:
                    try:
                        pid = int(args[1])
                        os.kill(pid, signal.SIGTERM)
                        print(f"Process {pid} terminated")
                        for jid, jpid in list(jobs.items()):
                            if jpid == pid:
                                del jobs[jid]
                    except Exception as e:
                        print(f"kill error: {e}")

            elif cmd == "jobs":
                if not jobs:
                    print("No background jobs")
                else:
                    for jid, pid in jobs.items():
                        try:
                            result = os.waitpid(pid, os.WNOHANG)
                            if result[0] == 0:
                                print(f"[{jid}] PID:{pid} Running")
                            else:
                                print(f"[{jid}] PID:{pid} Finished")
                        except ChildProcessError:
                            print(f"[{jid}] PID:{pid} Finished")

            elif cmd == "fg":
                if len(args) < 2:
                    print("fg: missing job id")
                else:
                    try:
                        jid = int(args[1])
                        if jid not in jobs:
                            print("fg: No such job")
                        else:
                            pid = jobs[jid]
                            print(f"Bringing job [{jid}] to foreground")
                            os.waitpid(pid, 0)
                            del jobs[jid]
                    except Exception as e:
                        print(f"fg error: {e}")

            elif cmd == "bg":
                if len(args) < 2:
                    print("bg: missing job id")
                else:
                    try:
                        jid = int(args[1])
                        if jid not in jobs:
                            print("bg: No such job")
                        else:
                            pid = jobs[jid]
                            print(f"Job [{jid}] running in background PID {pid}")
                    except Exception as e:
                        print(f"bg error: {e}")

            elif cmd == "sched_help":
                print_scheduler_help()
            elif cmd == "sched_reset":
                scheduler.reset()
                print("Scheduler state cleared.")
            elif cmd == "rr_add":
                if len(args) != 3: print("Usage: rr_add <name> <burst_time>")
                else:
                    try:
                        name, burst = args[1], int(args[2])
                        if burst <= 0: print("burst_time must be > 0")
                        else: scheduler.add_rr_process(name, burst)
                    except ValueError: print("burst_time must be an integer")
            elif cmd == "rr_show":
                scheduler.show_rr_queue()
            elif cmd == "rr_run":
                if len(args) != 2: print("Usage: rr_run <quantum>")
                else:
                    try:
                        quantum = int(args[1])
                        if quantum <= 0: print("quantum must be > 0")
                        else: scheduler.run_round_robin(quantum)
                    except ValueError: print("quantum must be an integer")
            elif cmd == "prio_add":
                if len(args) != 4: print("Usage: prio_add <name> <burst_time> <priority>")
                else:
                    try:
                        name, burst, priority = args[1], int(args[2]), int(args[3])
                        if burst <= 0: print("burst_time must be > 0")
                        else: scheduler.add_priority_process(name, burst, priority)
                    except ValueError: print("burst_time and priority must be integers")
            elif cmd == "prio_show":
                scheduler.show_priority_queue()
            elif cmd == "prio_run":
                scheduler.run_priority_preemptive()
            elif cmd == "sched_completed":
                scheduler.show_completed()

            # --- THE ONLY MODIFICATION: Triggering the Deliverable 3 function ---
            elif cmd == "demo":
                run_deliverable_3_demo()

            else:
                background = False
                if args[-1] == "&":
                    background = True
                    args = args[:-1]
                execute_command(args, background)

        except KeyboardInterrupt:
            print("\nCtrl+C detected")
        except Exception as e:
            print(f"Shell error: {e}")

if __name__ == "__main__":
    print("Advanced OS Shell Simulation Loaded.")
    print("Type 'sched_help' to see available commands, or 'demo' to run the Memory/Sync tests.")
    run_shell()
