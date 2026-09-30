export function formatClock(
  minutes = 0
) {
  const value = Math.max(
    0,
    Math.floor(minutes)
  );

  const hours =
    Math.floor(value / 60) % 24;

  const mins =
    value % 60;

  return `${String(hours).padStart(
    2,
    "0"
  )}:${String(mins).padStart(2, "0")}`;
}