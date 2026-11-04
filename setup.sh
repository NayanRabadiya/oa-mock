#!/usr/bin/env bash
# OA Mock setup for macOS and Linux.
#   ./setup.sh             install what's missing (Python 3, C++ compiler, Java JDK), then start the mock
#   ./setup.sh --no-java   skip the JDK
#   ./setup.sh --no-start  set up only, don't start the runner
set -u
cd "$(dirname "$0")"

WANT_JAVA=1; START=1
for a in "$@"; do
  case "$a" in
    --no-java) WANT_JAVA=0 ;;
    --no-start) START=0 ;;
    -h|--help) sed -n '2,5p' "$0"; exit 0 ;;
    *) echo "Unknown option: $a"; exit 2 ;;
  esac
done

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; }
step() { printf '\n\033[1m%s\033[0m\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

OS="$(uname -s)"
SUDO=""; [ "$(id -u)" -ne 0 ] && have sudo && SUDO="sudo"

PM=""
if [ "$OS" = "Darwin" ]; then PM="brew"
elif have apt-get; then PM="apt"
elif have dnf; then PM="dnf"
elif have yum; then PM="yum"
elif have pacman; then PM="pacman"
elif have zypper; then PM="zypper"
elif have apk; then PM="apk"
fi

pkg_install() {   # pkg_install <apt> <dnf/yum> <pacman> <zypper> <apk> <brew>
  case "$PM" in
    apt)    $SUDO apt-get update -y >/dev/null && $SUDO apt-get install -y $1 ;;
    dnf)    $SUDO dnf install -y $2 ;;
    yum)    $SUDO yum install -y $2 ;;
    pacman) $SUDO pacman -S --needed --noconfirm $3 ;;
    zypper) $SUDO zypper install -y $4 ;;
    apk)    $SUDO apk add $5 ;;
    brew)   if have brew; then brew install $6; else return 1; fi ;;
    *)      return 1 ;;
  esac
}

python_ok() { "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; }

echo "OA Mock setup ($OS)"

# ---------- Python ----------
step "1/3 Python 3.8+"
PY=""
for c in python3 python; do have "$c" && python_ok "$c" && { PY="$c"; break; }; done
if [ -z "$PY" ]; then
  warn "Python 3.8+ not found. Installing..."
  if [ "$OS" = "Darwin" ] && ! have brew; then
    warn "Install Python from https://www.python.org/downloads/macos/ (or install Homebrew from https://brew.sh), then run this script again."
    exit 1
  fi
  pkg_install python3 python3 python python3 python3 python || { warn "Couldn't install Python automatically. Install Python 3.8+ and run this again."; exit 1; }
  for c in python3 python; do have "$c" && python_ok "$c" && { PY="$c"; break; }; done
  [ -z "$PY" ] && { warn "Python still not found on PATH. Open a new terminal and run this again."; exit 1; }
fi
ok "$($PY --version 2>&1) ($(command -v $PY))"

# ---------- C++ ----------
step "2/3 C++ compiler (for C++17 answers)"
CXX=""
for c in g++ clang++; do
  if have "$c" && "$c" --version >/dev/null 2>&1; then CXX="$c"; break; fi
done
if [ -n "$CXX" ]; then
  ok "$("$CXX" --version 2>/dev/null | head -1)"
elif [ "$OS" = "Darwin" ]; then
  warn "No compiler yet. Opening the Apple Command Line Tools installer..."
  xcode-select --install 2>/dev/null || true
  warn "Finish the installer window, then run ./setup.sh again. (Apple clang works: the runner supplies <bits/stdc++.h>.)"
else
  warn "Installing g++..."
  if pkg_install g++ gcc-c++ gcc gcc-c++ g++ gcc && have g++; then ok "$(g++ --version | head -1)"
  else warn "Couldn't install g++. Install it with your package manager. Python and JavaScript answers still work."; fi
fi

# ---------- Java ----------
step "3/3 Java JDK (for Java answers)"
java_ok() {
  have javac || return 1
  javac -version >/dev/null 2>&1   # on macOS, /usr/bin/javac is a stub until a JDK is installed
}
if java_ok; then
  ok "$(javac -version 2>&1 | tail -1)"
elif [ "$WANT_JAVA" = 0 ]; then
  warn "Skipped (--no-java). C++, Python and JavaScript still work."
else
  warn "No JDK found. Installing..."
  if [ "$OS" = "Darwin" ]; then
    if have brew; then
      brew install openjdk && {
        JH="$(brew --prefix openjdk)"
        if [ -d /Library/Java/JavaVirtualMachines ] && [ ! -e /Library/Java/JavaVirtualMachines/openjdk.jdk ]; then
          sudo ln -sfn "$JH/libexec/openjdk.jdk" /Library/Java/JavaVirtualMachines/openjdk.jdk 2>/dev/null || true
        fi
        export PATH="$JH/bin:$PATH"
      }
    else
      warn "Install a JDK from https://adoptium.net (or install Homebrew from https://brew.sh and run this again)."
    fi
  else
    pkg_install default-jdk-headless java-21-openjdk-devel jdk-openjdk java-21-openjdk-devel openjdk21 openjdk || true
  fi
  if java_ok; then ok "$(javac -version 2>&1 | tail -1)"; else warn "No JDK. Java answers won't run; everything else does."; fi
fi

# ---------- launcher ----------
cat > start.sh <<'EOF'
#!/usr/bin/env bash
# Start the OA mock. Stop it with Ctrl+C (Ctrl+Z only pauses it and keeps the port busy).
cd "$(dirname "$0")"
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && exec "$c" run.py "$@"; done
echo "Python 3 not found. Run ./setup.sh first."; exit 1
EOF
chmod +x start.sh
step "Done"
ok "Start the mock any time with ./start.sh (stop it with Ctrl+C)."

if [ "$START" = 1 ]; then
  echo
  exec "$PY" run.py
fi
