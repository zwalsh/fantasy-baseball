import time

def timed(logger):
    def translator(func):
        def translated(*args, **kwargs):
            logger.info(f'Starting execution of {func.__name__} with args {str(args):100.100}')
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.info(f'Execution of {func.__name__} finished after {end_time - start_time:.3f}s')
            return result
        return translated
    return translator


