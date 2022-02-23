POWER_CUBIC = 3.0
POWER_QUARTIC = 4.0


def parse_number(text, errors_key, errors):
    try:
        value = int(str(text).strip())
    except ValueError:
        errors[errors_key] = "not-an-integer"
        return None
    if not value > 0:
        errors[errors_key] = "not-positive"
        return None
    return value


def validate(form):
    errors = {}

    x_cubic = parse_number(form.get("x-cubic"), "x-cubic", errors)
    y_cubic = parse_number(form.get("y-cubic"), "y-cubic", errors)
    z_cubic = parse_number(form.get("z-cubic"), "z-cubic", errors)

    if x_cubic is not None and y_cubic is not None and z_cubic is not None:
        if x_cubic ** POWER_CUBIC + y_cubic ** POWER_CUBIC != z_cubic ** POWER_CUBIC:
            errors["cubic"] = "not-a-counterexample"

    x_quartic = parse_number(form.get("x-quartic"), "x-quartic", errors)
    y_quartic = parse_number(form.get("y-quartic"), "y-quartic", errors)
    z_quartic = parse_number(form.get("z-quartic"), "z-quartic", errors)

    if x_quartic is not None and y_quartic is not None and z_quartic is not None:
        if x_quartic ** POWER_QUARTIC + y_quartic ** POWER_QUARTIC != z_quartic ** POWER_QUARTIC:
            errors["quartic"] = "not-a-counterexample"

    return errors
