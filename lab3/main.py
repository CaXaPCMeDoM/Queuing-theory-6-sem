import matplotlib.pyplot as plt
import heapq
import random


def calculate_metrics(lambd, mu, m):
    rho = lambd / mu
    if rho == 1:
        p_loss = 1 / (m + 2)
        L = (m + 1) / 2
        Lq = sum((k - 1) * (1 / (m + 2)) for k in range(1, m + 2))
        p0 = 1 / (m + 2)
    else:
        rho_m_plus_1 = rho ** (m + 1)
        denominator = 1 - rho ** (m + 2)
        p_loss = (1 - rho) * rho_m_plus_1 / denominator

        sum_L = sum(k * (1 - rho) * (rho ** k) / denominator for k in range(m + 2))
        L = sum_L

        Lq = sum((k - 1) * (1 - rho) * (rho ** k) / denominator for k in range(1, m + 2))

        p0 = (1 - rho) / denominator

    lambd_eff = lambd * (1 - p_loss)
    Wq = Lq / lambd_eff if lambd_eff != 0 else 0
    W = L / lambd_eff if lambd_eff != 0 else 0
    rho_effective = 1 - p0

    return {
        'P_loss': p_loss,
        'L': L,
        'Lq': Lq,
        'Wq': Wq,
        'W': W,
        'rho_effective': rho_effective
    }


def simulate_mm1m_queue(lambd, mu, m, simulation_time):
    time = 0.0
    queue = []
    server_busy = False
    events = []
    lost_customers = 0
    total_customers = 0
    total_waiting_time = 0.0
    total_queue_length = 0.0
    last_event_time = 0.0

    heapq.heappush(events, (random.expovariate(lambd), 'arrival'))

    while events:
        current_time, event_type = heapq.heappop(events)
        if current_time > simulation_time:
            break

        time_delta = current_time - last_event_time
        last_event_time = current_time
        total_queue_length += len(queue) * time_delta

        if event_type == 'arrival':
            total_customers += 1
            if len(queue) < m + 1:
                if server_busy:
                    queue.append(current_time)
                else:
                    server_busy = True
                    heapq.heappush(events, (current_time + random.expovariate(mu), 'departure'))
            else:
                lost_customers += 1

            next_arrival = current_time + random.expovariate(lambd)
            heapq.heappush(events, (next_arrival, 'arrival'))

        elif event_type == 'departure':
            if queue:
                arrival_time = queue.pop(0)
                waiting_time = current_time - arrival_time
                total_waiting_time += waiting_time
                heapq.heappush(events, (current_time + random.expovariate(mu), 'departure'))
            else:
                server_busy = False

    p_loss = lost_customers / total_customers if total_customers > 0 else 0
    Lq = total_queue_length / simulation_time if simulation_time > 0 else 0
    Wq = total_waiting_time / (total_customers - lost_customers) if (total_customers - lost_customers) > 0 else 0

    return {
        'P_loss': p_loss,
        'Lq': Lq,
        'Wq': Wq
    }


lambd = 8  # заявок в час
mu = 10  # заявок в час
max_m_to_test = 15
simulation_time = 100000  # часов

# Теоретические расчеты
m_values = list(range(0, max_m_to_test + 1))
theory_results = [calculate_metrics(lambd, mu, m) for m in m_values]

# Имитационные расчеты
sim_results = [simulate_mm1m_queue(lambd, mu, m, simulation_time) for m in m_values]

print("Сравнение теоретических и имитационных результатов:")
print("m | P_loss (теория) | P_loss (симуляция) | Wq (теория) | Wq (симуляция)")
for m in m_values:
    th = theory_results[m]
    sim = sim_results[m]
    print(f"{m:2} | {th['P_loss']:^15.4f} | {sim['P_loss']:^17.4f} | {th['Wq']:^11.4f} | {sim['Wq']:^12.4f}")

optimal_m_theory = next(m for m in m_values if theory_results[m]['P_loss'] <= 0.05)
optimal_m_sim = next(m for m in m_values if sim_results[m]['P_loss'] <= 0.05)

print(f"\nОптимальная длина очереди (теория): m={optimal_m_theory}")
print(f"Оптимальная длина очереди (симуляция): m={optimal_m_sim}")

plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(m_values, [res['P_loss'] for res in theory_results], 'o-', label='Теория')
plt.plot(m_values, [res['P_loss'] for res in sim_results], 'x--', label='Симуляция')
plt.axhline(0.05, color='r', linestyle='--', label='Порог 5%')
plt.xlabel('Длина очереди (m)')
plt.ylabel('Вероятность потерь')
plt.title('Вероятность потерь заявок')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(m_values, [res['Wq'] for res in theory_results], 'o-', label='Теория')
plt.plot(m_values, [res['Wq'] for res in sim_results], 'x--', label='Симуляция')
plt.xlabel('Длина очереди (m)')
plt.ylabel('Среднее время ожидания (часы)')
plt.title('Среднее время ожидания в очереди')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()