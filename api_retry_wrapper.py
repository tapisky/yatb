#!/usr/bin/env python3
import traceback
import time

from functools import wraps

class RetryWrapper:
    def __init__(self, retries, retry_wait_seconds=2):
        self.retries = retries
        self.retry_wait_seconds = retry_wait_seconds

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = None
            logger = None
            if args:
                logger = args[0]
            for _ in range(self.retries):
                try:
                    result = fn(*args, **kwargs)
                    break
                except:
                    if logger:
                        logger.info(traceback.format_exc())
                        logger.info(f"Retrying after {self.retry_wait_seconds} seconds")
                    else:
                        print(traceback.format_exc())
                        print(f"Retrying after {self.retry_wait_seconds} seconds")
                    time.sleep(self.retry_wait_seconds)
            return result
        return wrapper
