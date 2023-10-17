from datetime import datetime, timezone
import inspect

def expires_in(target_datetime):
    # Calculate the time difference
    time_diff = target_datetime - datetime.now().astimezone(timezone.utc)
    
    # Extract days, hours, and minutes from timedelta
    days = time_diff.days
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Construct a readable representation
    parts = []
    if days:
        parts.append(f"{days} days")
    if hours:
        parts.append(f"{hours} hours")
    if minutes:
        parts.append(f"{minutes} minutes")

    # Combine the parts into the final string
    return " ".join(parts)

def get_custom_logger_name():
    # Get the current frame
    frame = inspect.currentframe()

    # Go back to the calling frame
    frame = frame.f_back

    # Extract information
    module_name = frame.f_globals["__name__"]
    class_name = frame.f_locals.get("self", None).__class__.__name__ if "self" in frame.f_locals else None
    function_name = frame.f_code.co_name

    # Construct the logger name
    logger_name = f"AutoBrad.{module_name}"
    if class_name:
        logger_name += f".{class_name}"
    if function_name != "<module>":  # Avoid appending for module-level calls
        logger_name += f".{function_name}"

    return logger_name
