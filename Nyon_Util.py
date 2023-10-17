from datetime import datetime, timezone

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