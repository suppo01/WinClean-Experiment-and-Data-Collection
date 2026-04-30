import subprocess
import os
import csv


# Hardcoded path to WinClean
WINCCLEAN_MAIN = r"C:\Users\molly\github\WinClean-Experiment-and-Data-Collection\src\src\main.py"

def run_winclean(path, mode="static"):
    WINCCLEAN_MAIN = r"C:\Users\molly\github\WinClean-Experiment-and-Data-Collection\src\src\main.py"
    WINCCLEAN_DIR = os.path.dirname(WINCCLEAN_MAIN)
    
    cmd = ["python", WINCCLEAN_MAIN, "--mode", mode, "--path-command", path]
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Working directory: {WINCCLEAN_DIR}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        stdin=subprocess.DEVNULL,
        cwd=WINCCLEAN_DIR
    )
    
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    
    lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
    return lines[-1] if lines else None




def run_path_command_in_venv(command, venv_path="winclean_venv"):
    """Run a path command in a venv."""
    if command is None:
        return {"stdout": "", "stderr": "No command provided", "returncode": 1}
    
    # Create venv if needed
    if not os.path.exists(venv_path):
        subprocess.run(["python", "-m", "venv", venv_path], check=True)
    
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
    
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }


def winclean_recursive(path, pass_counter=0):
    """Recursively fix path bugs until resolved."""
    pass_counter += 1
    
    # Run the input through WinClean
    winclean_output = run_winclean(path)
    
    # Check if WinClean returned a fix
    if winclean_output is None:
        print(f"Attempt {pass_counter}: WinClean failed or timed out")
        return {"original": path, "fix": None, "passes": pass_counter, "status": "failed"}

    # Run the result from WinClean in a Venv and collect any errors
    venv_result = run_path_command_in_venv(winclean_output)
    
    # Check for errors
    if venv_result["returncode"] == 0:
        print(f"Here is the solution offered by WinClean:\n\n{winclean_output}")
        plural = "es" if pass_counter > 1 else ""
        print(f"The input was cleaned in {pass_counter} pass{plural}")
        return {"original": path, "fix": winclean_output, "passes": pass_counter, "status": "success"}
    else:
        print(f"Attempt {pass_counter} failed with errors: {venv_result['stderr']}")
        return {"original": path, "fix": winclean_output, "passes": pass_counter, "status": "failed"}


def main():
    """Runner for experiments regarding the performance of WinClean"""
    # Read in the input into a list
    with open("input.txt", "r", encoding="utf-8") as f:
        paths = [line.strip() for line in f if line.strip()]
    
    results = []
    
    # Loop through the inputs
    for path in paths:
        result = winclean_recursive(path)
        results.append(result)
        print()  # Blank line between paths
    
    # Write to CSV
    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["original", "fix", "passes", "status"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Results saved to output.csv")

if __name__ == "__main__":
    main()
