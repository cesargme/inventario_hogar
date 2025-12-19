from datetime import datetime, timedelta


def humanize_time(dt: datetime) -> str:
    """Convierte timestamp a formato humanizado (hace 2h, hace 3d, etc.)"""
    delta = datetime.utcnow() - dt

    if delta < timedelta(minutes=1):
        return "hace unos segundos"
    elif delta < timedelta(hours=1):
        minutes = delta.seconds // 60
        return f"hace {minutes}m"
    elif delta < timedelta(days=1):
        hours = delta.seconds // 3600
        return f"hace {hours}h"
    elif delta < timedelta(days=30):
        return f"hace {delta.days}d"
    elif delta < timedelta(days=365):
        months = delta.days // 30
        return f"hace {months} meses" if months > 1 else "hace 1 mes"
    else:
        years = delta.days // 365
        return f"hace {years} años" if years > 1 else "hace 1 año"
