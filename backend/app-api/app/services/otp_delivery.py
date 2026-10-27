"""Provider dispatch with backward-compatible char(64) challenge storage.
SHA256 hex = legacy local code; verify:VE... = external verification reference.
No schema change. Whitespace padding from PostgreSQL char(64) is stripped.
"""
from sqlalchemy import text
from app.mobile_support import digest, otp_debug
from app.team_integrations.sms import get_sms_provider, TwilioVerifyProvider


def start_challenge(db, phone, purpose, code):
    provider = get_sms_provider(otp_debug())
    if isinstance(provider, TwilioVerifyProvider):
        # Verify reuses a pending code for the same recipient. Cancel only when
        # switching purpose so reset and change-password cannot share a code.
        previous = db.execute(text("""SELECT purpose,code_hash FROM otp_challenges
            WHERE phone=:p AND consumed_at IS NULL AND code_hash LIKE 'verify:%'
            ORDER BY created_at DESC"""), {'p': phone}).mappings().all()
        canceled = set()
        for row in previous:
            sid = row['code_hash'].strip()[7:]
            if row['purpose'] != purpose and sid not in canceled:
                provider.cancel(sid)
                canceled.add(sid)
        return 'verify:' + provider.start(phone)
    provider.send_sms(phone, f'VirtuFitAI: ma xac nhan {code}. Het han sau 5 phut.')
    return digest(code)


def check_challenge(stored, code, phone):
    import secrets
    provider = get_sms_provider(otp_debug())
    stored = stored.strip()
    if isinstance(provider, TwilioVerifyProvider):
        return stored.startswith('verify:') and provider.check(stored[7:], code, phone)
    # Old provider challenges cannot be accepted after switching providers.
    return not stored.startswith('verify:') and secrets.compare_digest(stored, digest(code))
