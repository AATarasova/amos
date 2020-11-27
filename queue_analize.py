from queue import Queue, SimpleQueue, Empty # обычная очередь синхронизированная, блокирующая


import threading 
import sched, time
import numpy as np
from enum import Enum

import req

import distribution
import time


class QueuingSystem:


	class CharacterParam(Enum):
		TIME 			= 0
		COUNT 			= 1


	def __init__(self, length_of_queue, rho, number, lamb):
		self._queue_len 		= length_of_queue
		self._rho				= rho
		self._number 			= number
		self._lambda			= lamb

		self.no_waiting 		= 0
		self._max_len 			= 0
		self._len_sum 			= 0
		self.processed 			= 0
		self.empty_processing_count = 0

		self.real_try_proc_count = 0

		# Создание расписания:
		self.requests_shedule 	= sched.scheduler() # расписание добавления заявок в очередь
		self.processing_shedule = sched.scheduler() # расписание начала обработки заявок

		# Итак, сама очередь:
		self.requests_queue 	= SimpleQueue()		# объект очереди
		self.requests_arr 		= []				# массив заявок, он формируется при добавлении заявки в очередь 
		self.queue_len_arr 		= []				# массив из длин очереди, он формируется в момент вытаскивания заяки из очереди


	# Создание массива со временем добавления заявок в очередь:
	def generate_input_time_array (self, distr: distribution.TypeDistribution):
		self._in_time_arr 		= distribution.generate_time_array(distr, self._number, self._rho, self._lambda)

	def generate_input_time_array_special (self, distr: distribution.TypeDistribution, param = 0, a = 0, b = 0, c = 0):
		self._in_time_arr 		= distribution.generate_time_array_special(distr, self._number, param, a, b, c)	

	# Создание массива со временем начала обработки заявок:
	def generate_output_time_array (self, distr: distribution.TypeDistribution, number = 0):
		if number == 0:
			number = self._number
		self._out_time_arr 		= distribution.generate_time_array(distr, number, self._rho, self._lambda)

	def generate_output_time_array_special (self, distr: distribution.TypeDistribution, number = 0, param = 0, a = 0, b = 0, c = 0):
		if number == 0:
			number = self._number
		self._out_time_arr 		= distribution.generate_time_array_special(distr, number, param, a, b, c)	

	def add_in_fifo(self):
		self.requests_arr.append(req.Req())
		if self.requests_queue.empty():
			self.no_waiting = self.no_waiting + 1
		self.requests_queue.put(self.requests_arr[len(self.requests_arr) - 1])
	

	def get_from_fifo(self):
		cur_time = self.test_get_time()
		self.queue_len_arr.append(self.requests_queue.qsize())
		
		cur_req = self.requests_queue.get()
		cur_req.start_processing()
		# наверное, тут нужны какие-то действия по обработке, но их нет
		# мб чего-нибудь посчитать для заявки надо? Добавить вычисление времени ожидания?
		# но вообще подсчёты вынесены отсюда
		cur_req.set_time_tmp(cur_time)
		self.processed = self.processed  + 1

	

	def get_from_fifo_non_blocking(self):

		while self.req_thread.isAlive():
			self.queue_len_arr.append(self.requests_queue.qsize())
			if not self.requests_queue.empty():
				cur_req = self.requests_queue.get()
				cur_req.start_processing()
				
				self.processed = self.processed  + 1

			else:
				self.empty_processing_count = self.empty_processing_count  + 1
		

	# функция для потока, который добавляет в очередь заявки:
	def generate_requests(self):

		for time in self._in_time_arr:
			self.requests_shedule.enter   (delay=time, priority=1,action= self.add_in_fifo, argument=())
		self.requests_shedule.run()

	# функция для потока, который вытаскивает заявки из очереди:
	def processing(self):
		for time in self._out_time_arr:
			self.processing_shedule.enter (delay=time,  priority=1, action=self.get_from_fifo, argument=())
		self.processing_shedule.run()
	def processing_non_blocking(self):
		for time in self._out_time_arr:
			self.processing_shedule.enter (delay=time,  priority=1, action=self.get_from_fifo_non_blocking, argument=())
		self.processing_shedule.run()

	def testing_queue_len(self, interval):
		while self.req_thread.isAlive():
			time.sleep(interval)
			current_len = self.requests_queue.qsize()
			self._max_len = current_len if current_len > self._max_len else self._max_len
			self._len_sum = self._len_sum + current_len
			print(current_len, end=", ")



	# Запуск очереди
	def run(self, requests_distribution, processing_distribution):
		self.generate_input_time_array_special(distr = requests_distribution, param = self._lambda)
		self.generate_output_time_array(distr = processing_distribution, number= 8*self._number)
		#self.generate_output_time_array(distr = processing_distribution)
		
		testing_interval = self._in_time_arr.mean() 
		print(testing_interval)
		self._init_time = time.monotonic()

		self.req_thread 	= threading.Thread(target=self.generate_requests, args=())
		self.proc_thread 	= threading.Thread(target=self.processing_non_blocking, args=())
		#self.proc_thread 	= threading.Thread(target=self.processing, args=())
		test_len_thread 	= threading.Thread(target=self.testing_queue_len, args=(testing_interval,))

		self.proc_thread.start()
		time.sleep(testing_interval)
		self.req_thread.start()
		test_len_thread.start()

		self.req_thread.join()
		self.proc_thread.join()

		#print(threading.active_count())
		print("Обработанных заявок: ", self.processed )

	# rho практическое:
	def get_generated_rho(self):
		return self._out_time_arr.mean() / self._in_time_arr.mean()

	def test_get_time(self):
		return time.monotonic()

	# rho практическое:
	def get_real_rho(self):

		req_time 	= 0 # сумма в секундах времен генерации запросов от запуска программы
		proc_time	= 0 # сумма в секундах времен начала обработки от запуска программы
		tmp = 0
		for cur_req in self.requests_arr:
			req_time 	= req_time  + cur_req.get_generating_time()       - self._init_time
			proc_time 	= proc_time + cur_req.get_start_processing_time() - self._init_time
			tmp = tmp + cur_req.get_finish_processing_time() - self._init_time
		print('Запланировано для выхода: ', self._out_time_arr.mean(), ' по факту ', tmp / self._number)

		return proc_time / req_time


	# Подсчёт среднего времени обработки в очереди:
	def get_mean_processing_time(self):
		all_processing_time = 0
		previous_processing_start = self._init_time
		
		for cur_req in self.requests_arr:
			all_processing_time = all_processing_time + cur_req.get_start_processing_time() - previous_processing_start

		return all_processing_time / len(self.requests_arr)


	# Подсчёт среднего времени ожидания в очереди:
	def get_mean_waiting_time(self):
		all_waiting_time = 0

		for cur_req in self.requests_arr:
			all_waiting_time = all_waiting_time + cur_req.get_waiting_time()

		return all_waiting_time / len(self.requests_arr)


	# Подсчёт среднего размера очереди:
	def get_mean_queue_len(self):
		all_queue_len = 0
		print('mean = ', self._len_sum / len(self.requests_arr))

		for length in self.queue_len_arr:
			all_queue_len = all_queue_len + length
		return all_queue_len / len(self.queue_len_arr)

	
	# Максимальный размер очереди:
	def get_max_queue_len(self):
		print('max = ', self._max_len)

		return max(self.queue_len_arr)


	# Число заявок, обслуженных без очереди:
	def get_no_waiting_req_number(self):
		count = 0

		for cur_req in self.requests_arr:
			if cur_req.is_no_wait_in_queue():
				count = count + 1

		print( count)
		return self.no_waiting

	# Коэффициент загруженности очереди:
	def get_load_factor(self, param : CharacterParam):
		# по времени:
		flag = False
		free_time_counter = 0
		
		# мб надо заменить на время окончания обработки заявки:
		finising_time 			= self.requests_arr[len(self.requests_arr) - 1].get_start_processing_time() 

		if param == self.CharacterParam.TIME:
			for cur_req in self.requests_arr:
				if (not flag) and cur_req.is_no_wait_in_queue():
					flag = True
					mark = cur_req.get_generating_time()

				elif flag and not cur_req.is_no_wait_in_queue():
					flag = False
					free_time_counter = free_time_counter + cur_req.get_generating_time() - mark		
		
			all_working_time = finising_time - self._init_time

			return (all_working_time - free_time_counter) // all_working_time

		else:
			# по числу заявок без очереди:
			return self.get_no_waiting_req_number() / self._number	




			