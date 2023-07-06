@echo off

echo "Installing packages..."

pip install -r requirments.txt

echo "Building Measure Loader..."
echo "Compiling Python files..."

python -m PyInstaller --additional-hooks-dir . --onefile --noconsole main.py

echo "Build completed."