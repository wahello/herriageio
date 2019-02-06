from threading import local

my_local_global = local()

class MultiAuthMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def process_request(self, request):
		print('entered processing')
		my_local_global['database_name'] = get_database_name(request)
		
