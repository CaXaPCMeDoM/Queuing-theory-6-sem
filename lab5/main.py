import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

LAMBDA = 10  # Интенсивность входящего потока (заявок/час)
MU = 3       # Интенсивность обслуживания одного агента (заявок/час)
SIM_TIME = 1000  # Время моделирования (часы)
MAX_AGENTS = 5   # Максимальное количество агентов
MIN_AGENTS = 1   # Минимальное количество агентов
ADD_AGENT_RATE = 1    # Интенсивность добавления агентов (агентов/час)
REMOVE_AGENT_RATE = 0.5  # Интенсивность удаления агентов (агентов/час)
MAX_QUEUE_LENGTH = 100   # Максимальная длина очереди

stats = {
    'generated': 0,
    'lost': 0,
    'served': 0,
    'total_time': 0.0,
    'queue_lengths': [],
    'active_agents': [],
}

class Request:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time

def request_generator(env, queue_requests, lambda_rate, max_queue_length, stats):
    while True:
        yield env.timeout(random.expovariate(lambda_rate))
        stats['generated'] += 1
        if len(queue_requests.items) < max_queue_length:
            request = Request(env.now)
            yield queue_requests.put(request)
        else:
            stats['lost'] += 1

def agent_process(env, agent_id, queue_requests, mu, stats):
    try:
        while True:
            request = yield queue_requests.get()
            service_start = env.now
            try:
                service_time = random.expovariate(mu)
                yield env.timeout(service_time)
                stats['total_time'] += (env.now - request.arrival_time)
                stats['served'] += 1
            except simpy.Interrupt:
                yield queue_requests.put(request)
                break
    except simpy.Interrupt:
        pass

def add_agent(env, active_agents, queue_requests, mu, max_agents):
    while True:
        yield env.timeout(random.expovariate(ADD_AGENT_RATE))
        if len(active_agents) < max_agents:
            agent_id = len(active_agents) + 1
            agent_proc = env.process(agent_process(env, agent_id, queue_requests, mu, stats))
            active_agents.append(agent_proc)

def remove_agent(env, active_agents, min_agents):
    while True:
        yield env.timeout(random.expovariate(REMOVE_AGENT_RATE))
        if len(active_agents) > min_agents:
            agent_proc = random.choice(active_agents)
            agent_proc.interrupt()
            active_agents.remove(agent_proc)

def monitor_queue(env, queue_requests, active_agents, stats):
    while True:
        stats['queue_lengths'].append(len(queue_requests.items))
        stats['active_agents'].append(len(active_agents))
        yield env.timeout(1.0)

env = simpy.Environment()
queue_requests = simpy.Store(env)
active_agents = []

# начальный агент
agent_proc = env.process(agent_process(env, 1, queue_requests, MU, stats))
active_agents.append(agent_proc)

env.process(request_generator(env, queue_requests, LAMBDA, MAX_QUEUE_LENGTH, stats))
env.process(add_agent(env, active_agents, queue_requests, MU, MAX_AGENTS))
env.process(remove_agent(env, active_agents, MIN_AGENTS))
env.process(monitor_queue(env, queue_requests, active_agents, stats))

env.run(until=SIM_TIME)

avg_time = stats['total_time'] / stats['served'] if stats['served'] > 0 else 0
avg_queue = np.mean(stats['queue_lengths'])
avg_agents = np.mean(stats['active_agents'])
loss_prob = stats['lost'] / stats['generated'] if stats['generated'] > 0 else 0

print(f"Среднее время пребывания: {avg_time:.2f} ч")
print(f"Средняя длина очереди: {avg_queue:.2f}")
print(f"Среднее число агентов: {avg_agents:.2f}")
print(f"Вероятность потерь: {loss_prob:.4f}")

plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(stats['active_agents'], label='Активные агенты')
plt.xlabel('Время (часы)')
plt.ylabel('Количество')
plt.subplot(2, 1, 2)
plt.plot(stats['queue_lengths'], label='Длина очереди')
plt.xlabel('Время (часы)')
plt.ylabel('Количество')
plt.tight_layout()
plt.show()