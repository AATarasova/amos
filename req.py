import time # время в секундах,
# monotic -- следующее значение гарантиированно больше предыдущего

class Req:
	def __init__(self):
		self.generating_time		= time.monotonic()
		self.in_queue_time			= -1.0
		self.start_processing_time	= -1.0
		self.end_processing_time	= -1.0

# Ставим метки времени:
	# Добавление в очередь - поступление заявки в очередь:
	def add_in_queue(self):
		self.in_queue_time 			= time.monotonic()

	# Вывод заяки из очереди - начало обработки:
	def start_processing(self):
		self.start_processing_time	= time.monotonic()

	# Окончание обработки заявки:
	def finish_processing(self):
		self.end_processing_time	= time.monotonic()

	# Окончание обработки заявки:
	def set_time_tmp(self, time_mark):
		self.end_processing_time	= time_mark
	

# Получаем информацию:
	# Получаем время обрааботки заявки - от выхода из очереди ожидания до окончания выполнения действий:
	def get_processing_time(self):
		return self.end_processing_time - self.start_processing_time

	# Получаем время выхода заявки из очереди - начала обработки:
	def get_start_processing_time(self):
		return self.start_processing_time

	# Получаем время создания заявки:
	def get_generating_time(self):
		return self.generating_time
		
	# Получаем время ожидания заявки в очереди:	
	def get_waiting_time(self):
		return self.start_processing_time - self.generating_time

	# Поступила ли заявка на обработку сразу (с заданной погрешностью)
	def is_no_wait_in_queue(self, err = 0.0001):
		return abs(self.start_processing_time - self.generating_time) < err

	# Получаем время создания заявки:
	def get_finish_processing_time(self):
		return self.generating_time