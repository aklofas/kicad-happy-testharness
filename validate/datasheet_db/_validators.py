"""Schema invariant checks for manifest records. Private to the package.

Each public checker returns a list of human-readable violation strings.
An empty list means the record is valid. Callers should raise on non-empty
results — invariant violations are programming errors, not data-quality
issues."""
