import math
import numpy as np
import matplotlib.pyplot as plt
import heapq
import random


def calculate_characteristics(lambd, mu, n):
    rho = lambd / (n * mu)
    if rho >= 1:
        return {
            'P0': 0,
            'P_queued': 1,
            'Lq': float('inf'),
            'Wq': float('inf'),
            'W': float('inf'),
            'rho': rho
        }

    sum_part = 0.0
    for k in range(n):
        sum_part += ((lambd / mu) ** k) / math.factorial(k)
    second_part = ((lambd / mu) ** n) / (math.factorial(n) * (1 - rho))
    P0 = 1 / (sum_part + second_part)

    numerator = ((lambd / mu) ** n) / math.factorial(n)
    denominator = (1 - rho)
    P_queued = (numerator / denominator) * P0

    Lq = (P_queued * rho) / (1 - rho)
    Wq = Lq / lambd
    W = Wq + (1 / mu)

    return {
        'P0': P0,
        'P_queued': P_queued,
        'Lq': Lq,
        'Wq': Wq,
        'W': W,
        'rho': rho
    }


def simulate_mmn_queue(lambd, mu, n, simulation_time):
    time = 0.0
    servers_busy = 0
    queue = []
    events = []

    total_customers = 0
    customers_served = 0
    customers_queued = 0
    total_waiting_time = 0.0
    total_queue_length = 0.0
    time_all_idle = 0.0
    last_event_time = 0.0

    first_arrival = random.expovariate(lambd)
    heapq.heappush(events, (first_arrival, 'arrival', None))

    while events:
        current_time, event_type, event_data = heapq.heappop(events)
        if current_time > simulation_time:
            break

        time_delta = current_time - last_event_time
        last_event_time = current_time

        if servers_busy == 0:
            time_all_idle += time_delta

        total_queue_length += len(queue) * time_delta

        if event_type == 'arrival':
            total_customers += 1
            arrival_time = current_time
            if servers_busy < n:
                servers_busy += 1
                service_time = random.expovariate(mu)
                heapq.heappush(events, (current_time + service_time, 'departure', (arrival_time, service_time)))
            else:
                queue.append(arrival_time)
                customers_queued += 1

            next_arrival = current_time + random.expovariate(lambd)
            if next_arrival <= simulation_time:
                heapq.heappush(events, (next_arrival, 'arrival', None))

        elif event_type == 'departure':
            customers_served += 1
            arrival_time, service_time = event_data
            waiting_time = (current_time - service_time) - arrival_time
            total_waiting_time += waiting_time

            if queue:
                next_arrival_time = queue.pop(0)
                service_time_next = random.expovariate(mu)
                heapq.heappush(events,
                               (current_time + service_time_next, 'departure', (next_arrival_time, service_time_next)))
            else:
                servers_busy -= 1

        time = current_time

    P0 = time_all_idle / simulation_time if simulation_time > 0 else 0
    P_queued = customers_queued / total_customers if total_customers > 0 else 0
    Lq = total_queue_length / simulation_time if simulation_time > 0 else 0
    Wq = total_waiting_time / customers_served if customers_served > 0 else 0
    W = Wq + (1 / mu) if mu != 0 else 0
    rho = (lambd / (n * mu)) if (n * mu) != 0 else 0

    return {
        'P0': P0,
        'P_queued': P_queued,
        'Lq': Lq,
        'Wq': Wq,
        'W': W,
        'rho': rho
    }


lambd = 10  # заявок/час
mu = 3  # заявок/час на канал
n = 4
simulation_time = 100000

# Теоретические расчеты
theoretical = calculate_characteristics(lambd, mu, n)

# Имитационное моделирование
simulated = simulate_mmn_queue(lambd, mu, n, simulation_time)

print("Теоретические характеристики при n=4, μ=3:")
for key, value in theoretical.items():
    print(f"{key}: {value:.4f}")

print("\nИмитационные характеристики при n=4, μ=3:")
for key, value in simulated.items():
    print(f"{key}: {value:.4f}")

print("\nСравнение результатов:")
print("{:<10} {:<15} {:<15} {:<10}".format('Характ.', 'Теория', 'Симуляция', 'Разница (%)'))
for key in theoretical:
    if key in simulated:
        th = theoretical[key]
        sim = simulated[key]
        diff = abs((th - sim) / th) * 100 if th != 0 else 0
        print("{:<10} {:<15.4f} {:<15.4f} {:<10.2f}%".format(key, th, sim, diff))

n_values = range(4, 11)
wq_theory = []
lq_theory = []
wq_sim = []
lq_sim = []

for n in n_values:
    # Теория
    chars = calculate_characteristics(lambd, mu, n)
    wq_theory.append(chars['Wq'])
    lq_theory.append(chars['Lq'])

    # Симуляция
    sim = simulate_mmn_queue(lambd, mu, n, simulation_time)
    wq_sim.append(sim['Wq'])
    lq_sim.append(sim['Lq'])

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(n_values, wq_theory, 'o-', label='Теория')
plt.plot(n_values, wq_sim, 'x--', label='Симуляция')
plt.xlabel('Количество каналов (n)')
plt.ylabel('Wq (часы)')
plt.title('Среднее время ожидания')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(n_values, lq_theory, 'o-', label='Теория')
plt.plot(n_values, lq_sim, 'x--', label='Симуляция')
plt.xlabel('Количество каналов (n)')
plt.ylabel('Lq (заявки)')
plt.title('Средняя длина очереди')
plt.legend()
plt.tight_layout()
plt.show()