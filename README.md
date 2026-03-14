# 💻 Advanced OS Shell Simulation: User Guide

Welcome to the Advanced OS Shell Simulation! This project (`integrated.py`) is a custom command-line interface that not only executes standard shell commands but also simulates core Operating System concepts, including **Job Control**, **CPU Scheduling** (Round-Robin & Priority), **Memory Management** (Paging), and **Process Synchronization** (Producer-Consumer).

Follow this step-by-step guide to explore all the features of the shell.

## 🚀 Getting Started

To launch the shell, open your terminal and run the Python script:

```bash
python3 integrated.py
```

*You will see the welcome message:*
> `Advanced OS Shell Simulation Loaded.`  
> `Type 'sched_help' to see available commands, or 'demo' to run the Memory/Sync tests.`  
> `myshell>`

---

## Step 1: Background Processes and Job Control

The shell can run standard system commands and manage background tasks.

1. **Start a background process:** Use the `&` operator to run commands in the background.
   ```bash
   myshell> sleep 120 &
   [1] started with PID 10488
   myshell> sleep 120 &
   [2] started with PID 10489
   ```

2. **List running jobs:** Check active background processes.
   ```bash
   myshell> jobs
   [1] PID:10488 Running
   [2] PID:10489 Running
   ```

3. **Kill a process:** Terminate a process using its PID.
   ```bash
   myshell> kill 10488
   Process 10488 terminated
   ```

4. **Resume a job in the background:** Use the `bg` command with the job ID.
   ```bash
   myshell> bg 2
   Job [2] running in background PID 10489
   ```

*(You can also run standard foreground commands like `touch sample.txt` or `echo hello_world`!)*

---

## Step 2: Round-Robin (RR) CPU Scheduling Simulation

Simulate a time-sharing system where processes are given a fixed time slice (quantum) to execute.

1. **Clear the scheduler:** Ensure you are starting with a clean slate.
   ```bash
   myshell> sched_reset
   ```

2. **Add processes to the RR queue:** Syntax is `rr_add <Process_Name> <Burst_Time>`.
   ```bash
   myshell> rr_add P1 4
   myshell> rr_add P2 6
   myshell> rr_add P3 3
   ```

3. **View the queue:**
   ```bash
   myshell> rr_show
   ```

4. **Run the Round-Robin Scheduler:** Provide a time quantum (e.g., 2).
   ```bash
   myshell> rr_run 2
   ```
   *The shell will output a detailed, step-by-step execution log showing context switches, remaining burst times, and final performance metrics (Average Waiting, Turnaround, and Response Times).*

---

## Step 3: Preemptive Priority CPU Scheduling Simulation

Simulate an environment where processes are executed based on priority (lower number = higher priority), and can preempt currently running processes.

1. **Add priority processes:** Syntax is `prio_add <Process_Name> <Burst_Time> <Priority>`.
   ```bash
   myshell> prio_add P1 5 3
   myshell> prio_add P2 3 1
   myshell> prio_add P3 4 2
   ```

2. **View the queue:**
   ```bash
   myshell> prio_show
   ```

3. **Run the Priority Scheduler:**
   ```bash
   myshell> prio_run
   ```
   *You will see the scheduler execute `P2` (Priority 1) first, followed by `P3` (Priority 2), and finally `P1` (Priority 3), along with the resulting performance metrics.*

---

## Step 4: Memory Management & Synchronization Demo

The shell includes a built-in automated demo to showcase advanced OS concepts. Simply type the `demo` command to watch the OS handle:

```bash
myshell> demo 
```

1. **Memory Management (Paging):** * The system will simulate a scenario with limited memory frames.
   * It runs a **FIFO (First-In-First-Out)** page replacement algorithm, displaying page faults.
   * It then runs an **LRU (Least Recently Used)** page replacement algorithm to compare page fault counts.

2. **Process Synchronization:**
   * Demonstrates the classic **Producer-Consumer** problem.
   * Shows a producer generating items and adding them to a shared buffer, while a consumer safely removes them, preventing race conditions.

---

## Step 5: Built-in Error Handling
