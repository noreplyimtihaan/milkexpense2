from django.shortcuts import render, redirect
from django.contrib import messages
from milkapp.models import userProfileModel, milkShiftNameModel, updateMilkEntryModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import date as date_cls, datetime
from milkapp.utility import *
import json
from django.http import JsonResponse
from django.db.models import ExpressionWrapper, F, FloatField, Sum




VALID_ENTRY_STATES = {"Present", "Absent", None}
DASHBOARD_STATE_KEY = "dashboard_state"
UPDATE_STATE_KEY = "update_state"


def login(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or "").strip().lower()
        password = request.POST.get('password') or ""
        user = userProfileModel.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            request.session["user_id"] = user.id
            request.session["user_name"] = user.name
            return redirect('calendar')

        messages.error(request, "Invalid email or password.")
    return render(request, 'login.html')

def register(request): 
    if request.method == 'POST':
        name = (request.POST.get('name') or "").strip()
        email = (request.POST.get('email') or "").strip().lower()
        password = request.POST.get('password') or ""

        if not name or not email or not password:
            messages.error(request, "All fields are required")
            return redirect('register')

        if userProfileModel.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        user = userProfileModel(
            name=name,
            email=email,
            password=make_password(password)
        )
        user.save()
        return redirect('login')
        
    return render(request, 'register.html')


def calendar(request):
    user = get_current_user(request)
    if not user:
        return redirect("login")

    if not user.milk_shifts_name_model.exists():
        last_two = datetime.now().microsecond % 100
        milkShiftNameModel.objects.create(user=user, shift_name=f"Shift {last_two:02d}")

    user_milk_shifts = user.milk_shifts_name_model.order_by("created_at", "id")
    shifts = get_user_shift(user_milk_shifts)
    return render(request, "calendar.html", {"shifts": shifts, 'isCalendar': True})

def add_milk_shift(request):  
    if request.method == 'POST':
        user = get_current_user(request)
        if not user:
            return redirect("login")
        shift_name = (request.POST.get('shift_name') or "").strip()
        if shift_name:
            milkShiftNameModel.objects.create(user=user, shift_name=shift_name)
    return redirect('calendar')

def add_milk_entry(request):
    if request.method == 'POST':
        milk_date = request.POST.get('entry_date',None)
        milk_liter = request.POST.get('milk_liter',None)
        milk_price = request.POST.get('milk_price',None)
        shift_id = request.POST.get('shift_id')
        user_id = request.session.get("user_id")
       
        if not user_id:
            return redirect("login")
        
        user = userProfileModel.objects.get(id=user_id)
        milk_shift = milkShiftNameModel.objects.get(id=shift_id, user=user)
        milk_entry=updateMilkEntryModel.objects.get(user=user,milk_shift=milk_shift,date=milk_date)
        milk_entry.liter = float(milk_liter)
        milk_entry.price = float(milk_price)
        milk_entry.save()
        
    return redirect('calendar')


def get_milk_shifts(request,shift_id):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return JsonResponse({"error": "User not logged in."}, status=401)
    date = request.GET.get("date")
    
    try:
        user = userProfileModel.objects.get(id=user_id)
        milk_shift=milkShiftNameModel.objects.get(id=shift_id)
       
        milk_entry=updateMilkEntryModel.objects.filter(user=user,milk_shift=milk_shift,date=date).first()
        print(milk_entry)
        if milk_entry:
            return JsonResponse({
                "success": True,
                "default_price": milk_entry.price,
                "default_liter": milk_entry.liter
            })
        else:
            return JsonResponse({
                "success": False
            })
    except userProfileModel.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except:
        return JsonResponse({"error": "User not found."}, status=404)
    
def update_state(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "error": "POST required"}, status=405)

    user = get_current_user(request)
    if not user:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        data = json.loads(request.body)
        shift_id = data.get('shift_id')
        entry_date = datetime.strptime(data.get('date'), "%Y-%m-%d").date()
        new_state = data.get('status') or None
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request data"}, status=400)

    if new_state not in VALID_ENTRY_STATES:
        return JsonResponse({"success": False, "error": "Invalid state"}, status=400)

    try:
        milk_shift = milkShiftNameModel.objects.get(id=shift_id, user=user)
    except milkShiftNameModel.DoesNotExist:
        return JsonResponse({"success": False, "error": "Milk shift not found."}, status=404)

  
    updateMilkEntryModel.objects.update_or_create(
        user=user,
        milk_shift=milk_shift,
        date=entry_date,
        defaults={"state": new_state},
    )

    return JsonResponse({"success": True})

