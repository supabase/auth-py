# ⚠️⚠️⚠️ Deprecation notice ⚠️⚠️⚠️ 

The `gotrue` package name is deprecated and is not going to receive any more updates. Please, use `supabase_auth` instead.

## How to switch

1. Use `uv add supabase_auth` instead of `uv add gotrue`.
2. Replace `gotrue` with `supabase_auth` in your `requirements.txt`, `pyproject.toml`, `setup.py`, etc.
3. Replace all imports `from gotrue import ...` to `from supabase_auth import ...`
4. If `gotrue` is still used by one of your dependencies, consider reporting it in their issue tracker.
