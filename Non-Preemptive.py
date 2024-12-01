import heapq
from sortedcontainers import SortedList

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.start_time = 0
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

class Interval:
    def __init__(self, start, end, process):
        self.start = start
        self.end = end
        self.process = process

    def __lt__(self, other):
        return self.start < other.start
    
    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

class IntervalTree:
    def __init__(self):
        self.intervals = SortedList()

    def insert(self, interval):
        self.intervals.add(interval)

    def delete(self, interval):
        self.intervals.remove(interval)

    def query(self, start_time):
        #Find the interval that starts after a given time
        index = self.intervals.bisect_left(Interval(start_time, float('inf'), None))
        if index == len(self.intervals):
            return None
        return self.intervals[index]
    
def sjf_scheduling(processes):
    ready_queue = []
    gantt_chart = []
    interval_tree = IntervalTree()
    time = 0
    max_starvation = 0

    # Sort processes by arrival time
    processes.sort(key=lambda x: x.arrival_time)

    # Initialize average waiting and turnaround times
    avg_waiting_time = 0
    avg_turnaround_time = 0
    completed_processes = []  # Track completed processes

    while processes or ready_queue:
        # Add newly arrived processes to ready queue
        while processes and processes[0].arrival_time <= time:
            process = processes.pop(0)
            interval = Interval(process.arrival_time, process.arrival_time + process.burst_time, process)  # Create interval
            interval_tree.insert(interval)

            heapq.heappush(ready_queue, (-process.priority, process.burst_time, process))

        # If ready queue is empty or idle
        if not ready_queue:
            time += 1
            continue

        # Select the next process to execute
        _, burst_time, current_process = heapq.heappop(ready_queue)
        interval_to_delete = interval_tree.query(current_process.arrival_time)  # Find interval by arrival time
        interval_tree.delete(interval_to_delete)

        # Update process information and interval object
        interval_to_delete.end = time + burst_time  # Update end time of the existing interval
        current_process.start_time = time
        current_process.completion_time = time + burst_time
        current_process.waiting_time = current_process.start_time - current_process.arrival_time
        current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
        max_starvation = max(max_starvation, current_process.waiting_time)
        time += burst_time

        # Append to gantt chart
        gantt_chart.append((current_process.pid, current_process.start_time, current_process.completion_time))

        # Add current process to completed processes
        completed_processes.append(current_process)

        # Update waiting time for processes in ready queue
        for _, _, waiting_process in ready_queue:
            waiting_process.priority += waiting_process.waiting_time // 10

    # Calculate average waiting and turnaround times
    if completed_processes:
        avg_waiting_time = sum(p.waiting_time for p in completed_processes) / len(completed_processes)
        avg_turnaround_time = sum(p.turnaround_time for p in completed_processes) / len(completed_processes)

    return {
        "Gantt_Chart": gantt_chart,
        "Average_Waiting_Time": avg_waiting_time,
        "Average_Turnaround_Time": avg_turnaround_time,
        "Maximum_Starvation_Time": max_starvation
    }

if __name__ == "__main__":
    processes = [
        Process(1, 3, 6, 4),
        Process(2, 1, 7, 1),
        Process(3, 2, 8, 7),
        Process(4, 6, 4, 5)
    ]

    print("Processes before scheduling:", [(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes])

    result = sjf_scheduling(processes)
    print("Gantt Chart: ", result["Gantt_Chart"])
    print("Average waiting time: ", result["Average_Waiting_Time"])
    print("Average turnaround time: ", result["Average_Turnaround_Time"])
    print("Maximum starvation time: ", result["Maximum_Starvation_Time"])