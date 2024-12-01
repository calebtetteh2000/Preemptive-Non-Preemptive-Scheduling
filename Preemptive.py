import heapq
from dataclasses import dataclass
from typing import List

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int
    remaining_burst_time: int
    waiting_time: int = 0
    turnaround_time: int = 0
    completion_time: int = 0

class DynamicRoundRobinScheduler:
    def __init__(self, processes: List[Process], initial_quantum = 5):
        self.processes = sorted(processes, key=lambda p: p.arrival_time)
        self.initial_quantum = initial_quantum
        self.current_quantum = initial_quantum
        self.current_time = 0
        self.completed_processes = []
        self.gantt_chart = []

    def calculate_average_remaining_burst(self, active_processes):
        if not active_processes:
            return self.initial_quantum
        
        #dynamic quantum adjustment
        avg_burst = sum(p.remaining_burst_time for p in active_processes) / len(active_processes)
        new_quantum = max(2, min(int(avg_burst), 10))
        return new_quantum
    
    def run(self):
        #priority queue to manage processes
        ready_queue = []
        process_index = 0

        while process_index < len(self.processes) or ready_queue:
            #add newly arrives processes to ready_queue
            while (process_index < len(self.processes) and 
                   self.processes[process_index].arrival_time <= self.current_time):
                heapq.heappush(ready_queue, (self.processes[process_index].priority,
                                             self.processes[process_index].arrival_time,
                                             self.processes[process_index]))
                process_index += 1

            if not ready_queue:
                #if there's no process, advance time
                self.current_time += 1
                continue

            #get the highest priority process
            _, _, current_process = heapq.heappop(ready_queue)

            # Execute process for current quantum or remaining burst time
            execution_time = min(self.current_quantum, current_process.remaining_burst_time)

            #update process metrics
            current_process.remaining_burst_time -= execution_time
            self.current_time += execution_time

            #Update waiting time for processes in ready queue
            for _, _, p in ready_queue:
                if p != current_process:
                    p.waiting_time += execution_time

            #Record Gantt chart
            self.gantt_chart.append({
                'pid': current_process.pid,
                'start_time': self.current_time - execution_time,
                'end_time': self.current_time
            })

            #Check if process is complete
            if current_process.remaining_burst_time == 0:
                current_process.turnaround_time = (
                    self.current_time - current_process.arrival_time
                )
                self.completed_processes.append(current_process)
            else:
                #put process back to ready queue
                heapq.heappush(ready_queue, (current_process.priority,
                                             current_process.arrival_time,
                                             current_process))
                 
            #update quantum
            active_processes = [p for _, _, p in ready_queue]
            self.current_quantum = self.calculate_average_remaining_burst(active_processes)
            return self.analyze_performance()
        
    def analyze_performance(self):
        total_waiting_time = sum(p.waiting_time for p in self.completed_processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.completed_processes)

        total_execution_time = self.gantt_chart[-1]['end_time']

        #To calculate CPU utilization
        total_busy_time = sum(entry['end_time'] - entry['start_time'] for entry in self.gantt_chart)
        cpu_utilization = (total_busy_time / total_execution_time) * 100

        return {
            'total_waiting_time': total_waiting_time,
            'total_turnaround_time': total_turnaround_time,
            'cpu_utilization': cpu_utilization,
            'gantt_chart': self.gantt_chart
        }
    
    def print_gantt_chart(gantt_chart):
        print("\n--- Gantt Chart ---") 
        for entry in gantt_chart:
            print(f"Process {entry['pid']}: {entry['start_time']} - {entry['end_time']}")

def main():
    processes = [
        Process(pid=1, arrival_time=0, burst_time=10, remaining_burst_time=10, priority=1),
        Process(pid=2, arrival_time=1, burst_time=5, remaining_burst_time=5, priority=2),
        Process(pid=3, arrival_time=3, burst_time=8, remaining_burst_time=8, priority=3),
    ]

    scheduler = DynamicRoundRobinScheduler(processes)
    result = scheduler.run()

    print("\n--- Scheduling result ---")
    print(f"Total waiting time: {result['total_waiting_time']}")
    print(f"Total turnaround time: {result['total_turnaround_time']}")
    print(f"CPU utilization: {result['cpu_utilization']:.2f}%")

    DynamicRoundRobinScheduler.print_gantt_chart(result['gantt_chart'])

if __name__ == "__main__":
    main()