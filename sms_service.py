import os
import re
from typing import Optional

try:
    from twilio.rest import Client  # type: ignore
    from twilio.base.exceptions import TwilioRestException  # type: ignore
except Exception:
    Client = None  # Allows the app to import even if dependency missing; runtime will warn
    TwilioRestException = Exception


def _get_env():
    """Fetch Twilio-related env vars on-demand to avoid import-order issues."""
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    phone = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
    messaging_service_sid = os.getenv("TWILIO_MESSAGING_SERVICE_SID", "").strip()
    testing = os.getenv("SMS_TESTING_MODE", "false").lower() in ("1", "true", "yes", "y")
    return sid, token, phone, testing, messaging_service_sid


def _twilio_configured() -> bool:
    sid, token, phone, _, _ = _get_env()
    return bool(sid and token and phone)


def _get_client() -> Optional[Client]:
    sid, token, _, testing, _ = _get_env()
    if testing:
        return None
    if Client is None:
        print("Twilio client library not installed. Please add 'twilio' to requirements and install.")
        return None
    if not _twilio_configured():
        print("Twilio credentials not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER.")
        return None
    try:
        return Client(sid, token)
    except Exception as e:
        print(f"Failed to initialize Twilio client: {e}")
        return None


def format_phone(number: str, default_country: str = "+91") -> str:
    """Return an E.164 phone number. Adds default country code if 10-digit local number.
    - Keeps leading '+' if already present
    - Strips non-digits otherwise
    """
    if not number:
        return ""
    original = str(number).strip()
    if original.startswith('+'):
        # Very basic validation; Twilio will enforce correctness
        return original
    # Remove non-digits
    digits = re.sub(r"\D", "", original)
    # Handle '00' international prefix
    if digits.startswith('00'):
        digits = digits[2:]
    # Handle common Indian local format with leading 0 (e.g., 09876543210)
    if len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
    # Handle 12-digit starting with country code 91 (e.g., 919876543210)
    if len(digits) == 12 and digits.startswith('91'):
        return f"+{digits}"
    # Indian local 10-digit assumption
    if len(digits) == 10:
        return f"{default_country}{digits}"
    # Fallback: prefix '+'
    return f"+{digits}"


def send_sms(to_phone: str, message: str) -> bool:
    """Send an SMS using Twilio. Returns True if queued/simulated, False otherwise.
    Respects SMS_TESTING_MODE to avoid real sends in dev.
    """
    try:
        to_e164 = format_phone(to_phone)
        if not to_e164:
            print("SMS not sent: invalid or empty recipient phone number")
            return False
        if not message or not message.strip():
            print("SMS not sent: empty message body")
            return False

        # Get latest env configuration
        sid, token, from_number, testing, msg_service = _get_env()

        # Testing mode: log only
        if testing:
            print("\n" + "=" * 50)
            print(f"SMS SIMULATION - Would send to: {to_e164}")
            if msg_service:
                print(f"Using Messaging Service SID: {msg_service}")
            else:
                print(f"From: {from_number or '(unset)'}")
            print(f"Message:\n{message}")
            print("=" * 50 + "\n")
            return True

        client = _get_client()
        if not client:
            return False

        params = {
            'body': message[:1000],  # Hard cap to keep messages within Twilio limits
            'to': to_e164,
        }
        if msg_service:
            params['messaging_service_sid'] = msg_service
        else:
            params['from_'] = from_number

        msg = client.messages.create(**params)
        print(f"✅ SMS queued: SID={msg.sid}, To={to_e164}")
        return True
    except TwilioRestException as e:
        # Log rich error info from Twilio
        try:
            print(f"❌ TwilioRestException: status={getattr(e, 'status', None)}, code={getattr(e, 'code', None)}")
            print(f"Message: {getattr(e, 'msg', str(e))}")
            if getattr(e, 'more_info', None):
                print(f"More info: {e.more_info}")
        except Exception:
            pass
        return False
    except Exception as e:
        print(f"❌ SMS send failed: {e}")
        return False
