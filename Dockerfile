# Small, explicit base image. "slim" = Debian without the extra weight.
FROM python:3.12-slim

WORKDIR /app

# --- Layer caching trick ---
# Copy ONLY the dependency file first, install, THEN copy the source.
# Docker caches each step. If you change source code but not dependencies,
# Docker reuses the (slow) install layer and only redoes the (fast) copy.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# Now copy the actual code. Changing this line does NOT re-run pip install above.
COPY src ./src
RUN pip install --no-cache-dir .

# matplotlib "Agg" backend needs no display, so this runs fine with no GUI.
ENTRYPOINT ["attention-sim"]