def get_month_states(request):
    user = get_current_user(request)
    if not user:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        shift_id = request.GET.get("shift_id")
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        start_date = date_cls(year, month, 1)
        end_date = date_cls(year + 1, 1, 1) if month == 12 else date_cls(year, month + 1, 1)
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid query data"}, status=400)

    try:
        shift = milkShiftNameModel.objects.get(id=shift_id, user=user)
    except milkShiftNameModel.DoesNotExist:
        return JsonResponse({"success": False, "error": "Milk shift not found."}, status=404)

    entries = updateMilkEntryModel.objects.filter(
        user=user,
        milk_shift=shift,
        date__gte=start_date,
        date__lt=end_date,
    ).only("date", "state")

    data = {}
    for entry in entries:
        key = f"{entry.date.year}-{entry.date.month-1}-{entry.date.day}"
        data[key] = entry.state

    return JsonResponse({
        "success": True,
        "states": data
    })



def dashboard(request):
    user = get_current_user(request)
    if not user:
        return redirect("login")

    user_milk_shifts = user.milk_shifts_name_model.order_by("created_at", "id")
    shifts = get_user_shift(user_milk_shifts)
    current_month, min_month = get_dashboard_month_bounds()

    if request.method == "POST":
        dashboard_action = request.POST.get("dashboard_action")
        selected_month = parse_dashboard_month(
            request.POST.get("dashboard_year"),
            request.POST.get("dashboard_month"),
            current_month,
            min_month,
        )

        if dashboard_action in {"prev_month", "next_month"}:
            step = -1 if dashboard_action == "prev_month" else 1
            selected_month = clamp_dashboard_month(
                shift_month(selected_month, step),
                current_month,
                min_month,
            )

        shift_by = request.POST.get("shift_by")
        selected_shift = None

        if shift_by:
            try:
                shift_id = int(shift_by)
            except (TypeError, ValueError):
                shift_id = None

            if shift_id:
                selected_shift = user_milk_shifts.filter(id=shift_id).first()

        if not selected_shift:
            selected_shift = user_milk_shifts.first()

        request.session[DASHBOARD_STATE_KEY] = {
            "year": selected_month.year,
            "month": selected_month.month,
            "shift_id": selected_shift.id if selected_shift else None,
        }
        request.session.pop("dashboard_year", None)
        request.session.pop("dashboard_month", None)
        request.session.pop("dashboard_shift_id", None)

        return redirect("dashboard")

    dashboard_state = request.session.pop(DASHBOARD_STATE_KEY, None)
    request.session.pop("dashboard_year", None)
    request.session.pop("dashboard_month", None)
    request.session.pop("dashboard_shift_id", None)

    if dashboard_state:
        selected_month = parse_dashboard_month(
            dashboard_state.get("year"),
            dashboard_state.get("month"),
            current_month,
            min_month,
        )
        selected_shift = user_milk_shifts.filter(id=dashboard_state.get("shift_id")).first()
    else:
        selected_month = current_month
        selected_shift = user_milk_shifts.first()

    if not selected_shift:
        selected_shift = user_milk_shifts.first()

    selected_shift_id = selected_shift.id if selected_shift else None
    selected_shift_name = selected_shift.shift_name if selected_shift else "No Shift Found"
    entries = updateMilkEntryModel.objects.none()
    total_liter = 0
    total_price = 0
    next_month = shift_month(selected_month, 1)

    if selected_shift:
        entries = (
            updateMilkEntryModel.objects
            .filter(
                user=user,
                state="Present",
                milk_shift=selected_shift,
                date__gte=selected_month,
                date__lt=next_month,
            )
            .select_related("milk_shift")
            .annotate(
                total_amount=ExpressionWrapper(
                    F("liter") * F("price"),
                    output_field=FloatField(),
                )
            )
            .order_by("-date", "-id")
        )

        totals = entries.aggregate(
            total_liter=Sum("liter"),
            total_price=Sum("total_amount"),
        )
        total_liter = totals["total_liter"] or 0
        total_price = totals["total_price"] or 0

    return render(
        request,
        'dashboard.html',
        {
            "shifts": shifts,
            "entries": entries,
            "selected_shift_id": selected_shift_id,
            "selected_shift_name": selected_shift_name,
            "selected_month": selected_month,
            "prev_month_disabled": selected_month <= min_month,
            "next_month_disabled": selected_month >= current_month,
            "total_liter": total_liter,
            "total_price": total_price,
        }
    )




def logout_view(request):
    # Clear the session data to log out the user
    request.session.flush()
    return redirect('login')  # Redirect to the login page after logout
