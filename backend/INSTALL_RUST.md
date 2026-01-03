# Installing Rust for tiktoken

The `tiktoken` package requires Rust to build. Here are quick installation options:

## Option 1: Install Rust via rustup (Recommended)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

## Option 2: Install Rust via Homebrew

```bash
brew install rust
```

## Option 3: Skip tiktoken (if not critical)

If you don't need tiktoken immediately, you can install dependencies without it:

```bash
cd backend
poetry remove tiktoken  # This will update dependencies
poetry install
```

However, tiktoken is used by OpenAI SDK for token counting, so it's recommended to install Rust.

## After Installing Rust

Once Rust is installed, run:

```bash
cd backend
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1  # Required for Python 3.13
poetry install --no-root
```

**Note for Python 3.13 users**: You need to set `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` because `tiktoken` uses PyO3 which doesn't officially support Python 3.13 yet. This flag enables forward compatibility using the stable ABI.

This should now succeed!

