# Makefile
# =======================================
# Agentic Prompt Workflow Automation
# =======================================

# Default: run a single prompt template
run:
	python run_template_batch.py --file $(FILE)

# Run the full agent loop on all predefined prompts
all:
	python run_template_batch.py --all

# Clean all generated logs (except .gitkeep)
clean:
	rm -f logs/*/*.json

# Format Python code using Black
format:
	black .

# Lint project code using Ruff
lint:
	ruff .

# Check if .env is present and valid
check-env:
	@if [ -f .env ]; then echo ".env found ✔"; else echo "⚠️ .env not found"; fi

# Help: list available commands
help:
	@echo "Available make commands:"
	@echo "  make run FILE=path    # Run a single prompt"
	@echo "  make all             # Run all prompts"
	@echo "  make clean           # Delete all logs"
	@echo "  make format          # Run Black code formatter"
	@echo "  make lint            # Run Ruff code linter"
	@echo "  make check-env       # Check for .env file"
	@echo "  make help            # Show this message"
