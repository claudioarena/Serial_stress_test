import serial.tools.list_ports
import serial
from pick import pick
import string
import time
import random
# def random_nonascii_unicode(length):
#    return u''.join(chr(random.randint(0x80, sys.maxunicode)) for _ in range(length))
# def random_unicode(length):
#    # Create a list of unicode characters within the range 0000-D7FF
#    random_unicodes = [chr(random.randrange(0xD7FF)) for _ in xrange(0, length)]
#    return u"".join(random_unicodes)


def get_random__string(length):
	characters = string.ascii_letters + string.digits + string.punctuation
	result_str = ''.join(random.choice(characters) for i in range(length))
	return result_str


class SerialStressTest:
	def __init__(self, max_length=64, default_baud=9600, verbose=False, verbose_send=False):
		self.max_length = max_length
		self.verbose = verbose
		self.verbose_send = verbose_send

		# List and ask to select available ports
		ports = serial.tools.list_ports.comports()
		ports_list = [port.device for port in sorted(ports)]
		ports_descriptions = [port.description for port in sorted(ports)]
		ports_verbose = [i + ' - ' + j for i, j in zip(ports_list, ports_descriptions)]

		title = 'Please select com port: '
		indicator = "=> "
		option, index = pick(ports_verbose, title, indicator=indicator)

		print('\nConnecting to ', ports_list[index], '...')

		self.ser = serial.Serial(ports_list[index])
		self.ser.timeout = 1
		self.ser.baudrate = default_baud
		self.ser.set_buffer_size(128, 128)
		time.sleep(0.5)
		self.ser.reset_output_buffer()
		self.ser.reset_input_buffer()
		print('Connected to ', self.ser.name, '\n')

	def __del__(self):
		self.ser.close()  # close port
		print('\nDisconnected port')

	# Should really be all possible UTF-8 combinations, but ok for now
	def check_message_send_receive(self, message):
		message = message.encode('utf-8')

		if len(message) > self.max_length:
			message = message[:self.max_length - 1] + message[-1:]

		if self.verbose_send:
			print('Testing by sending message ', message)

		tout = (len(message) / self.ser.baudrate) * 10 * 2
		if tout < 0.1:
			tout = 0.1
		self.ser.timeout = tout

		start_time = time.time()
		self.ser.write(message)
		received = self.ser.read(len(message))
		tot = (time.time() - start_time)

		if received == message:
			result = True
		else:
			result = False
			time.sleep(tout)
			self.ser.reset_output_buffer()
			self.ser.reset_input_buffer()
			time.sleep(tout)

		if self.verbose_send:
			print('Received: ', received)
			print('Result: ', result)
			print('Time needed: ')

		return result, tot

	def stress_test(self, baudrate, n, print_update=True):
		self.ser.baudrate = baudrate
		result = True
		print('---- Stress Test Start ----', '(baud rate: ', baudrate , ')')
		print('Expected time for completion:', (self.max_length / baudrate) * 10 * n, ' seconds')

		total_t = 0
		for i in range(0, n):
			message = get_random__string(self.max_length)
			res, t = self.check_message_send_receive(message)
			total_t = total_t + t
			if i % 10 == 0 and print_update:
				print('n: ', i)

			if res is False:
				print('Failed at n ', i)
				result = False

		print("--- %s seconds ---" % total_t)
		if result is True:
			print('All stress tests PASSED\n')
		else:
			print('Stress tests FAILED\n')

		return result

	def test_all_lengths(self):
		result = True
		print('----Test all lengths Start ----')

		total_t = 0
		for i in range(0, self.max_length + 1):
			message = get_random__string(i)
			res, t = self.check_message_send_receive(message)
			total_t = total_t + t

			if res is False:
				print('Failed at length ', i)
				result = False

			if i % 50 == 0:
				print('n: ', i)

		print("--- %s seconds ---" % total_t)

		if result is True:
			print('All length tests PASSED\n')
		else:
			print('Length tests FAILED\n')

		return result

	def test_baud_rates_very_low(self):
		baud_rate = [300, 600, 1200, 1800, 2400, 4800, 9600]
		return self.test_baud_rate(baud_rate)

	def test_baud_rates_low(self):
		baud_rate = [19200, 38400, 57600, 115200]
		return self.test_baud_rate(baud_rate)

	def test_baud_rates_high(self):
		baud_rate = [230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 3000000]
		return self.test_baud_rate(baud_rate)

	def test_baud_rate(self, rate_list):
		result = True

		for rate in rate_list:
			print('Testing baudrate ', rate)

			if rate < 19200:  # slow rate, just test a single length a few times
				result = self.stress_test(rate, 3) and result
			else:
				self.ser.baudrate = rate
				result = self.test_all_lengths() and result

		return result


if __name__ == '__main__':
	# Seems to work, up to a length of ~8256
	result_status = True

	s = SerialStressTest(max_length=128, default_baud=115200, verbose_send=False)
	s.check_message_send_receive("hello world")
	result_status = s.test_all_lengths() and result_status
	result_status = s.test_baud_rates_very_low() and result_status
	result_status = s.test_baud_rates_low() and result_status
	result_status = s.test_baud_rates_high() and result_status
	result_status = s.stress_test(115200, 1000) and result_status

	result_status = s.stress_test(115200, 100, print_update=False) and result_status
	result_status = s.stress_test(460800, 100, print_update=False) and result_status
	result_status = s.stress_test(500000, 100, print_update=False) and result_status
	result_status = s.stress_test(1000000, 100, print_update=False) and result_status
	result_status = s.stress_test(3000000, 100, print_update=False) and result_status

	if result_status is True:
		print('All tests run successfully')
	else:
		print('Some Tests failed')

