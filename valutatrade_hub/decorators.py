# valutatrade_hub/decorators.py

import functools

from .logging_config import logger


def log_action(func):
    """
    Декоратор для логирования действий в use cases.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        method_name = func.__name__
        
        user_info = "guest"
        if hasattr(self, 'current_user') and self.current_user:
            user_info = (f"User(id={self.current_user.user_id}, "
                f"name={self.current_user.username})")

        safe_args = []
        for arg in args:
            if "password" in method_name.lower() and isinstance(arg, str):
                safe_args.append("****")
            else:
                safe_args.append(arg)

        try:
            result = func(self, *args, **kwargs)
            res_str = str(result)[:100] + "..." if result and \
                len(str(result)) > 100 else str(result)
            
            logger.info(f"SUCCESS {method_name} | Who: {user_info} | "
                f"Args: {safe_args} | Result: {res_str}")
            return result
        except Exception as e:
            logger.error(f"FAILED {method_name} | Who: {user_info} | "
                f"Args: {safe_args} | Error: {type(e).__name__}: {e}")
            raise e
    return wrapper