import phonenumbers
from phonenumbers import carrier, geocoder, timezone


def run_phonenumbers(phone: str, timeout: int = 15) -> dict:
    try:
        parsed = phonenumbers.parse(phone, None)
        is_valid = phonenumbers.is_valid_number(parsed)
        country_code = parsed.country_code
        national_number = parsed.national_number
        location = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en")
        tz = timezone.time_zones_for_number(parsed)
        country = phonenumbers.region_code_for_number(parsed)

        return {
            "status": "success",
            "phone": phone,
            "valid": is_valid,
            "country_code": country_code,
            "national_number": national_number,
            "country": country,
            "location": location,
            "carrier": carrier_name or "unknown",
            "timezones": list(tz),
            "formatted_international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "formatted_national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "number_type": phonenumbers.PhoneNumberType.to_string(phonenumbers.number_type(parsed)) if is_valid else "unknown",
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
