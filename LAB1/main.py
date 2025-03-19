import simpy
import numpy as np
import matplotlib.pyplot as plt


def simulate_mm1_queue(lambda_, mu, simulation_time):
    env = simpy.Environment()
    stats = {
        'total': 0,
        'served': 0,
        'lost': 0,
        'busy_time': 0.0
    }

    resource = simpy.Resource(env, capacity=1)

    def generate_requests():
        while True:
            yield env.timeout(np.random.exponential(1 / lambda_))
            stats['total'] += 1

            req = resource.request()
            result = yield req | env.timeout(0)

            if req in result:
                stats['served'] += 1
                env.process(process_request(req))
            else:
                stats['lost'] += 1
                req.cancel()

    def process_request(req):
        start_time = env.now
        try:
            yield env.timeout(np.random.exponential(1 / mu))
        finally:
            stats['busy_time'] += env.now - start_time
            resource.release(req)

    env.process(generate_requests())
    env.run(until=simulation_time)

    p_loss_theory = lambda_ / (lambda_ + mu)
    utilization_theory = lambda_ / (lambda_ + mu)

    return {
        'total': stats['total'],
        'served': stats['served'],
        'lost': stats['lost'],
        'p_loss_exp': stats['lost'] / (stats['served'] + stats['lost']),
        'p_loss_theory': p_loss_theory,
        'utilization_exp': stats['busy_time'] / simulation_time,
        'utilization_theory': utilization_theory
    }


lambda_ = 5  # Интенсивность входящего потока
mu = 6  # Интенсивность обслуживания
simulation_time = 48

results = simulate_mm1_queue(lambda_, mu, simulation_time)

print("Результаты эксперимента:")
print(f"Всего заявок: {results['total']}")
print(f"Обслужено: {results['served']}")
print(f"Потеряно: {results['lost']}")
print(f"Вероятность отказа (эксп.): {results['p_loss_exp']:.4f}")
print(f"Вероятность отказа (теор.): {results['p_loss_theory']:.4f}")
print(f"Коэффициент загрузки (эксп.): {results['utilization_exp']:.4f}")
print(f"Коэффициент загрузки (теор.): {results['utilization_theory']:.4f}")

lambdas = np.arange(1, 15, 1)
mu_fixed = 6
results_list = [simulate_mm1_queue(l, mu_fixed, simulation_time) for l in lambdas]

p_loss_exp = [res['p_loss_exp'] for res in results_list]
p_loss_theory = [res['p_loss_theory'] for res in results_list]
util_exp = [res['utilization_exp'] for res in results_list]
util_theory = [res['utilization_theory'] for res in results_list]

plt.figure(figsize=(12, 6))
plt.plot(lambdas, p_loss_exp, 'bo-', label='Экспериментальная')
plt.plot(lambdas, p_loss_theory, 'r--', label='Теоретическая')
plt.xlabel('Интенсивность входящего потока (λ)')
plt.ylabel('Вероятность отказа')
plt.title('Зависимость вероятности отказа от интенсивности входящего потока')
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(lambdas, util_exp, 'go-', label='Экспериментальная')
plt.plot(lambdas, util_theory, 'r--', label='Теоретическая')
plt.xlabel('Интенсивность входящего потока (λ)')
plt.ylabel('Коэффициент загрузки')
plt.title('Зависимость коэффициента загрузки от интенсивности входящего потока')
plt.legend()
plt.grid(True)
plt.show()
