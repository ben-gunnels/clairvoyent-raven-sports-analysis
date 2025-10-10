import subprocess
import os

def run_R_file(file:str):
    # Run an R file from Python
    subprocess.run(["Rscript", file])

if __name__ == "__main__":
    file = r"C:\Users\bengu\Documents\Sports Analysis Project\clairvoyent-raven-sports-analysis\src\data_api\R\nflReadr.r"
    if os.path.exists(file):
        print("File exists")
    else:
        print("File not found")
    run_R_file(file)