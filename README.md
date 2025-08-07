# ⚠️⚠️⚠️ Deprecation notice ⚠️⚠️⚠️ 

The `gotrue` package name is deprecated and is not going to receive any more updates. Please, use `supabase_auth` instead.

## How to switch

1. Use `uv add supabase_auth` instead of `uv add gotrue`.
2. Replace `gotrue` with `supabase_auth` in your `requirements.txt`, `pyproject.toml`, `setup.py`, etc.
3. Replace all imports `from gotrue import ...` to `from supabase_auth import ...`
4. If `gotrue` is still used by one of your dependencies, consider reporting it in their issue tracker.

## Reasoning

The `gotrue` package has been replaced by the `supabase_auth` since December 14th, 2024, following the JavaScript implementation name switch. Changes and fixes were maintained for a couple of months by pushing them in both packages at the same time, using a patching script. In order to simplify maintenance and improve the CI, this package is going to cease receiving updates as of 7 of August 2025, and going forward everyone should use `supabase_auth` instead.
