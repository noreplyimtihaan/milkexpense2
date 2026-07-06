from milkapp.models import userProfileModel
from django.utils import timezone
from datetime import date as date_cls, datetime

def get_user_shift(user_milk_shifts):
    return [
        {
            "shift_id": shift.id,
            "name": shift.shift_name,
        }
        for shift in user_milk_shifts
    ]

def get_month_start(year, month):
    return date_cls(year, month, 1)


def shift_month(month_start, step):
    month_index = month_start.month - 1 + step
    year = month_start.year + month_index // 12
    month = month_index % 12 + 1
    return date_cls(year, month, 1)


def clamp_dashboard_month(month_start, current_month, min_month):
    if month_start > current_month:
        return current_month
    if month_start < min_month:
        return min_month
    return month_start


def get_dashboard_month_bounds():
    today = timezone.localdate()
    current_month = get_month_start(today.year, today.month)
    min_month = shift_month(current_month, -5)
    return current_month, min_month


def parse_dashboard_month(year, month, current_month, min_month):
    try:
        selected_month = get_month_start(
            int(year),
            int(month),
        )
    except (TypeError, ValueError):
        selected_month = current_month

    return clamp_dashboard_month(selected_month, current_month, min_month)


def get_selected_shift(user_milk_shifts, shift_id):
    try:
        shift_id = int(shift_id)
    except (TypeError, ValueError):
        shift_id = None

    if shift_id:
        selected_shift = user_milk_shifts.filter(id=shift_id).first()
        if selected_shift:
            return selected_shift

    return user_milk_shifts.first()


def get_current_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return userProfileModel.objects.filter(id=user_id).first()