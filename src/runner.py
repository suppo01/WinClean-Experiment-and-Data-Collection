import subprocess

def run_winclean(path, mode="static"):
    """Run WinClean CLI on a path command."""
    cmd = [
        "winclean",
        "--mode", mode,
        "--path-command", path
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Extract the last non-empty line as the fix
    lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
    fix = lines[-1] if lines else None
    return fix

def run_path_command_in_venv(command, venv_path="winclean_venv"):
    """Run a path command (like cd, dir) in a venv."""
    
    # Create venv if needed
    if not os.path.exists(venv_path):
        subprocess.run(["python", "-m", "venv", venv_path], check=True)
    
    # Use cmd to run the command
    if os.name == "nt":
        cmd_path = os.path.join(venv_path, "Scripts", "cmd.exe")
        result = subprocess.run(
            [cmd_path, "/c", command],
            capture_output=True,
            text=True
        )
    else:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
    
    errors = result.stderr if result.stderr else None
    return {
        "stderr": result.stderr,
        "errors": errors
    }

def winclean_recursive(path, pass_counter=0):
    """Recursively fix path bugs until resolved."""
    pass_counter += 1
    
    # Run the input through WinClean
    winclean_output = run_winclean(path)

    # Run the result from WinClean in a Venv and collect any errors
    venv_errors = run_path_command_in_venv(winclean_output)
    
    # Check for the number of errors
    if venv_errors is None:
        # Success - print output
        print(f"Here is the solution offered by WinClean:\n\n{winclean_output}")
        plural = "es" if pass_counter > 1 else ""
        print(f"The input was cleaned in {pass_counter} pass{plural}")
        
        # Write to CSV
        with open("output.csv", "w", newline="", encoding="utf-8") as f:
          writer = csv.DictWriter(f, fieldnames=["fix", "passes", "errors"])
          writer.writeheader()
          writer.writerows(winclean_output, pass_counter, venv_errors)
        return pass_counter, data_to_csv
    else:
        # Try again recursively
        print(f"Attempt {pass_counter} failed. Trying again...")
        return winclean_recursive(winclean_output, pass_counter)


def main():
    """Runner for experiments regarding the performance of WinClean"""
    pass_counter = 0
    
    # Read in the input into a list
    with open("input.txt", "r", encoding="utf-8") as f:
        paths = [line.strip() for line in f if line.strip()]
    
    # Loop through the inputs
    for path in paths:
        winclean_recursive(path)
