import numpy as np
import heapq
import matplotlib.pyplot as plt

class Simulation:
    def __init__(self, lambda1, lambda2, mu):
        self.lambda1 = lambda1  # Интенсивность высокоприоритетных заявок
        self.lambda2 = lambda2  # Интенсивность низкоприоритетных заявок
        self.mu = mu            # Интенсивность обслуживания

        # Очереди для высокоприоритетных и низкоприоритетных заявок
        self.queue_high = []    # (время поступления, время обслуживания)
        self.queue_low = []

        # Статистика
        self.total_wait_high = 0.0  # Общее время ожидания для класса 1
        self.total_wait_low = 0.0   # Общее время ожидания для класса 2
        self.num_served_high = 0   # Количество обслуженных заявок класса 1
        self.num_served_low = 0    # Количество обслуженных заявок класса 2
        self.queue_wait_counts_high = 0  # Количество заявок класса 1, которые ждали в очереди
        self.queue_wait_counts_low = 0   # Количество заявок класса 2, которые ждали в очереди

        # События: (время, тип: 'arrival_high', 'arrival_low', 'service_completion')
        self.events = []
        self.current_time = 0.0
        self.server_busy = False    # Занят ли сервер

    def schedule_event(self, event_time, event_type):
        heapq.heappush(self.events, (event_time, event_type))

    def run(self, max_events):
        # Начальные события: первые заявки каждого класса
        first_arrival_high = np.random.exponential(1 / self.lambda1)
        self.schedule_event(first_arrival_high, 'arrival_high')
        first_arrival_low = np.random.exponential(1 / self.lambda2)
        self.schedule_event(first_arrival_low, 'arrival_low')

        event_count = 0
        while event_count < max_events and self.events:
            current_time, event_type = heapq.heappop(self.events)
            self.current_time = current_time

            if event_type == 'arrival_high':
                # Генерация следующей высокоприоритетной заявки
                next_arrival = current_time + np.random.exponential(1 / self.lambda1)
                self.schedule_event(next_arrival, 'arrival_high')
                # Обработка текущей заявки
                service_time = np.random.exponential(1 / self.mu)
                if self.server_busy:
                    self.queue_high.append((current_time, service_time))
                else:
                    self.server_busy = True
                    completion_time = current_time + service_time
                    self.schedule_event(completion_time, 'service_completion')
                    self.total_wait_high += 0  # Ожидания нет
                self.num_served_high += 1

            elif event_type == 'arrival_low':
                # Генерация следующей низкоприоритетной заявки
                next_arrival = current_time + np.random.exponential(1 / self.lambda2)
                self.schedule_event(next_arrival, 'arrival_low')
                # Обработка текущей заявки
                service_time = np.random.exponential(1 / self.mu)
                if self.server_busy:
                    self.queue_low.append((current_time, service_time))
                else:
                    self.server_busy = True
                    completion_time = current_time + service_time
                    self.schedule_event(completion_time, 'service_completion')
                    self.total_wait_low += 0  # Ожидания нет
                self.num_served_low += 1

            elif event_type == 'service_completion':
                # Выбор следующей заявки из очереди (сначала высокоприоритетные)
                if self.queue_high:
                    arrival_time, service_time = self.queue_high.pop(0)
                    wait_time = current_time - arrival_time
                    self.total_wait_high += wait_time
                    self.queue_wait_counts_high += 1
                    completion_time = current_time + service_time
                    self.schedule_event(completion_time, 'service_completion')
                elif self.queue_low:
                    arrival_time, service_time = self.queue_low.pop(0)
                    wait_time = current_time - arrival_time
                    self.total_wait_low += wait_time
                    self.queue_wait_counts_low += 1
                    completion_time = current_time + service_time
                    self.schedule_event(completion_time, 'service_completion')
                else:
                    self.server_busy = False

            event_count += 1

    def get_stats(self):
        stats = {
            'avg_wait1': self.total_wait_high / self.num_served_high if self.num_served_high > 0 else 0,
            'avg_wait2': self.total_wait_low / self.num_served_low if self.num_served_low > 0 else 0,
            'prob_wait1': self.queue_wait_counts_high / self.num_served_high if self.num_served_high > 0 else 0,
            'prob_wait2': self.queue_wait_counts_low / self.num_served_low if self.num_served_low > 0 else 0,
        }
        return stats

# Вариация λ1 при λ2=5, μ=10
lambda1_values = np.linspace(1, 4, 10)
lambda2 = 5
mu = 10
Wq1_theory_list = []
Wq2_theory_list = []
Wq1_sim_list = []
Wq2_sim_list = []

for lambda1 in lambda1_values:
    # Теоретические расчеты
    rho1 = lambda1 / mu
    rho2 = lambda2 / mu
    Wq1 = (lambda1 + lambda2) / (mu ** 2 * (1 - rho1))
    Wq2 = (lambda1 + lambda2) / (mu ** 2 * (1 - rho1 - 0.5) * (1 - rho1))
    Wq1_theory_list.append(Wq1)
    Wq2_theory_list.append(Wq2)

    # Симуляция
    sim = Simulation(lambda1, lambda2, mu)
    sim.run(1000000)
    stats = sim.get_stats()
    Wq1_sim_list.append(stats['avg_wait1'])
    Wq2_sim_list.append(stats['avg_wait2'])

print("Результаты симуляции:")
print(f"Среднее время ожидания (класс 1): {stats['avg_wait1']:.3f} ч")
print(f"Среднее время ожидания (класс 2): {stats['avg_wait2']:.3f} ч")
print(f"Вероятность ожидания (класс 1): {stats['prob_wait1']:.2%}")
print(f"Вероятность ожидания (класс 2): {stats['prob_wait2']:.2%}")
plt.figure(figsize=(10, 6))
plt.plot(lambda1_values, Wq1_theory_list, label='Теория (Класс 1)')
plt.plot(lambda1_values, Wq1_sim_list, '--', label='Симуляция (Класс 1)')
plt.plot(lambda1_values, Wq2_theory_list, label='Теория (Класс 2)')
plt.plot(lambda1_values, Wq2_sim_list, '--', label='Симуляция (Класс 2)')
plt.xlabel('λ₁ (заявок/час)')
plt.ylabel('Среднее время ожидания (ч)')
plt.legend()
plt.title('Зависимость времени ожидания от интенсивности λ₁')
plt.grid(True)
plt.show()