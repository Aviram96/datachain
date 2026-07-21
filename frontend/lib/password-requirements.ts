/** Matches backend ``UserRegister`` password rules in ``app/schemas/auth.py``. */

export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_MAX_LENGTH = 200;
export const PASSWORD_MAX_UTF8_BYTES = 72;

export const PASSWORD_REQUIREMENTS_HINT =
  "At least 8 characters, at most 200 characters, and at most 72 bytes (UTF-8).";

/**
 * Returns a user-facing error message when the password fails requirements,
 * or null when it is valid for registration.
 */
export function passwordRequirementsError(password: string): string | null {
  if (password.length < PASSWORD_MIN_LENGTH) {
    return "Password must be at least 8 characters.";
  }
  if (password.length > PASSWORD_MAX_LENGTH) {
    return "Password must be at most 200 characters.";
  }
  if (new TextEncoder().encode(password).length > PASSWORD_MAX_UTF8_BYTES) {
    return "Password must be at most 72 bytes (UTF-8).";
  }
  return null;
}
