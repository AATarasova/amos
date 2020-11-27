from scipy.stats import uniform, expon,triang
import matplotlib
# Для сохранения в файл
matplotlib.use('Agg')
import matplotlib.pyplot as plt


from queue import Queue # и очередь, и стек, но нам нужна только очередь
# обычная очередь синхронизированная, блокирующая -- нам эти сложности ни к чему

from time import sleep 

import threading 
import sched, time

import req
import queue_analize
import distribution

NUMBER_1 		= 1000
NUMBER_2		= 40000
RHO_1			= 0.55
RHO_2	 		= 0.9
LAMBDA_IN		= 5
QUEUE_LEN		= NUMBER_1 + 1000


processing_system = queue_analize.QueuingSystem(QUEUE_LEN, rho=RHO_2, lamb=LAMBDA_IN, number=NUMBER_2)
processing_system.run(distribution.TypeDistribution.EXPONENTIAL, distribution.TypeDistribution.EXPONENTIAL)


print('rho, практ: ', processing_system.get_real_rho())
print('rho, практ: ', processing_system.get_generated_rho())

print('Максимальный размер очереди: ', 				processing_system.get_max_queue_len())
print('Средний размер очереди: ', 					processing_system.get_mean_queue_len())
print('Число заявок, обслуженных без очереди: ', 	processing_system.get_no_waiting_req_number())
print('Среднее время ожидания в очереди: ', 		processing_system.get_mean_waiting_time())

print('Коэффициент загрузки очереди: ', 			processing_system.get_load_factor(queue_analize.QueuingSystem.CharacterParam.TIME))
print('Среднее время обслуживания заявки: ', 		processing_system.get_mean_processing_time())

